"""Window large phase plans into bounded slice batches for unattended relay runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import load_operator_config

PROGRESS_REL = "artifacts/orchestrator/PHASE_SLICE_PROGRESS.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_plan(path: str) -> str:
    return path.replace("\\", "/").strip()


def _ide_marker_completed_slices(repo: Path, plan_path: str) -> set[str]:
    """Product slices marked IDE-ready for this plan (skip re-run in relay batch)."""
    norm = _norm_plan(plan_path)
    try:
        from scripts.ppe_ide_product_ready import load_marker
    except ImportError:
        return set()
    marker = load_marker(repo)
    if not marker:
        return set()
    marker_plan = _norm_plan(str(marker.get("phasePlanPath") or ""))
    if marker_plan and marker_plan != norm:
        return set()
    out: set[str] = set()
    for sid in marker.get("completedProductSlices") or []:
        s = str(sid or "").strip()
        if s:
            out.add(s)
    return out


def progress_path(repo: Path) -> Path:
    return (repo / PROGRESS_REL).resolve()


def load_progress(repo: Path) -> dict[str, Any]:
    p = progress_path(repo)
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_progress(repo: Path, data: dict[str, Any]) -> None:
    p = progress_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def phase_slice_batching_enabled(repo: Path) -> bool:
    cfg = load_operator_config(repo)
    g = cfg.get("guards") if isinstance(cfg.get("guards"), dict) else {}
    if g.get("phaseSliceBatching") is False:
        return False
    if cfg.get("phaseSliceBatching") is False:
        return False
    return bool(cfg.get("phaseSliceBatching", g.get("phaseSliceBatching", True)))


def slice_batch_limit(repo: Path) -> int:
    cfg = load_operator_config(repo)
    g = cfg.get("guards") if isinstance(cfg.get("guards"), dict) else {}
    raw = g.get("maxPhaseSlices", cfg.get("maxPhaseSlices", 6))
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 6


def _is_closeout_slice(sl: dict[str, Any]) -> bool:
    return isinstance(sl.get("closeout"), dict)


def completed_slice_ids(repo: Path, plan_path: str) -> set[str]:
    norm = _norm_plan(plan_path)
    out: set[str] = set()
    try:
        plan = load_phase_plan(repo, plan_path)
        for sid in plan.get("preCompletedSliceIds") or []:
            s = str(sid or "").strip()
            if s:
                out.add(s)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        pass
    data = load_progress(repo)
    if _norm_plan(str(data.get("planPath") or "")) == norm:
        for sid in data.get("completedSliceIds") or []:
            s = str(sid or "").strip()
            if s:
                out.add(s)
    out.update(_ide_marker_completed_slices(repo, plan_path))
    return out


def mark_slice_complete(repo: Path, plan_path: str, slice_id: str) -> None:
    norm = _norm_plan(plan_path)
    sid = str(slice_id or "").strip()
    if not sid:
        return
    data = load_progress(repo)
    if _norm_plan(str(data.get("planPath") or "")) != norm:
        data = {"planPath": norm, "completedSliceIds": []}
    done = [str(x).strip() for x in (data.get("completedSliceIds") or []) if str(x).strip()]
    if sid not in done:
        done.append(sid)
    data["planPath"] = norm
    data["completedSliceIds"] = done
    data["updatedAt"] = _utc_now()
    save_progress(repo, data)
    try:
        from scripts.ppe_operator_daily_metrics import record_slice_completed

        record_slice_completed(repo, slice_id=sid, plan_path=norm)
    except ImportError:
        pass


def clear_progress(repo: Path, plan_path: str) -> None:
    norm = _norm_plan(plan_path)
    data = load_progress(repo)
    if _norm_plan(str(data.get("planPath") or "")) == norm:
        progress_path(repo).unlink(missing_ok=True)


def select_slice_batch(all_slices: list[dict[str, Any]], *, limit: int, completed: set[str]) -> list[dict[str, Any]]:
    """Return the next batch of slices (order preserved), deferring closeout if batch is full."""
    remaining: list[dict[str, Any]] = []
    for sl in all_slices:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if not sid or sid in completed:
            continue
        remaining.append(sl)
    if not remaining:
        return []

    batch: list[dict[str, Any]] = []
    idx = 0
    while idx < len(remaining) and len(batch) < limit:
        sl = remaining[idx]
        if _is_closeout_slice(sl):
            non_closeout_after = any(
                not _is_closeout_slice(x) for x in remaining[idx + 1 :]
            )
            if non_closeout_after:
                idx += 1
                continue
        batch.append(sl)
        idx += 1
    return batch


def active_slice_window(repo: Path, plan_path: str) -> list[dict[str, Any]]:
    plan = load_phase_plan(repo, plan_path)
    slices = [sl for sl in (plan.get("slices") or []) if isinstance(sl, dict)]
    completed = completed_slice_ids(repo, plan_path)
    return select_slice_batch(slices, limit=slice_batch_limit(repo), completed=completed)


def windowed_phase_plan(repo: Path, plan_path: str) -> dict[str, Any]:
    """Full plan metadata with only the active slice batch."""
    plan = load_phase_plan(repo, plan_path)
    batch = active_slice_window(repo, plan_path)
    out = dict(plan)
    out["slices"] = batch
    out["_sliceBatch"] = {
        "enabled": phase_slice_batching_enabled(repo),
        "limit": slice_batch_limit(repo),
        "batchSize": len(batch),
        "completedCount": len(completed_slice_ids(repo, plan_path)),
        "totalSlices": len(plan.get("slices") or []),
    }
    return out


def plan_slice_count(repo: Path, plan_path: str) -> int:
    plan = load_phase_plan(repo, plan_path)
    return sum(
        1
        for sl in (plan.get("slices") or [])
        if isinstance(sl, dict) and str(sl.get("sliceId") or "").strip()
    )


def effective_slice_count_for_guard(repo: Path, plan_path: str) -> int:
    if phase_slice_batching_enabled(repo):
        return len(active_slice_window(repo, plan_path))
    return plan_slice_count(repo, plan_path)
