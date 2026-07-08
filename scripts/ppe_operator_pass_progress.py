"""Operator pass progress — what changed, wait health, no-progress streak.

Canon: operator thread reply contract (ppe-operator-core.mdc).
Waiting is never progress; in-flight work needs evidence + elapsed vs budget.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.workflow_metrics_cli import (  # noqa: E402
    SLICES_FILE,
    _append_jsonl,
    _metrics_dir,
    _parse_iso,
    _read_jsonl,
    _utc_now,
)

OPERATOR_PASSES_FILE = "operator_passes.jsonl"
EVIDENCE_STATE_REL = "artifacts/control_plane/OPERATOR_PASS_EVIDENCE.json"
LATEST_REL = "artifacts/control_plane/OPERATOR_PASS_LATEST.json"

PHASE_BUDGET_SECONDS: dict[str, int] = {
    "BUILD_IN_FLIGHT": 2 * 3600,
    "FINISH_IN_FLIGHT": 3600,
    "RUN_LOCAL_PENDING": 4 * 3600,
    "CLOSEOUT_PENDING": 4 * 3600,
}
DESKTOP_RUN_LOCAL_BUDGET_SECONDS = 2 * 3600
BUILD_LOCK_BUDGET_SECONDS = 2 * 3600
RELAY_ACTIVE_BUDGET_SECONDS = 3 * 3600
CI_AUTOMERGE_BUDGET_SECONDS = 2 * 3600
EVIDENCE_RECENT_SECONDS = 900
PASS_DEDUPE_SECONDS = 120
STREAK_WINDOW = 10
FOUNDER_ALERT_STATE_REL = "artifacts/control_plane/OPERATOR_PASS_ALERT_STATE.json"
ALERT_STREAK_THRESHOLD = 4
RADAR_STREAK_THRESHOLD = 7

WaitHealth = Literal["moving", "quiet", "stuck", "deadlock", "unknown", "none"]
ProgressClass = Literal["high", "medium", "low", "none"]


def _parse_utc(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _elapsed_seconds(since: datetime | None) -> float | None:
    if since is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - since).total_seconds())


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_operator_passes(repo: Path) -> list[dict[str, Any]]:
    return _read_jsonl(_metrics_dir(repo) / OPERATOR_PASSES_FILE)


def latest_operator_pass(repo: Path) -> dict[str, Any] | None:
    rows = read_operator_passes(repo)
    return rows[-1] if rows else None


def _passes_path(repo: Path) -> Path:
    return _metrics_dir(repo) / OPERATOR_PASSES_FILE


def _file_fingerprint(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False}
    try:
        st = path.stat()
        return {"exists": True, "size": st.st_size, "mtime": int(st.st_mtime)}
    except OSError:
        return {"exists": False}


def _git_head(repo: Path) -> str:
    import subprocess

    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _median_slice_duration_seconds(repo: Path, *, kind: str) -> int | None:
    """Historical median wall-clock from slices.jsonl (v3 adaptive budgets)."""
    durations: list[float] = []
    for row in _read_jsonl(_metrics_dir(repo) / SLICES_FILE):
        sid = str(row.get("slice_id") or "")
        if kind == "closeout" and "Closeout" not in sid and "Witness" not in sid:
            continue
        if kind == "product" and "Product" not in sid:
            continue
        t0 = _parse_iso(str(row.get("started_at") or ""))
        t1 = _parse_iso(str(row.get("completed_at") or ""))
        if t0 and t1 and t1 > t0:
            durations.append((t1 - t0).total_seconds())
    if len(durations) < 2:
        return None
    durations.sort()
    mid = len(durations) // 2
    return int(durations[mid])


def _budget_for_phase(repo: Path, phase: str) -> int:
    base = PHASE_BUDGET_SECONDS.get(phase, 3600)
    if phase == "FINISH_IN_FLIGHT":
        med = _median_slice_duration_seconds(repo, kind="closeout")
        if med is not None:
            return max(base, int(med * 1.25))
    if phase == "BUILD_IN_FLIGHT":
        med = _median_slice_duration_seconds(repo, kind="product")
        if med is not None:
            return max(base, int(med * 1.25))
    return base


def _relay_run_context(repo: Path) -> dict[str, Any]:
    """Newest relay run slice + events.log activity (v2)."""
    ctx: dict[str, Any] = {"slice_id": "", "run_id": "", "events_mtime": 0, "events_size": 0}
    try:
        from scripts.ppe_active_run import load_active_run

        active = load_active_run(repo)
        if active:
            ctx["slice_id"] = str(active.get("slice_id") or "")
            ctx["since_at"] = str(active.get("ts_utc") or "")
    except Exception:
        pass
    runs_root = repo / "artifacts" / "relay" / "runs"
    if not runs_root.is_dir():
        wt = repo / "_worktrees" / "orchestrator"
        if wt.is_dir():
            for child in wt.iterdir():
                alt = child / "artifacts" / "relay" / "runs"
                if alt.is_dir():
                    runs_root = alt
                    break
    if runs_root.is_dir():
        best_mtime = 0.0
        best_run = ""
        for run_dir in runs_root.iterdir():
            if not run_dir.is_dir():
                continue
            events = run_dir / "events.log"
            if events.is_file():
                mt = events.stat().st_mtime
                if mt > best_mtime:
                    best_mtime = mt
                    best_run = run_dir.name
                    ctx["events_mtime"] = int(mt)
                    ctx["events_size"] = events.stat().st_size
        ctx["run_id"] = best_run
    return ctx


def _open_pr_wait_context(repo: Path) -> dict[str, Any] | None:
    """Open PR with pending checks — CI/automerge wait (v2)."""
    import subprocess

    try:
        proc = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--head",
                _git_branch(repo),
                "--state",
                "open",
                "--json",
                "number,title,statusCheckRollup,mergeable,url",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list) or not rows:
        return None
    row = rows[0] if isinstance(rows[0], dict) else None
    if not row:
        return None
    checks = row.get("statusCheckRollup") or []
    pending = sum(
        1
        for c in checks
        if isinstance(c, dict) and str(c.get("state") or "").upper() in ("PENDING", "IN_PROGRESS", "QUEUED")
    )
    return {
        "number": row.get("number"),
        "title": row.get("title"),
        "url": row.get("url"),
        "pending_checks": pending,
        "mergeable": row.get("mergeable"),
    }


def _git_branch(repo: Path) -> str:
    import subprocess

    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def collect_evidence_fingerprint(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    fp: dict[str, Any] = {
        "as_of": _utc_now(),
        "git_head": _git_head(repo),
        "post_build_log": _file_fingerprint(repo / "artifacts/orchestrator/POST_BUILD_FINISH.log"),
        "build_worker_events_tail": "",
        "vm_phase": "",
        "vm_phase_as_of": "",
        "manifest_status": "",
        "active_run_ts": "",
    }
    bwe = repo / "artifacts/orchestrator/build_worker_events.jsonl"
    if bwe.is_file():
        try:
            lines = [ln.strip() for ln in bwe.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
            fp["build_worker_events_tail"] = lines[-1][:240] if lines else ""
        except OSError:
            pass
    mirror = _load_json(repo / "docs/SOP/VM_OPERATOR_PHASE.json")
    fp["vm_phase"] = str(mirror.get("phase") or "")
    fp["vm_phase_as_of"] = str(mirror.get("as_of") or "")
    try:
        from scripts.ppe_manifest import load_manifest

        fp["manifest_status"] = str(load_manifest(repo).get("status") or "")
    except Exception:
        pass
    active = _load_json(repo / "artifacts/orchestrator/ACTIVE_RUN.json")
    fp["active_run_ts"] = str(active.get("ts_utc") or active.get("started_at") or "")
    fp["active_run_slice_id"] = str(active.get("slice_id") or "")
    relay = _relay_run_context(repo)
    fp["relay_run_id"] = str(relay.get("run_id") or "")
    fp["relay_events_mtime"] = relay.get("events_mtime") or 0
    fp["relay_events_size"] = relay.get("events_size") or 0
    return fp


def _evidence_moved_since(prior: dict[str, Any], current: dict[str, Any]) -> tuple[bool, list[str]]:
    if not prior:
        return False, []
    signals: list[str] = []
    if prior.get("git_head") != current.get("git_head") and current.get("git_head"):
        signals.append("git_head")
    pl = prior.get("post_build_log") if isinstance(prior.get("post_build_log"), dict) else {}
    cl = current.get("post_build_log") if isinstance(current.get("post_build_log"), dict) else {}
    if cl.get("exists") and (pl.get("mtime") != cl.get("mtime") or pl.get("size") != cl.get("size")):
        signals.append("post_build_log")
    if prior.get("build_worker_events_tail") != current.get("build_worker_events_tail") and current.get(
        "build_worker_events_tail"
    ):
        signals.append("build_worker_event")
    if prior.get("vm_phase") != current.get("vm_phase") and current.get("vm_phase"):
        signals.append("vm_phase")
    if prior.get("manifest_status") != current.get("manifest_status") and current.get("manifest_status"):
        signals.append("manifest")
    if prior.get("active_run_ts") != current.get("active_run_ts") and current.get("active_run_ts"):
        signals.append("active_run")
    if prior.get("relay_events_mtime") != current.get("relay_events_mtime") and current.get("relay_events_mtime"):
        signals.append("relay_events")
    if prior.get("relay_events_size") != current.get("relay_events_size") and current.get("relay_events_size"):
        if "relay_events" not in signals:
            signals.append("relay_events")
    return bool(signals), signals


def _recent_evidence(signals: list[str], prior_at: str | None) -> bool:
    if not signals:
        return False
    dt = _parse_utc(prior_at)
    if dt is None:
        return True
    return (_elapsed_seconds(dt) or 9999) <= EVIDENCE_RECENT_SECONDS


def _remaining_count(status: dict[str, Any]) -> int:
    burst = status.get("burst_plan") if isinstance(status.get("burst_plan"), dict) else {}
    if burst.get("remaining_count") is not None:
        return int(burst.get("remaining_count") or 0)
    pending = burst.get("pending_slices")
    if isinstance(pending, list):
        return len(pending)
    return 0


def _status_fingerprint(status: dict[str, Any], wait: dict[str, Any] | None) -> str:
    verdict = str(status.get("verdict") or "")
    blocker = str(status.get("blocker") or "")[:120]
    phase = str((wait or {}).get("phase") or "")
    remaining = _remaining_count(status)
    plan = str(status.get("phase_plan_path") or "")
    return f"{verdict}|{blocker}|{phase}|{remaining}|{plan}"


def assess_wait_program(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    """Primary wait program — what we are waiting for (waiting is not progress)."""
    repo = repo.resolve()
    verdict = str(status.get("verdict") or "")

    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    vm_phase = str(vm_trust.get("vm_phase") or "").strip()
    if not vm_phase:
        mirror = _load_json(repo / "docs/SOP/VM_OPERATOR_PHASE.json")
        vm_phase = str(mirror.get("phase") or "").strip()

    in_flight = frozenset({"BUILD_IN_FLIGHT", "FINISH_IN_FLIGHT"})
    if vm_trust.get("wait_for_vm") or vm_phase in in_flight:
        chapter = str(status.get("chapter_name") or status.get("phase_plan_path") or "relay").strip()
        since_state = _load_json(repo / "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json")
        since_at = str(since_state.get("since") or "")
        if str(since_state.get("phase") or "") != vm_phase:
            since_at = str(_load_json(repo / "docs/SOP/VM_OPERATOR_PHASE.json").get("as_of") or "")
        budget = _budget_for_phase(repo, vm_phase)
        action = "run_ppe_local / relay finish" if vm_phase == "FINISH_IN_FLIGHT" else "product BUILD on VM"
        slice_hint = ""
        relay = _relay_run_context(repo)
        if relay.get("slice_id"):
            slice_hint = f" slice `{relay['slice_id']}`"
        elif relay.get("run_id"):
            slice_hint = f" run `{relay['run_id']}`"
        return {
            "kind": "vm_in_flight",
            "phase": vm_phase,
            "slice_id": relay.get("slice_id") or None,
            "waiting_for": f"VM `{vm_phase}` — {action}{slice_hint} ({chapter})",
            "expected_seconds": budget,
            "since_at": since_at or str(relay.get("since_at") or ""),
        }

    if verdict == "RUN_LOCAL":
        chapter = str(status.get("chapter_name") or "chapter closeout").strip()
        return {
            "kind": "desktop_run_local",
            "phase": "RUN_LOCAL_PENDING",
            "waiting_for": f"Desktop/VM finish — `{chapter}` (DESKTOP_CONTINUE / finish_ide_build)",
            "expected_seconds": DESKTOP_RUN_LOCAL_BUDGET_SECONDS,
            "since_at": "",
        }

    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        lock = read_build_lock(repo)
        if lock:
            sid = str(lock.get("slice_id") or "?")
            return {
                "kind": "build_lock",
                "phase": "BUILD_IN_FLIGHT",
                "waiting_for": f"Desktop BUILD worker — slice `{sid}`",
                "expected_seconds": BUILD_LOCK_BUDGET_SECONDS,
                "since_at": str(lock.get("started_at") or lock.get("ts") or ""),
            }
    except Exception:
        pass

    lease = status.get("worker_lease") if isinstance(status.get("worker_lease"), dict) else {}
    if lease.get("active"):
        wid = str((lease.get("lease") or {}).get("worker_id") or lease.get("suggested_lane") or "worker")
        return {
            "kind": "worker_lease",
            "phase": "BUILD_IN_FLIGHT",
            "waiting_for": f"Active worker lease — `{wid}`",
            "expected_seconds": BUILD_LOCK_BUDGET_SECONDS,
            "since_at": str((lease.get("lease") or {}).get("acquired_at") or ""),
        }

    try:
        from scripts.ppe_active_run import load_active_run

        active = load_active_run(repo)
        if active:
            sid = str(active.get("slice_id") or active.get("kind") or "relay")
            relay = _relay_run_context(repo)
            return {
                "kind": "relay_active",
                "phase": "CLOSEOUT_PENDING",
                "slice_id": sid,
                "waiting_for": f"Relay in flight — `{sid}`"
                + (f" (run `{relay['run_id']}`)" if relay.get("run_id") else ""),
                "expected_seconds": _budget_for_phase(repo, "CLOSEOUT_PENDING"),
                "since_at": str(active.get("ts_utc") or ""),
            }
    except Exception:
        pass

    manifest = str(status.get("manifest_status") or "").upper()
    if manifest == "RUNNING":
        return {
            "kind": "manifest_running",
            "phase": "CLOSEOUT_PENDING",
            "waiting_for": "Manifest RUNNING — relay slice in progress",
            "expected_seconds": RELAY_ACTIVE_BUDGET_SECONDS,
            "since_at": "",
        }

    coord = status.get("coordination_check") if isinstance(status.get("coordination_check"), dict) else {}
    if coord.get("blocks_burst") or coord.get("blocks_build"):
        return {
            "kind": "coordination_blocked",
            "phase": "BLOCKED",
            "waiting_for": f"Coordination blocked — `{coord.get('verdict') or 'repair'}`",
            "expected_seconds": 0,
            "since_at": "",
            "deadlock_hint": True,
        }

    pr = _open_pr_wait_context(repo)
    if pr and int(pr.get("pending_checks") or 0) > 0:
        num = pr.get("number")
        title = str(pr.get("title") or "")[:60]
        return {
            "kind": "ci_automerge",
            "phase": "CI_PENDING",
            "waiting_for": f"PR #{num} checks — {title}",
            "expected_seconds": CI_AUTOMERGE_BUDGET_SECONDS,
            "since_at": "",
            "pr_url": pr.get("url"),
        }

    return None


def classify_wait_health(
    repo: Path,
    wait: dict[str, Any] | None,
    *,
    evidence: dict[str, Any],
    prior_evidence: dict[str, Any],
    status: dict[str, Any],
) -> tuple[WaitHealth, list[str]]:
    if wait is None:
        return "none", []

    if wait.get("deadlock_hint"):
        return "deadlock", []

    mirror_health = status.get("vm_mirror_health") if isinstance(status.get("vm_mirror_health"), dict) else {}
    if wait.get("kind") == "vm_in_flight" and mirror_health.get("stale"):
        moved, signals = _evidence_moved_since(prior_evidence, evidence)
        if not moved:
            return "unknown", ["mirror_stale"]

    since_at = str(wait.get("since_at") or "")
    elapsed = _elapsed_seconds(_parse_utc(since_at))
    if elapsed is None and wait.get("kind") == "vm_in_flight":
        monitor = _load_json(repo / "artifacts/control_plane/IN_FLIGHT_MONITOR_STATE.json")
        elapsed = _elapsed_seconds(_parse_utc(str(monitor.get("watch_started_at") or "")))

    budget = int(wait.get("expected_seconds") or 3600)
    moved, signals = _evidence_moved_since(prior_evidence, evidence)
    recent = _recent_evidence(signals, str(prior_evidence.get("as_of") or ""))

    if wait.get("kind") == "build_lock":
        try:
            from scripts.ppe_remote_build_agent import is_build_lock_stale

            raw = _load_json(repo / "artifacts/orchestrator/REMOTE_BUILD_LOCK.json")
            if raw and is_build_lock_stale(repo, raw):
                return "deadlock", ["stale_build_lock"]
        except Exception:
            pass

    if elapsed is not None and elapsed > budget:
        return "stuck", signals

    if moved and recent:
        return "moving", signals
    if elapsed is not None and elapsed > budget * 0.75:
        return "quiet", signals
    if elapsed is not None and elapsed > 600 and not moved:
        return "quiet", signals
    if moved:
        return "moving", signals
    return "quiet", signals


def _slices_since(repo: Path, since: datetime | None) -> list[dict[str, Any]]:
    if since is None:
        return []
    cutoff = since.timestamp()
    out: list[dict[str, Any]] = []
    for row in _read_jsonl(_metrics_dir(repo) / SLICES_FILE):
        dt = _parse_iso(str(row.get("completed_at") or ""))
        if dt and dt.timestamp() >= cutoff:
            out.append(row)
    return out


def _verdict_advanced(prior: dict[str, Any] | None, status: dict[str, Any]) -> bool:
    if not prior:
        return False
    order = {
        "ERROR": 0,
        "FIX_PLAN": 1,
        "STALE_STATE": 1,
        "SUPPLY_LOW": 2,
        "IDE_BUILD": 3,
        "RUN_LOCAL": 4,
        "RUN_AUTO": 5,
    }
    pv = str(prior.get("verdict") or "")
    cv = str(status.get("verdict") or "")
    return order.get(cv, 0) > order.get(pv, 0)


def assess_pass_progress(
    repo: Path,
    status: dict[str, Any],
    *,
    prior_pass: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    if prior_pass is None:
        prior_pass = latest_operator_pass(repo)

    prior_evidence = _load_json(repo / EVIDENCE_STATE_REL)
    evidence = collect_evidence_fingerprint(repo)
    wait = assess_wait_program(repo, status)
    wait_health, evidence_signals = classify_wait_health(
        repo, wait, evidence=evidence, prior_evidence=prior_evidence, status=status
    )

    prior_at = _parse_utc(str(prior_pass.get("pass_at") or "")) if prior_pass else None
    new_slices = _slices_since(repo, prior_at)
    slice_ids = [str(s.get("slice_id") or "") for s in new_slices if s.get("slice_id")]

    progress_bits: list[str] = []
    progress_class: ProgressClass = "none"

    if slice_ids:
        progress_class = "high"
        progress_bits.append(f"closed {', '.join(slice_ids[-3:])}")
    elif _verdict_advanced(prior_pass, status):
        progress_class = "medium"
        progress_bits.append(f"verdict → `{status.get('verdict')}`")
    elif prior_pass and str(prior_pass.get("blocker") or "") != str(status.get("blocker") or ""):
        if str(status.get("blocker") or "").strip():
            progress_class = "medium"
            progress_bits.append("blocker changed")
    elif prior_pass and int(prior_pass.get("remaining_count") or -1) > _remaining_count(status) >= 0:
        progress_class = "medium"
        progress_bits.append(f"remaining slices {_remaining_count(status)}")

    manifest = str(status.get("manifest_status") or "").upper()
    if prior_pass and str(prior_pass.get("manifest_status") or "").upper() != manifest and manifest == "COMPLETE":
        progress_class = "high"
        progress_bits.append("chapter manifest COMPLETE")

    if progress_class == "none" and wait and wait_health in ("moving", "quiet", "unknown"):
        active_kinds = {
            "vm_in_flight",
            "build_lock",
            "worker_lease",
            "relay_active",
            "manifest_running",
            "ci_automerge",
        }
        if wait.get("kind") in active_kinds:
            progress_class = "low"
            progress_bits.append(f"in flight — {wait.get('waiting_for', 'worker active')[:120]}")

    has_progress = progress_class in ("high", "medium")
    progress_summary = "none" if not progress_bits else " · ".join(progress_bits)

    fingerprint = _status_fingerprint(status, wait)
    prior_rows = read_operator_passes(repo)
    consecutive = 0
    if not has_progress:
        consecutive = int(prior_pass.get("consecutive_no_progress") or 0) + 1 if prior_pass else 1
    last_window = prior_rows[-(STREAK_WINDOW - 1) :] if prior_rows else []
    no_prog_window = sum(1 for r in last_window if not r.get("had_progress"))
    if not has_progress:
        no_prog_window += 1
    else:
        no_prog_window = 0

    elapsed_s = None
    expected_s = int((wait or {}).get("expected_seconds") or 0)
    if wait:
        elapsed_s = _elapsed_seconds(_parse_utc(str(wait.get("since_at") or "")))

    return {
        "pass_at": _utc_now(),
        "fingerprint": fingerprint,
        "verdict": status.get("verdict"),
        "blocker": status.get("blocker"),
        "chapter_id": status.get("chapter_name") or status.get("phase_plan_path"),
        "remaining_count": _remaining_count(status),
        "manifest_status": manifest,
        "had_progress": has_progress,
        "progress_class": progress_class,
        "progress_summary": progress_summary,
        "consecutive_no_progress": 0 if has_progress else consecutive,
        "no_progress_in_last_10": no_prog_window if not has_progress else 0,
        "wait": wait,
        "wait_health": wait_health,
        "wait_elapsed_s": elapsed_s,
        "wait_expected_s": expected_s,
        "evidence_signals": evidence_signals,
        "slices_closed_since_last": slice_ids,
    }


def _should_append_pass(repo: Path, outcome: dict[str, Any]) -> bool:
    prior = latest_operator_pass(repo)
    if not prior:
        return True
    if str(prior.get("fingerprint") or "") != str(outcome.get("fingerprint") or ""):
        return True
    prior_at = _parse_utc(str(prior.get("pass_at") or ""))
    elapsed = _elapsed_seconds(prior_at)
    if elapsed is not None and elapsed >= PASS_DEDUPE_SECONDS:
        return True
    if bool(prior.get("had_progress")) != bool(outcome.get("had_progress")):
        return True
    if str(prior.get("wait_health") or "") != str(outcome.get("wait_health") or ""):
        return True
    return False


def record_operator_pass(
    repo: Path,
    status: dict[str, Any],
    *,
    append: bool = True,
) -> dict[str, Any]:
    repo = repo.resolve()
    prior = latest_operator_pass(repo)
    outcome = assess_pass_progress(repo, status, prior_pass=prior)

    evidence = collect_evidence_fingerprint(repo)
    _save_json(repo / EVIDENCE_STATE_REL, evidence)

    if append and _should_append_pass(repo, outcome):
        row = {**outcome, "event": "operator_pass"}
        _append_jsonl(_passes_path(repo), row)
    elif not append:
        pass
    else:
        outcome["deduped"] = True

    _save_json(repo / LATEST_REL, outcome)
    return outcome


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    mins = int(seconds // 60)
    if mins < 90:
        return f"{mins}m"
    return f"{mins // 60}h{mins % 60}m"


def _attach_in_flight_monitor(repo: Path, status: dict[str, Any], outcome: dict[str, Any]) -> None:
    wait = outcome.get("wait") if isinstance(outcome.get("wait"), dict) else None
    if not wait or wait.get("kind") != "vm_in_flight":
        return
    existing = status.get("in_flight_monitor") if isinstance(status.get("in_flight_monitor"), dict) else None
    snap: dict[str, Any] | None = existing if existing and existing.get("phase") else None
    if snap is None:
        try:
            from scripts.ppe_in_flight_monitor import collect_monitor_snapshot

            snap = collect_monitor_snapshot(repo, local_verdict=str(status.get("verdict") or ""))
            status["in_flight_monitor"] = snap
        except Exception:
            return
    if snap.get("elapsed_in_phase_s") is not None:
        outcome["wait_elapsed_s"] = float(snap["elapsed_in_phase_s"])
    outcome["monitor"] = {
        "phase": snap.get("phase"),
        "status": snap.get("status"),
        "elapsed_in_phase_m": snap.get("elapsed_in_phase_m"),
        "next_poll_m": snap.get("next_poll_m"),
        "stuck": snap.get("stuck"),
        "stale_recover": snap.get("stale_recover"),
        "productive_evidence": snap.get("productive_evidence"),
        "stuck_threshold_m": snap.get("stuck_threshold_m"),
        "done": snap.get("done"),
        "completion_action": snap.get("completion_action"),
        "mirror_stale": snap.get("mirror_stale"),
        "log_tail": snap.get("log_tail"),
    }
    if snap.get("stuck") and outcome.get("wait_health") not in ("deadlock", "stuck"):
        outcome["wait_health"] = "stuck"


def format_pass_lines(outcome: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    summary = str(outcome.get("progress_summary") or "none")
    pclass = str(outcome.get("progress_class") or "none")
    if outcome.get("had_progress"):
        lines.append(f"**Progress:** {summary}")
    elif pclass == "low":
        lines.append(f"**Progress:** low — {summary} (waiting; does not reset streak)")
    else:
        streak = int(outcome.get("consecutive_no_progress") or 0)
        window = int(outcome.get("no_progress_in_last_10") or 0)
        streak_s = f" · Streak: {streak} in a row · {window}/{STREAK_WINDOW} last passes" if streak >= 2 else ""
        lines.append(f"**Progress:** none{streak_s}")

    wait = outcome.get("wait") if isinstance(outcome.get("wait"), dict) else None
    health = str(outcome.get("wait_health") or "none")
    if wait and health != "none":
        elapsed = _format_duration(outcome.get("wait_elapsed_s"))
        expected = _format_duration(float(outcome.get("wait_expected_s") or 0))
        waiting_for = str(wait.get("waiting_for") or "")
        evidence = outcome.get("evidence_signals") or []
        ev_s = f" ({', '.join(evidence)})" if evidence else ""
        health_label = health.upper() if health in ("stuck", "deadlock", "unknown") else health
        lines.append(
            f"**Waiting:** {waiting_for} · Expected: ~{expected} · Elapsed: {elapsed} · "
            f"Evidence: {health_label}{ev_s}"
        )
    elif health == "deadlock":
        lines.append("**Waiting:** coordination/deadlock — no active program advancing")

    monitor = outcome.get("monitor") if isinstance(outcome.get("monitor"), dict) else None
    if monitor and wait and health != "none":
        parts: list[str] = []
        if monitor.get("phase"):
            parts.append(f"phase `{monitor.get('phase')}`")
        if monitor.get("elapsed_in_phase_m") is not None:
            parts.append(f"elapsed {monitor.get('elapsed_in_phase_m')}m")
        if monitor.get("next_poll_m"):
            parts.append(f"next check ~{monitor.get('next_poll_m')}m")
        if monitor.get("mirror_stale"):
            parts.append("mirror stale — git refresh/merge pending")
        if monitor.get("completion_action"):
            parts.append(f"then {monitor.get('completion_action')}")
        if monitor.get("stuck_threshold_m"):
            parts.append(f"stuck threshold ~{monitor.get('stuck_threshold_m')}m")
        if parts:
            lines.append(f"**Monitor:** {' · '.join(parts)}")
        log_tail = monitor.get("log_tail") if isinstance(monitor.get("log_tail"), dict) else None
        combined = str((log_tail or {}).get("combined") or "").strip()
        if monitor.get("stuck") and combined:
            lines.append("**Stuck log tail:**")
            for log_line in combined.splitlines()[:22]:
                lines.append(f"  {log_line}")

    if health in ("stuck", "deadlock") or int(outcome.get("consecutive_no_progress") or 0) >= ALERT_STREAK_THRESHOLD:
        lines.append("**Alert:** factory wait unhealthy — agents should triage (fix_vm / coordination repair)")

    return lines


def collect_operator_pass_stats(repo: Path, *, window: int = STREAK_WINDOW) -> dict[str, Any]:
    rows = read_operator_passes(repo)[-window:]
    latest = _load_json(repo / LATEST_REL)
    no_prog = sum(1 for r in rows if not r.get("had_progress"))
    stuck = sum(1 for r in rows if str(r.get("wait_health") or "") in ("stuck", "deadlock"))
    low = sum(1 for r in rows if str(r.get("progress_class") or "") == "low")
    return {
        "passes_in_window": len(rows),
        "no_progress_in_window": no_prog,
        "stuck_or_deadlock_in_window": stuck,
        "low_progress_in_window": low,
        "latest": latest,
        "consecutive_no_progress": int(latest.get("consecutive_no_progress") or 0),
        "wait_health": latest.get("wait_health"),
        "recent": list(reversed(rows[-10:])),
    }


def scan_operator_pass_friction(repo: Path) -> tuple[list[Any], dict[str, int]]:
    from scripts.ppe_workflow_radar import RadarCandidate

    stats = collect_operator_pass_stats(repo)
    signals: dict[str, int] = {}
    candidates: list[Any] = []
    no_prog = int(stats.get("no_progress_in_window") or 0)
    if no_prog >= RADAR_STREAK_THRESHOLD:
        signals["operator_no_progress_streak"] = no_prog
        candidates.append(
            RadarCandidate(
                id="operator-no-progress-streak",
                severity="watch",
                title="Many operator passes without factory progress",
                evidence=[
                    f"no_progress_in_last_{STREAK_WINDOW}={no_prog}",
                    f"consecutive={stats.get('consecutive_no_progress')}",
                    f"wait_health={stats.get('wait_health')}",
                ],
                suggested_action=(
                    "Run fix_vm_operator / coordination repair; "
                    "see artifacts/workflow_metrics/operator_passes.jsonl."
                ),
            )
        )
    return candidates, signals


def backfill_operator_passes(repo: Path, *, limit: int = 30) -> dict[str, Any]:
    """Seed operator_passes.jsonl from context closeouts (v3 one-time)."""
    from scripts.workflow_metrics_cli import read_context_windows

    existing = {str(r.get("pass_at") or "") for r in read_operator_passes(repo)}
    added = 0
    for row in read_context_windows(repo)[-limit:]:
        closed_at = str(row.get("closed_at") or "")
        if closed_at in existing:
            continue
        slices_n = int(row.get("slices_closed_in_thread") or 0)
        had = slices_n > 0
        synthetic = {
            "event": "operator_pass",
            "pass_at": closed_at or _utc_now(),
            "fingerprint": f"backfill|{closed_at}",
            "verdict": row.get("operator_verdict"),
            "chapter_id": row.get("chapter_id"),
            "had_progress": had,
            "progress_class": "high" if slices_n > 0 else "none",
            "progress_summary": f"backfill: {slices_n} slice(s) in thread" if had else "none",
            "consecutive_no_progress": 0 if had else 1,
            "no_progress_in_last_10": 0 if had else 1,
            "wait_health": "none",
            "backfill": True,
            "source": "context_windows.jsonl",
        }
        _append_jsonl(_passes_path(repo), synthetic)
        added += 1
    return {"added": added, "limit": limit}


def maybe_founder_alert_from_pass(repo: Path, outcome: dict[str, Any]) -> dict[str, Any]:
    """Layer 3 ntfy when wait unhealthy or long no-progress streak (v2). Deduped."""
    health = str(outcome.get("wait_health") or "")
    streak = int(outcome.get("consecutive_no_progress") or 0)
    should = health in ("stuck", "deadlock") or streak >= ALERT_STREAK_THRESHOLD
    result: dict[str, Any] = {"attempted": False, "skipped": True}
    if not should:
        result["reason"] = "healthy"
        return result

    fp = f"{health}|{streak}|{outcome.get('fingerprint')}"
    prior = _load_json(repo / FOUNDER_ALERT_STATE_REL)
    if str(prior.get("fingerprint") or "") == fp:
        result["reason"] = "deduped"
        return result

    wait = outcome.get("wait") if isinstance(outcome.get("wait"), dict) else {}
    body_lines = [
        "Alert: operator pass — factory wait unhealthy.",
        "",
        f"Progress: {outcome.get('progress_summary') or 'none'}",
        f"Streak: {streak} in a row · {outcome.get('no_progress_in_last_10')}/{STREAK_WINDOW} last passes",
        f"Wait health: {health}",
    ]
    if wait.get("waiting_for"):
        body_lines.append(f"Waiting: {wait.get('waiting_for')}")
    body_lines.append("Agents triaging — nothing required unless this repeats after repair.")

    pulse = {
        "layer": "alert",
        "title": "PPE alert — operator pass stall",
        "body": "\n".join(body_lines),
        "founder_role": "listen",
    }
    try:
        from scripts.ppe_founder_pulse import maybe_notify, write_pulse_artifact

        write_pulse_artifact(repo, pulse)
        notify = maybe_notify(repo, pulse)
        _save_json(repo / FOUNDER_ALERT_STATE_REL, {"fingerprint": fp, "pass_at": _utc_now(), "notify": notify})
        result = {"attempted": True, "skipped": False, "notify": notify, "fingerprint": fp}
    except Exception as exc:
        result = {"attempted": True, "skipped": False, "error": str(exc)}
    return result


def enrich_status_with_pass_progress(repo: Path, status: dict[str, Any], *, record: bool = True) -> dict[str, Any]:
    outcome = record_operator_pass(repo, status, append=record)
    _attach_in_flight_monitor(repo, status, outcome)
    status["operator_pass_progress"] = outcome
    status["operator_pass_lines"] = format_pass_lines(outcome)
    if record:
        alert_result = maybe_founder_alert_from_pass(repo, outcome)
        outcome["founder_alert"] = alert_result
    return outcome


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Operator pass progress assess/record")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-record", action="store_true", help="Assess only; do not append jsonl")
    ap.add_argument("--backfill", action="store_true", help="Seed passes from context_windows.jsonl")
    ap.add_argument("--backfill-limit", type=int, default=30)
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.backfill:
        report = backfill_operator_passes(repo, limit=max(1, args.backfill_limit))
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"ppe_operator_pass_progress: backfill added {report.get('added')} row(s)")
        return 0
    from scripts.ppe_operator_status import prepare_operator_status

    status = prepare_operator_status(repo)
    outcome = enrich_status_with_pass_progress(repo, status, record=not args.no_record)
    if args.json:
        print(json.dumps(outcome, indent=2))
    else:
        for line in format_pass_lines(outcome):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
