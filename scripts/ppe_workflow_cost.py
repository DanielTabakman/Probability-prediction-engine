"""Workflow cost accounting — worker lane tags and auto slice-close recording."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_slice_worker_mode import infer_slice_kind, resolve_worker_mode
from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _parse_iso, _read_jsonl

VALID_WORKER_LANES = frozenset(
    {
        "deterministic-local",
        "cursor-cli",
        "codex-cli",
        "manual",
        "acp",
        "local-agent",
    }
)

SOURCE_RELAY_CLOSEOUT = "relay_closeout"
SOURCE_IDE_PRODUCT_READY = "ide_product_ready"


def worker_mode_to_lane(worker_mode: str) -> str:
    mode = (worker_mode or "").strip().lower()
    if mode == "deterministic":
        return "deterministic-local"
    if mode == "acp":
        return "acp"
    if mode == "local-agent":
        return "local-agent"
    return "deterministic-local"


def build_worker_to_lane(worker: str) -> str:
    kind = (worker or "").strip().lower()
    if kind in VALID_WORKER_LANES:
        return kind
    if kind in ("cursor", "cursor-cli"):
        return "cursor-cli"
    if kind in ("codex", "codex-cli"):
        return "codex-cli"
    if kind == "manual":
        return "manual"
    return "manual"


def default_size_for_slice(slice_id: str, slice_obj: dict[str, Any] | None) -> str:
    if infer_slice_kind(slice_id, slice_obj) == "product":
        return "M"
    return "S"


def default_roundtrips_for_lane(worker_lane: str) -> int:
    return 0 if worker_lane == "deterministic-local" else 1


def slice_already_recorded(repo: Path, slice_id: str) -> bool:
    rows = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
    return any(str(row.get("slice_id") or "") == slice_id for row in rows)


def _slice_obj_from_plan(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and str(sl.get("sliceId") or "") == slice_id:
            return sl
    return None


def infer_relay_worker_lane(
    repo: Path,
    *,
    slice_id: str,
    plan: dict[str, Any] | None = None,
    slice_obj: dict[str, Any] | None = None,
) -> str:
    sl = slice_obj if slice_obj is not None else (_slice_obj_from_plan(plan, slice_id) if plan else None)
    return worker_mode_to_lane(resolve_worker_mode(slice_id=slice_id, slice_obj=sl))


def infer_ide_worker_lane(repo: Path) -> str:
    lock_path = repo / "artifacts" / "orchestrator" / "REMOTE_BUILD_LOCK.json"
    if lock_path.is_file():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8-sig"))
            if isinstance(lock, dict):
                worker = str(lock.get("build_worker") or "").strip()
                if worker:
                    return build_worker_to_lane(worker)
        except (OSError, json.JSONDecodeError):
            pass
    try:
        from scripts.ppe_build_worker import resolve_build_worker

        return build_worker_to_lane(str(resolve_build_worker(repo, for_handoff=True).get("worker") or "manual"))
    except ImportError:
        return "manual"


def slices_in_window(repo: Path, *, days: int) -> list[dict[str, Any]]:
    rows = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
    if days <= 0:
        return rows
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    return [
        row
        for row in rows
        if (t := _parse_iso(str(row.get("completed_at") or ""))) and t.timestamp() >= cutoff
    ]


def summarize_by_lane(repo: Path, *, days: int = 7) -> dict[str, Any]:
    rows = slices_in_window(repo, days=days)
    by_lane: dict[str, int] = {}
    api_calls = 0
    roundtrips: list[int] = []
    for row in rows:
        lane = str(row.get("worker_lane") or "unspecified").strip() or "unspecified"
        by_lane[lane] = by_lane.get(lane, 0) + 1
        if row.get("api_calls") is not None:
            api_calls += int(row.get("api_calls") or 0)
        if row.get("roundtrips") is not None:
            roundtrips.append(int(row.get("roundtrips") or 0))
    return {
        "days": days,
        "slices_logged": len(rows),
        "by_lane": dict(sorted(by_lane.items(), key=lambda kv: (-kv[1], kv[0]))),
        "api_calls_total": api_calls,
        "avg_roundtrips": (sum(roundtrips) / len(roundtrips)) if roundtrips else 0.0,
    }


def format_lane_summary_line(summary: dict[str, Any]) -> str:
    by_lane = summary.get("by_lane") or {}
    if not by_lane:
        return "Cost lanes (7d): no slices logged yet."
    parts = [f"{lane}={count}" for lane, count in by_lane.items()]
    avg_rt = float(summary.get("avg_roundtrips") or 0.0)
    return f"Cost lanes ({summary.get('days', 7)}d): {', '.join(parts)} | avg_roundtrips={avg_rt:.1f}"


def maybe_record_slice_close(
    repo: Path,
    *,
    slice_id: str,
    source: str,
    worker_lane: str | None = None,
    size: str | None = None,
    roundtrips: int | None = None,
    api_calls: int | None = None,
    notes: str = "",
    plan: dict[str, Any] | None = None,
    slice_obj: dict[str, Any] | None = None,
) -> bool:
    if slice_already_recorded(repo, slice_id):
        return False

    lane = (worker_lane or "").strip() or infer_relay_worker_lane(
        repo, slice_id=slice_id, plan=plan, slice_obj=slice_obj
    )
    sl = slice_obj if slice_obj is not None else (_slice_obj_from_plan(plan, slice_id) if plan else None)
    size_u = (size or default_size_for_slice(slice_id, sl)).upper()
    rt = default_roundtrips_for_lane(lane) if roundtrips is None else roundtrips
    merged_notes = " | ".join(p for p in (notes.strip(), f"source={source}") if p)

    from scripts.workflow_metrics_cli import append_slice_close_row

    append_slice_close_row(
        repo,
        slice_id=slice_id,
        size=size_u,
        roundtrips=rt,
        worker_lane=lane,
        api_calls=api_calls,
        source=source,
        notes=merged_notes,
    )
    return True


def record_relay_closeout(repo: Path, *, slice_id: str, plan_path: Path | str) -> bool:
    try:
        from scripts.ppe_manifest import load_phase_plan

        plan = load_phase_plan(repo, str(plan_path))
    except Exception:
        plan = {}
    try:
        return maybe_record_slice_close(
            repo,
            slice_id=slice_id,
            source=SOURCE_RELAY_CLOSEOUT,
            plan=plan if isinstance(plan, dict) else {},
        )
    except Exception as exc:
        print(f"ppe_workflow_cost: relay record skipped ({exc})")
        return False


def record_ide_product_ready(repo: Path, *, slice_id: str) -> bool:
    try:
        lane = infer_ide_worker_lane(repo)
        api = 1 if lane in ("cursor-cli", "codex-cli", "acp") else None
        return maybe_record_slice_close(
            repo,
            slice_id=slice_id,
            source=SOURCE_IDE_PRODUCT_READY,
            worker_lane=lane,
            size="M",
            api_calls=api,
        )
    except Exception as exc:
        print(f"ppe_workflow_cost: IDE record skipped ({exc})")
        return False
