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
DESKTOP_RUN_LOCAL_BUDGET_SECONDS = 4 * 3600
BUILD_LOCK_BUDGET_SECONDS = 2 * 3600
RELAY_ACTIVE_BUDGET_SECONDS = 3 * 3600
EVIDENCE_RECENT_SECONDS = 900
PASS_DEDUPE_SECONDS = 120
STREAK_WINDOW = 10

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
        budget = PHASE_BUDGET_SECONDS.get(vm_phase, 3600)
        action = "run_ppe_local / relay finish" if vm_phase == "FINISH_IN_FLIGHT" else "product BUILD on VM"
        return {
            "kind": "vm_in_flight",
            "phase": vm_phase,
            "waiting_for": f"VM `{vm_phase}` — {action} ({chapter})",
            "expected_seconds": budget,
            "since_at": since_at,
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
            return {
                "kind": "relay_active",
                "phase": "CLOSEOUT_PENDING",
                "waiting_for": f"Relay in flight — `{sid}`",
                "expected_seconds": RELAY_ACTIVE_BUDGET_SECONDS,
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


def format_pass_lines(outcome: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    summary = str(outcome.get("progress_summary") or "none")
    if outcome.get("had_progress"):
        lines.append(f"**Progress:** {summary}")
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

    if health in ("stuck", "deadlock") or int(outcome.get("consecutive_no_progress") or 0) >= 4:
        lines.append("**Alert:** factory wait unhealthy — agents should triage (fix_vm / coordination repair)")

    return lines


def enrich_status_with_pass_progress(repo: Path, status: dict[str, Any], *, record: bool = True) -> dict[str, Any]:
    outcome = record_operator_pass(repo, status, append=record)
    status["operator_pass_progress"] = outcome
    status["operator_pass_lines"] = format_pass_lines(outcome)
    return outcome


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Operator pass progress assess/record")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-record", action="store_true", help="Assess only; do not append jsonl")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
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
