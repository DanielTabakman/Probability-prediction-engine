"""Multi-agent worker leases — lanes, cost preference, and synthetic events."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

ACTIVE_LEASE_REL = "artifacts/control_plane/ACTIVE_LEASE.json"
WORK_DISPATCH_REL = "artifacts/control_plane/WORK_DISPATCH.json"
WORKER_EVENTS_REL = "artifacts/control_plane/WORKER_EVENTS.json"
DESKTOP_BUILD_HANDOFF_REL = "artifacts/control_plane/DESKTOP_BUILD_HANDOFF.json"
REGISTRY_REL = "docs/SOP/WORKER_REGISTRY_V1.json"

LANE_CURSOR = "cursor-desktop"
LANE_CODEX = "codex-app"
LANE_VM = "vm-relay"
LANE_SCRIPTS = "scripts-only"

CONTROL_PLANE_BRANCH_PREFIXES = ("control-plane/", "ops/", "chore/")
RELAY_VERDICTS = frozenset({"RUN_LOCAL", "IDE_BUILD", "RUN_AUTO"})


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _utc_iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip()


def _dirty_paths(repo: Path) -> list[str]:
    proc = _git(repo, "status", "--porcelain")
    if proc.returncode != 0:
        return []
    paths: list[str] = []
    for line in (proc.stdout or "").splitlines():
        if len(line) < 4 or line.startswith("##"):
            continue
        raw = line[3:].strip().split(" -> ")[-1].replace("\\", "/")
        if raw.endswith("/"):
            dir_path = repo / raw.rstrip("/")
            if dir_path.is_dir():
                for f in sorted(dir_path.rglob("*")):
                    if f.is_file():
                        paths.append(str(f.relative_to(repo)).replace("\\", "/"))
            continue
        paths.append(raw)
    return paths


def _normalize_globs(globs: list[str] | None) -> list[str]:
    return [str(g).strip().replace("\\", "/") for g in (globs or []) if str(g).strip()]


def path_matches_any(path: str, globs: list[str]) -> bool:
    norm = path.replace("\\", "/")
    return any(fnmatch.fnmatch(norm, g) for g in globs)


def paths_overlap(dirty: list[str], globs: list[str], forbidden: list[str]) -> list[str]:
    hits: list[str] = []
    for p in dirty:
        if forbidden and path_matches_any(p, forbidden):
            hits.append(p)
        elif globs and path_matches_any(p, globs):
            hits.append(p)
        elif not globs:
            hits.append(p)
    return hits


def load_lease(repo: Path) -> dict[str, Any] | None:
    path = repo / ACTIVE_LEASE_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def save_lease(repo: Path, lease: dict[str, Any]) -> Path:
    path = repo / ACTIVE_LEASE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lease, indent=2) + "\n", encoding="utf-8")
    return path


def release_lease(repo: Path) -> bool:
    path = repo / ACTIVE_LEASE_REL
    if not path.is_file():
        return False
    path.unlink(missing_ok=True)
    return True


def maybe_release_lease_on_mark_ready(
    repo: Path,
    *,
    slice_id: str,
    build_branch: str | None = None,
) -> dict[str, Any]:
    """Release ACTIVE_LEASE when mark_ide_product_ready matches slice + branch."""
    repo = repo.resolve()
    lease = load_lease(repo)
    if not lease or not _lease_active(lease):
        return {"released": False, "reason": "no_active_lease"}

    work_item = lease.get("work_item") if isinstance(lease.get("work_item"), dict) else {}
    lease_slice = str(work_item.get("slice_id") or "").strip()
    if lease_slice and lease_slice != slice_id.strip():
        return {
            "released": False,
            "reason": "slice_mismatch",
            "lease_slice": lease_slice,
            "slice_id": slice_id,
        }

    lease_branch = str(lease.get("branch") or "").strip()
    current = _current_branch(repo)
    branch = (build_branch or current).strip()
    if lease_branch and lease_branch not in {current, branch}:
        return {
            "released": False,
            "reason": "branch_mismatch",
            "lease_branch": lease_branch,
            "current_branch": current,
            "build_branch": branch,
        }

    lease_id = lease.get("lease_id")
    released = release_lease(repo)
    return {
        "released": released,
        "reason": "mark_ide_product_ready",
        "lease_id": lease_id,
        "slice_id": slice_id,
        "branch": branch or current,
    }


def load_worker_registry(repo: Path) -> dict[str, Any]:
    path = repo / REGISTRY_REL
    if not path.is_file():
        return {"workers": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"workers": []}
    return data if isinstance(data, dict) else {"workers": []}


def suggest_lane(
    *,
    verdict: str,
    branch: str,
    closeout_only: bool,
    loop_host_allowed: bool,
) -> str:
    if verdict in ("RUN_LOCAL", "RUN_AUTO"):
        return LANE_VM
    if closeout_only:
        return LANE_SCRIPTS
    if verdict == "IDE_BUILD":
        if any(branch.startswith(p) for p in CONTROL_PLANE_BRANCH_PREFIXES):
            return LANE_CODEX
        return LANE_CURSOR
    return LANE_CURSOR


def _cost_lane_counts(repo: Path, *, days: int = 7) -> dict[str, int]:
    try:
        from scripts.ppe_workflow_cost import summarize_by_lane

        summary = summarize_by_lane(repo, days=days)
        raw = summary.get("by_lane") if isinstance(summary.get("by_lane"), dict) else {}
        return {str(k): int(v) for k, v in raw.items()}
    except Exception:
        return {}


def _load_lane_est_usd(repo: Path) -> dict[str, float]:
    path = repo / "docs/SOP/PPE_COST_LANE_ESTIMATES.json"
    if not path.is_file():
        from scripts.ppe_workflow_cost import DEFAULT_LANE_EST_USD

        return dict(DEFAULT_LANE_EST_USD)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict):
            return {str(k): float(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        pass
    from scripts.ppe_workflow_cost import DEFAULT_LANE_EST_USD

    return dict(DEFAULT_LANE_EST_USD)


def _worker_lane_est_usd(registry: dict[str, Any], worker_id: str, est: dict[str, float]) -> float:
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    row = next((w for w in workers if isinstance(w, dict) and w.get("id") == worker_id), None)
    lanes = row.get("cost_lanes") if isinstance(row, dict) else None
    if not lanes:
        return est.get("unspecified", 0.5)
    return min(float(est.get(str(lane), est.get("unspecified", 0.5))) for lane in lanes)


def prefer_build_lane(
    repo: Path,
    *,
    verdict: str,
    branch: str,
    closeout_only: bool,
    loop_host_allowed: bool = False,
    path_globs: list[str] | None = None,
) -> dict[str, Any]:
    """Tier 2: branch heuristic + 7d cost lanes → preferred worker lane."""
    base = suggest_lane(
        verdict=verdict,
        branch=branch,
        closeout_only=closeout_only,
        loop_host_allowed=loop_host_allowed,
    )
    reason = "branch_heuristic"
    preferred = base
    counts = _cost_lane_counts(repo)
    codex_n = counts.get("codex-cli", 0)
    cursor_n = counts.get("cursor-cli", 0) + counts.get("acp", 0)
    registry = load_worker_registry(repo)
    est = _load_lane_est_usd(repo)
    codex_usd = _worker_lane_est_usd(registry, LANE_CODEX, est)
    cursor_usd = _worker_lane_est_usd(registry, LANE_CURSOR, est)

    globs = _normalize_globs(path_globs)
    product_scope = any(g.startswith("src/") for g in globs) or (
        not globs and not any(branch.startswith(p) for p in CONTROL_PLANE_BRANCH_PREFIXES)
    )

    if verdict == "IDE_BUILD" and not closeout_only:
        if product_scope:
            codex_pref = False
            codex_preflight: dict[str, Any] = {}
            try:
                from scripts.ppe_build_worker import (
                    PREF_CODEX,
                    build_worker_preflight_status,
                    load_build_worker_pref,
                )

                codex_pref = load_build_worker_pref(repo) == PREF_CODEX
                codex_preflight = build_worker_preflight_status(repo)
            except Exception:
                codex_pref = False
                codex_preflight = {}

            if codex_pref and (
                codex_preflight.get("ok") or codex_preflight.get("classification") == "routing_tooling"
            ):
                preferred = LANE_CODEX
                reason = (
                    "codex_build_worker_pref"
                    if codex_preflight.get("ok")
                    else "codex_build_worker_pref_tooling_gap"
                )
            elif codex_pref and codex_preflight.get("classification") == "fallback_available":
                preferred = LANE_CURSOR
                reason = "codex_preflight_cursor_fallback"
            else:
                preferred = LANE_CURSOR
                reason = "product_path_scope"
        elif not product_scope and codex_usd < cursor_usd and any(
            branch.startswith(p) for p in CONTROL_PLANE_BRANCH_PREFIXES
        ):
            preferred = LANE_CODEX
            reason = "cost_usd_prefer_codex"
        elif base == LANE_CODEX and codex_n > cursor_n + 3:
            preferred = LANE_CURSOR
            reason = "cost_cap_codex_high"
        elif base == LANE_CURSOR and branch.startswith(CONTROL_PLANE_BRANCH_PREFIXES[:1]) and codex_n <= cursor_n:
            preferred = LANE_CODEX
            reason = "cost_prefer_codex"

    return {
        "preferred_lane": preferred,
        "base_lane": base,
        "reason": reason,
        "cost_lanes_7d": counts,
        "cost_est_usd": {"codex-app": codex_usd, "cursor-desktop": cursor_usd},
    }


def _lease_active(lease: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or _utc_now()
    expires = _parse_utc(str(lease.get("expires_at") or ""))
    if expires is not None and now >= expires:
        return False
    return True


def assess_worker_lease(
    repo: Path,
    status: dict[str, Any] | None = None,
    *,
    proposed_worker: str | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)

    verdict = str(status.get("verdict") or "")
    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    closeout_only = bool(chapter_mode.get("do_not_rebuild")) or str(chapter_mode.get("mode") or "") == "CLOSEOUT_ONLY"

    loop_host_allowed = False
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        loop_host_allowed = bool(loop_host_start_allowed()[0])
    except Exception:
        pass

    branch = _current_branch(repo)
    dirty = _dirty_paths(repo)
    lease = load_lease(repo)
    now = _utc_now()

    lane_pref = prefer_build_lane(
        repo,
        verdict=verdict,
        branch=branch,
        closeout_only=closeout_only,
        loop_host_allowed=loop_host_allowed,
        path_globs=_normalize_globs((lease or {}).get("path_globs")),
    )

    result: dict[str, Any] = {
        "as_of": _utc_iso(now),
        "suggested_lane": lane_pref["preferred_lane"],
        "lane_preference": lane_pref,
        "current_branch": branch,
        "dirty_count": len(dirty),
        "active": False,
        "expired": False,
        "blocks_dispatch": False,
        "blocks_relay": False,
        "reasons": [],
        "path_conflicts": [],
        "lease": lease,
    }

    if lease is None:
        if closeout_only and any(p.startswith("src/") for p in dirty) and verdict in RELAY_VERDICTS:
            result["reasons"].append("CLOSEOUT_ONLY with dirty src/ — park product edits before relay")
            result["blocks_dispatch"] = True
        return result

    if not _lease_active(lease, now):
        result["expired"] = True
        result["reasons"].append("ACTIVE_LEASE expired — release or re-acquire before BUILD")
        return result

    result["active"] = True
    lease_branch = str(lease.get("branch") or "").strip()
    lease_worker = str(lease.get("worker_id") or lease.get("lane") or "").strip()
    path_globs = _normalize_globs(lease.get("path_globs"))
    forbidden = _normalize_globs(lease.get("forbidden_globs"))
    exclusive = lease.get("exclusive", True)

    if lease_branch and branch != lease_branch:
        result["reasons"].append(f"checkout {branch!r} != lease branch {lease_branch!r}")
        result["blocks_dispatch"] = True
        if verdict in RELAY_VERDICTS and not loop_host_allowed:
            result["blocks_relay"] = True

    conflicts = paths_overlap(dirty, path_globs, forbidden)
    if conflicts and exclusive:
        result["path_conflicts"] = conflicts[:10]
        result["reasons"].append(f"dirty paths overlap lease scope ({len(conflicts)} path(s))")
        result["blocks_dispatch"] = True

    for p in dirty:
        if forbidden and path_matches_any(p, forbidden):
            result["reasons"].append(f"forbidden path dirty under lease: {p}")
            result["blocks_dispatch"] = True
            break

    if closeout_only and any(p.startswith("src/") for p in dirty):
        result["reasons"].append("CLOSEOUT_ONLY forbids product edits under src/")
        result["blocks_dispatch"] = True

    if proposed_worker and lease_worker and proposed_worker != lease_worker and exclusive:
        result["reasons"].append(f"lease held by {lease_worker!r}, cannot dispatch {proposed_worker!r}")
        result["blocks_dispatch"] = True

    return result


def infer_worker_events(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    """Tier 2: infer worker progress from git + markers (no Codex API)."""
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)

    now = _utc_iso(_utc_now())
    events: list[dict[str, Any]] = []
    branch = _current_branch(repo)
    dirty = _dirty_paths(repo)

    proc = _git(repo, "log", "-1", "--format=%H %s")
    if proc.returncode == 0 and (proc.stdout or "").strip():
        parts = (proc.stdout or "").strip().split(" ", 1)
        events.append(
            {
                "event": "git_head",
                "at": now,
                "commit": parts[0],
                "subject": parts[1] if len(parts) > 1 else "",
                "branch": branch,
            }
        )

    trigger = repo / ".cursor" / "IDE_BUILD_TRIGGER.json"
    if trigger.is_file():
        try:
            data = json.loads(trigger.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                events.append({"event": "ide_build_trigger", "at": now, "payload": data})
        except (OSError, json.JSONDecodeError):
            pass

    ready_marker = repo / "artifacts" / "orchestrator" / "IDE_PRODUCT_READY.json"
    if ready_marker.is_file():
        try:
            data = json.loads(ready_marker.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                events.append({"event": "ide_product_ready", "at": now, "payload": data})
        except (OSError, json.JSONDecodeError):
            pass

    lease = load_lease(repo)
    if lease and _lease_active(lease):
        events.append(
            {
                "event": "lease_active",
                "at": now,
                "worker_id": lease.get("worker_id"),
                "branch": lease.get("branch"),
                "expires_at": lease.get("expires_at"),
            }
        )

    assessment = assess_worker_lease(repo, status)
    if assessment.get("blocks_dispatch"):
        events.append(
            {
                "event": "dispatch_blocked",
                "at": now,
                "reasons": assessment.get("reasons") or [],
            }
        )

    if dirty:
        events.append({"event": "dirty_tree", "at": now, "paths": dirty[:20], "count": len(dirty)})

    return {
        "schema_version": 1,
        "as_of": now,
        "events": events,
        "suggested_lane": assessment.get("suggested_lane"),
        "verdict": status.get("verdict"),
    }


def write_worker_events(repo: Path, status: dict[str, Any] | None = None) -> Path:
    payload = infer_worker_events(repo, status)
    path = repo / WORKER_EVENTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def build_work_dispatch(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    if status is None:
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)

    assessment = assess_worker_lease(repo, status)
    lane_pref = assessment.get("lane_preference") if isinstance(assessment.get("lane_preference"), dict) else {}
    preferred = str(assessment.get("suggested_lane") or LANE_CURSOR)
    fallback = LANE_CURSOR if preferred == LANE_CODEX else LANE_CODEX

    verdict = str(status.get("verdict") or "")
    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    mode = str(chapter_mode.get("mode") or verdict)

    slice_id = str(status.get("product_slice") or "").strip() or None
    if not slice_id:
        guard = status.get("guard") if isinstance(status.get("guard"), dict) else {}
        detail = str(guard.get("detail") or status.get("blocker") or "")
        left, right = detail.find("["), detail.find("]")
        if left >= 0 and right > left:
            ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
            if ids:
                slice_id = ids[0]

    lease = assessment.get("lease") if isinstance(assessment.get("lease"), dict) else {}
    branch = str(lease.get("branch") or assessment.get("current_branch") or _current_branch(repo))
    now = _utc_now()
    dispatch_id = f"wi-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    kind = "finish_closeout" if mode == "CLOSEOUT_ONLY" and verdict == "RUN_LOCAL" else "ide_build"
    if verdict == "RUN_AUTO":
        kind = "relay_auto"

    registry = load_worker_registry(repo)
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    worker_row = next((w for w in workers if isinstance(w, dict) and w.get("id") == preferred), {})
    path_globs = _normalize_globs(lease.get("path_globs")) or _normalize_globs(
        worker_row.get("default_path_globs")
    )
    forbidden = _normalize_globs(lease.get("forbidden_globs"))
    if mode == "CLOSEOUT_ONLY" and "src/**" not in forbidden:
        forbidden = [*forbidden, "src/**"]

    return {
        "schema_version": 1,
        "dispatch_id": dispatch_id,
        "as_of": _utc_iso(now),
        "work_item": {"slice_id": slice_id, "kind": kind, "verdict": verdict, "mode": mode},
        "lane": {
            "machine": "vm" if preferred == LANE_VM else "desktop",
            "runtime": str(worker_row.get("runtime") or preferred),
            "worker_id": preferred,
            "fallback_worker_id": fallback,
            "preference_reason": lane_pref.get("reason"),
        },
        "lease": {
            "lease_id": lease.get("lease_id"),
            "branch": branch,
            "path_globs": path_globs,
            "forbidden_globs": forbidden,
            "expires_at": lease.get("expires_at"),
            "active": bool(assessment.get("active")),
        },
        "handoff": {
            "continuity_uri": "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
            "operator_status_uri": "artifacts/orchestrator/OPERATOR_STATUS.md",
            "lane_policy_uri": "docs/SOP/WORKER_LANE_POLICY_V1.md",
        },
        "acceptance": {
            "gate": "python scripts/run_pushable_gate.py",
            "ship": "python scripts/ppe_worker_lease.py --ship --release",
            "branch_recovery": "python scripts/ppe_branch_recovery.py --plane control --ship",
            "mark_ready": f"python scripts/mark_ide_product_ready.py --slice {slice_id}" if slice_id else None,
            "relay_continue": "DESKTOP_CONTINUE.cmd --no-pause",
        },
        "coordination": {
            "other_workers_blocked": bool(assessment.get("active")),
            "blocks_dispatch": bool(assessment.get("blocks_dispatch")),
            "notes": "; ".join(assessment.get("reasons") or []) or None,
        },
    }


def write_work_dispatch(repo: Path, status: dict[str, Any] | None = None) -> Path:
    dispatch = build_work_dispatch(repo, status)
    path = repo / WORK_DISPATCH_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dispatch, indent=2) + "\n", encoding="utf-8")
    return path


def acquire_lease(
    repo: Path,
    *,
    worker_id: str,
    branch: str | None = None,
    path_globs: list[str] | None = None,
    forbidden_globs: list[str] | None = None,
    ttl_hours: float = 2.0,
    exclusive: bool = True,
    notes: str | None = None,
    work_item: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    existing = load_lease(repo)
    if existing and _lease_active(existing):
        assessment = assess_worker_lease(repo, proposed_worker=worker_id)
        if assessment.get("blocks_dispatch"):
            raise RuntimeError(
                "Cannot acquire lease: " + "; ".join(assessment.get("reasons") or ["active lease conflict"])
            )

    now = _utc_now()
    expires = now + timedelta(hours=ttl_hours)
    branch = branch or _current_branch(repo)
    lease_id = f"lease-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    lease = {
        "schema_version": 1,
        "lease_id": lease_id,
        "worker_id": worker_id,
        "lane": worker_id,
        "machine": "desktop" if worker_id != LANE_VM else "vm",
        "branch": branch,
        "exclusive": exclusive,
        "path_globs": _normalize_globs(path_globs),
        "forbidden_globs": _normalize_globs(forbidden_globs),
        "work_item": work_item or {},
        "acquired_at": _utc_iso(now),
        "expires_at": _utc_iso(expires),
        "notes": notes,
    }
    save_lease(repo, lease)
    return lease


def lane_to_handoff_worker(lane: str) -> str:
    """Map ARCP lane id to ppe_build_worker handoff kind."""
    if lane == LANE_CODEX:
        return "codex-cli"
    if lane == LANE_CURSOR:
        return "manual"
    return "manual"


def default_lease_scope_for_lane(
    repo: Path,
    worker_id: str,
    *,
    branch: str,
    closeout_only: bool,
    product_build: bool = False,
) -> tuple[list[str], list[str]]:
    registry = load_worker_registry(repo)
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    row = next((w for w in workers if isinstance(w, dict) and w.get("id") == worker_id), {})
    path_globs = _normalize_globs(row.get("default_path_globs"))
    forbidden: list[str] = []
    product_branch = product_build or any(branch.startswith(p) for p in ("product/", "build/"))
    if worker_id == LANE_CODEX and product_branch:
        product_row = next((w for w in workers if isinstance(w, dict) and w.get("id") == LANE_CURSOR), {})
        product_globs = _normalize_globs(product_row.get("default_path_globs"))
        path_globs = product_globs or ["src/**", "apps/**", "tests/**"]
    if closeout_only or (worker_id == LANE_CODEX and not product_branch):
        forbidden.append("src/**")
    if worker_id == LANE_CURSOR and any(branch.startswith(p) for p in ("product/", "build/")):
        forbidden = [g for g in forbidden if g != "src/**"]
    return path_globs, forbidden


def load_desktop_build_handoff(repo: Path) -> dict[str, Any] | None:
    path = repo / DESKTOP_BUILD_HANDOFF_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def write_desktop_build_handoff(repo: Path, record: dict[str, Any]) -> Path:
    path = repo / DESKTOP_BUILD_HANDOFF_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def _refresh_lease_ttl(repo: Path, lease: dict[str, Any], *, ttl_hours: float) -> dict[str, Any]:
    now = _utc_now()
    lease = {**lease, "expires_at": _utc_iso(now + timedelta(hours=ttl_hours))}
    save_lease(repo, lease)
    return lease


def prepare_desktop_build_handoff(
    repo: Path,
    status: dict[str, Any] | None = None,
    *,
    ttl_hours: float = 4.0,
) -> dict[str, Any]:
    """DESKTOP_BUILD entry: prefer lane, acquire/refresh lease, write dispatch."""
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)

    verdict = str(status.get("verdict") or "")
    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    closeout_only = bool(chapter_mode.get("do_not_rebuild")) or str(chapter_mode.get("mode") or "") == "CLOSEOUT_ONLY"
    mode = str(chapter_mode.get("mode") or verdict)
    branch = _current_branch(repo)

    lane_pref = prefer_build_lane(
        repo,
        verdict=verdict,
        branch=branch,
        closeout_only=closeout_only,
    )
    worker_id = str(lane_pref.get("preferred_lane") or LANE_CURSOR)
    path_globs, forbidden = default_lease_scope_for_lane(
        repo,
        worker_id,
        branch=branch,
        closeout_only=closeout_only,
        product_build=verdict == "IDE_BUILD" and not closeout_only,
    )

    slice_id = str(status.get("product_slice") or "").strip() or None
    if not slice_id:
        guard = status.get("guard") if isinstance(status.get("guard"), dict) else {}
        detail = str(guard.get("detail") or status.get("blocker") or "")
        left, right = detail.find("["), detail.find("]")
        if left >= 0 and right > left:
            ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
            if ids:
                slice_id = ids[0]

    work_item = {
        "slice_id": slice_id,
        "verdict": verdict,
        "mode": mode,
        "source": "DESKTOP_BUILD",
    }

    blocked = False
    reasons: list[str] = []
    lease: dict[str, Any] | None = None
    existing = load_lease(repo)
    should_lease = verdict == "IDE_BUILD" and not closeout_only

    if not should_lease:
        reasons.append(
            f"skip auto-lease (verdict={verdict!r}, closeout_only={closeout_only}) — handoff only"
        )
    elif existing and _lease_active(existing):
        same_worker = str(existing.get("worker_id") or existing.get("lane") or "") == worker_id
        same_branch = str(existing.get("branch") or "") == branch
        if same_worker and same_branch:
            lease = _refresh_lease_ttl(repo, existing, ttl_hours=ttl_hours)
        else:
            assessment = assess_worker_lease(repo, status, proposed_worker=worker_id)
            if assessment.get("blocks_dispatch"):
                blocked = True
                reasons.extend(assessment.get("reasons") or [])
            else:
                release_lease(repo)
                lease = acquire_lease(
                    repo,
                    worker_id=worker_id,
                    branch=branch,
                    path_globs=path_globs,
                    forbidden_globs=forbidden,
                    ttl_hours=ttl_hours,
                    work_item=work_item,
                    notes="DESKTOP_BUILD auto-acquire",
                )
    elif should_lease:
        try:
            lease = acquire_lease(
                repo,
                worker_id=worker_id,
                branch=branch,
                path_globs=path_globs,
                forbidden_globs=forbidden,
                ttl_hours=ttl_hours,
                work_item=work_item,
                notes="DESKTOP_BUILD auto-acquire",
            )
        except RuntimeError as exc:
            blocked = True
            reasons.append(str(exc))

    dispatch_path: str | None = None
    if not blocked:
        write_work_dispatch(repo, status)
        write_worker_events(repo, status)
        dispatch_path = WORK_DISPATCH_REL

    record: dict[str, Any] = {
        "schema_version": 1,
        "as_of": _utc_iso(_utc_now()),
        "preferred_lane": worker_id,
        "handoff_worker": lane_to_handoff_worker(worker_id),
        "lane_preference": lane_pref,
        "lease_id": (lease or {}).get("lease_id"),
        "branch": branch,
        "path_globs": path_globs,
        "forbidden_globs": forbidden,
        "blocked": blocked,
        "reasons": reasons,
        "dispatch_uri": dispatch_path,
        "work_item": work_item,
    }
    write_desktop_build_handoff(repo, record)
    return record


def _commit_message_for_ship_paths(paths: list[str]) -> str:
    norm = [p.replace("\\", "/") for p in paths]
    if norm and all(p.startswith("docs/") for p in norm):
        return "control-plane: lease ship (docs)"
    if any(p.startswith("src/") or p.startswith("apps/") for p in norm):
        return "product: lease ship"
    if any(p.startswith("tests/") or p.startswith("scripts/") for p in norm):
        return "evidence-plane: lease ship"
    return "control-plane: lease ship"


def _ship_excluded(path: str) -> bool:
    p = path.replace("\\", "/")
    if p.startswith(("artifacts/", "_worktrees/", ".cursor/projects/")):
        return True
    lower = p.lower()
    return lower in {".env", ".env.local"} or "credential" in lower


def scoped_dirty_paths(
    repo: Path,
    *,
    path_globs: list[str],
    forbidden_globs: list[str],
) -> list[str]:
    scoped: list[str] = []
    for p in _dirty_paths(repo):
        if _ship_excluded(p):
            continue
        if forbidden_globs and path_matches_any(p, forbidden_globs):
            continue
        if path_globs and not path_matches_any(p, path_globs):
            continue
        scoped.append(p)
    return scoped


def _ensure_work_branch(repo: Path, branch: str) -> tuple[bool, str, str]:
    current = _current_branch(repo)
    if not branch:
        return True, current, "no branch constraint"
    if current == branch:
        return True, branch, "on lease branch"
    co = _git(repo, "checkout", branch)
    if co.returncode == 0:
        return True, branch, f"checked out {branch}"
    cob = _git(repo, "checkout", "-b", branch)
    if cob.returncode == 0:
        return True, branch, f"created branch {branch}"
    detail = (co.stderr or co.stdout or cob.stderr or cob.stdout or "checkout failed").strip()
    return False, current, detail


def ship_lease_work(
    repo: Path,
    *,
    dry_run: bool = False,
    release_after: bool = False,
    message: str | None = None,
    pre_push: bool = False,
    path_globs: list[str] | None = None,
    forbidden_globs: list[str] | None = None,
    branch: str | None = None,
) -> dict[str, Any]:
    """Stage lease-scoped dirty paths → gate → commit → push → PR."""
    repo = repo.resolve()
    lease = load_lease(repo)
    globs = _normalize_globs(path_globs or (lease or {}).get("path_globs"))
    forbidden = _normalize_globs(forbidden_globs or (lease or {}).get("forbidden_globs"))
    work_branch = (branch or (lease or {}).get("branch") or _current_branch(repo) or "").strip()

    report: dict[str, Any] = {
        "action": "ship",
        "ok": False,
        "dry_run": dry_run,
        "branch": work_branch,
        "path_globs": globs,
        "steps": [],
    }

    def step(name: str, payload: dict[str, Any]) -> None:
        report["steps"].append({"step": name, **payload})
        if payload.get("ok") is False and not payload.get("optional"):
            report["ok"] = False

    ok_branch, actual_branch, branch_detail = _ensure_work_branch(repo, work_branch)
    step("branch", {"ok": ok_branch, "branch": actual_branch, "detail": branch_detail})
    if not ok_branch:
        report["blocked"] = True
        report["reason"] = branch_detail
        return report

    scoped = scoped_dirty_paths(repo, path_globs=globs, forbidden_globs=forbidden)
    report["paths"] = scoped
    if not scoped:
        report["ok"] = True
        report["skipped"] = True
        report["reason"] = "no scoped dirty paths"
        return report

    commit_msg = message or _commit_message_for_ship_paths(scoped)
    if dry_run:
        report["ok"] = True
        report["message"] = commit_msg
        step("dry_run", {"ok": True, "paths": scoped, "message": commit_msg})
        return report

    add = _git(repo, "add", "--", *scoped)
    step("stage", {"ok": add.returncode == 0, "count": len(scoped)})
    if add.returncode != 0:
        report["blocked"] = True
        report["reason"] = (add.stderr or add.stdout or "git add failed").strip()
        return report

    from scripts.run_pushable_gate import run_gate_for_paths

    gate_rc = run_gate_for_paths(repo, scoped, pre_push=pre_push)
    step("gate", {"ok": gate_rc == 0, "pre_push": pre_push})
    if gate_rc != 0:
        _git(repo, "reset", "HEAD", "--", *scoped)
        report["blocked"] = True
        report["reason"] = "gate failed — see stderr"
        return report

    commit = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    step("commit", {"ok": commit.returncode == 0, "message": commit_msg})
    if commit.returncode != 0:
        report["blocked"] = True
        report["reason"] = (commit.stderr or commit.stdout or "git commit failed").strip()
        return report

    from scripts.ppe_context_closeout_ship import _publish

    pub = _publish(repo, branch=actual_branch)
    step("publish", pub)
    report["ok"] = bool(pub.get("ok"))

    if pub.get("pr_url"):
        report["pr_url"] = pub["pr_url"]

    if report.get("ok"):
        try:
            from scripts.ppe_operator_vm_mirror_refresh import maybe_sync_desktop_mirror_after_ship

            report["mirror_sync"] = maybe_sync_desktop_mirror_after_ship(repo, pre_push=True)
        except Exception as exc:
            report["mirror_sync"] = {"ok": False, "error": str(exc)}

    if release_after and report["ok"]:
        released = release_lease(repo)
        step("release", {"ok": released, "released": released})

    return report


def operator_ship_hint(repo: Path) -> str | None:
    """One-line ship command for OPERATOR_STATUS when scoped dirty work exists."""
    repo = repo.resolve()
    dirty = _dirty_paths(repo)
    if not dirty:
        return None

    lease = load_lease(repo)
    globs = _normalize_globs((lease or {}).get("path_globs"))
    forbidden = _normalize_globs((lease or {}).get("forbidden_globs"))
    scoped = scoped_dirty_paths(
        repo,
        path_globs=globs if globs else ["**"],
        forbidden_globs=forbidden,
    )
    if not scoped:
        return None

    try:
        from scripts.ppe_delegation_envelope import classify_paths, current_branch

        verdict = classify_paths(repo, scoped, branch=current_branch(repo))
        if verdict.tier == "human_only":
            return None
    except Exception:
        pass

    if lease and _lease_active(lease):
        return "python scripts/ppe_worker_lease.py --ship --release"

    branch = _current_branch(repo)
    if branch in ("main", "master", ""):
        from scripts.ppe_branch_recovery import recovery_ship_command

        return recovery_ship_command(plane="control")

    try:
        from scripts.ppe_branch_recovery import needs_branch_recovery, recovery_ship_command

        if needs_branch_recovery(repo, scoped):
            plane = "product" if any(p.startswith(("src/", "apps/")) for p in scoped) else "control"
            return recovery_ship_command(plane=plane)
    except Exception:
        pass

    return "python scripts/run_pushable_gate.py → commit → push → PR (see AGENTS.md)"


def format_ship_hint_lines(hint: str | None) -> list[str]:
    if not hint:
        return []
    return [
        "",
        "**Ship (agent — do not ask operator):**",
        f"  → `{hint}`",
    ]


def format_lease_lines(assessment: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lane = assessment.get("suggested_lane")
    if not lane:
        return lines

    pref = assessment.get("lane_preference") if isinstance(assessment.get("lane_preference"), dict) else {}
    reason = pref.get("reason")
    lines.append("")
    lines.append(f"**Worker lane:** `{lane}`" + (f" ({reason})" if reason else ""))

    if assessment.get("blocks_dispatch"):
        lines.append("  **Lease: BLOCKS dispatch**")
        for r in assessment.get("reasons") or []:
            lines.append(f"  - {r}")
        lines.append("  → docs/SOP/WORKER_LANE_POLICY_V1.md — release, re-acquire, or checkout lease branch")
    elif assessment.get("expired"):
        lines.append("  Lease expired — re-acquire before multi-agent BUILD")
    elif assessment.get("active"):
        lease = assessment.get("lease") if isinstance(assessment.get("lease"), dict) else {}
        holder = lease.get("worker_id") or "?"
        lines.append(f"  Active lease: `{holder}` on `{lease.get('branch')}`")

    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Multi-agent worker lease assess / acquire / dispatch.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--write-dispatch", action="store_true")
    ap.add_argument("--infer-events", action="store_true", help=f"Write {WORKER_EVENTS_REL}")
    ap.add_argument(
        "--prepare-desktop-build",
        action="store_true",
        help=f"DESKTOP_BUILD: auto-acquire lease + write {WORK_DISPATCH_REL}",
    )
    ap.add_argument("--release", action="store_true")
    ap.add_argument("--ship", action="store_true", help="Gate → commit → push → PR for lease-scoped dirty paths")
    ap.add_argument("--dry-run", action="store_true", help="With --ship: plan paths only, no git writes")
    ap.add_argument("--pre-push", action="store_true", help="With --ship: run full pre-push gate")
    ap.add_argument("--message", type=str, default=None, help="With --ship: commit message override")
    ap.add_argument("--acquire", action="store_true")
    ap.add_argument("--worker", type=str, default=LANE_CODEX)
    ap.add_argument("--branch", type=str, default=None)
    ap.add_argument("--paths", nargs="*", default=None)
    ap.add_argument("--forbid", nargs="*", default=None)
    ap.add_argument("--ttl-hours", type=float, default=2.0)
    ap.add_argument("--notes", type=str, default=None)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()

    if args.release and not args.ship:
        released = release_lease(repo)
        print(json.dumps({"released": released}) if args.json else f"ppe_worker_lease: released={released}")
        return 0

    if args.ship:
        report = ship_lease_work(
            repo,
            dry_run=args.dry_run,
            release_after=args.release and not args.dry_run,
            message=args.message,
            pre_push=args.pre_push,
            path_globs=args.paths,
            forbidden_globs=args.forbid,
            branch=args.branch,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            status = "ok" if report.get("ok") else "blocked"
            extra = report.get("pr_url") or report.get("reason") or report.get("skipped")
            print(f"ppe_worker_lease: ship {status} {extra or ''}".strip())
        return 0 if report.get("ok") and not report.get("blocked") else 1

    if args.acquire:
        try:
            lease = acquire_lease(
                repo,
                worker_id=args.worker,
                branch=args.branch,
                path_globs=args.paths,
                forbidden_globs=args.forbid,
                ttl_hours=args.ttl_hours,
                notes=args.notes,
            )
        except RuntimeError as exc:
            print(f"ppe_worker_lease: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(lease, indent=2) if args.json else f"ppe_worker_lease: acquired {lease['lease_id']}")
        return 0

    if args.write_dispatch:
        dispatch = build_work_dispatch(repo)
        path = write_work_dispatch(repo)
        print(json.dumps(dispatch, indent=2) if args.json else f"ppe_worker_lease: wrote {path.relative_to(repo)}")
        return 0

    if args.prepare_desktop_build:
        record = prepare_desktop_build_handoff(repo)
        if args.json:
            print(json.dumps(record, indent=2))
        else:
            lane = record.get("preferred_lane")
            hw = record.get("handoff_worker")
            pref = record.get("lane_preference") or {}
            reason = pref.get("reason") if isinstance(pref, dict) else None
            print(f"ppe_worker_lease: DESKTOP_BUILD lane={lane} handoff={hw} reason={reason}")
            if record.get("blocked"):
                for r in record.get("reasons") or []:
                    print(f"  BLOCKED: {r}")
            elif record.get("dispatch_uri"):
                print(f"  dispatch: {record['dispatch_uri']}")
        return 1 if record.get("blocked") else 0

    if args.infer_events:
        payload = infer_worker_events(repo)
        path = write_worker_events(repo)
        print(json.dumps(payload, indent=2) if args.json else f"ppe_worker_lease: wrote {path.relative_to(repo)}")
        return 0

    assessment = assess_worker_lease(repo)
    if args.json:
        print(json.dumps(assessment, indent=2))
    else:
        print(
            f"ppe_worker_lease: lane={assessment.get('suggested_lane')} "
            f"active={assessment.get('active')} blocks={assessment.get('blocks_dispatch')}"
        )
    return 1 if assessment.get("blocks_dispatch") else 0


if __name__ == "__main__":
    raise SystemExit(main())
