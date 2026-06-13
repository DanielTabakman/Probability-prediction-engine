"""Insert a chartered chapter into roadmap + queue immediately after an anchor plan.

Use when steward/agent needs relative RUN order without changing backlog priority tiers.
Canonical field on backlog rows: ``queueAfterPlanPath`` (see BACKLOG_OPERATOR.md).

Example::

    python scripts/ppe_queue_insert_after.py \\
      --chapter-id mvp1_bl_density_smoothing_v1 \\
      --after-plan docs/SOP/PHASE_PLANS/mvp1_distribution_quant_research_v2_relay.json \\
      --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ppe_manifest import load_phase_plan, validate_phase_plan
from scripts.ppe_propagate_queue import load_backlog, save_backlog
from scripts.ppe_queue import load_queue, save_queue
from scripts.ppe_roadmap import (
    ROADMAP_REL,
    load_roadmap,
    norm_plan,
    roadmap_path,
    save_roadmap,
    sync_roadmap_to_queue,
)

BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"


def _find_backlog_item(backlog: dict[str, Any], chapter_id: str) -> dict[str, Any] | None:
    for item in backlog.get("items") or []:
        if isinstance(item, dict) and str(item.get("chapterId") or "") == chapter_id:
            return item
    return None


def _index_by_plan(items: list[Any], plan_path: str) -> int | None:
    norm = norm_plan(plan_path)
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if norm_plan(str(item.get("planPath") or "")) == norm:
            return i
    return None


def _remove_plan_rows(items: list[Any], plan_path: str) -> list[Any]:
    norm = norm_plan(plan_path)
    return [
        item
        for item in items
        if not (isinstance(item, dict) and norm_plan(str(item.get("planPath") or "")) == norm)
    ]


def _roadmap_row_from_backlog(item: dict[str, Any], plan_path: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        "planPath": plan_path,
        "status": "pending",
        "reason": str(item.get("reason") or "backlog relative insert"),
    }
    sel = str(item.get("selectionRecord") or item.get("selectionPrep") or "").strip()
    if sel:
        row["selectionPrep"] = sel
    wm = str(item.get("workerMode") or "").strip()
    if wm:
        row["workerMode"] = wm
    return row


def _queue_row_from_roadmap(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "planPath": norm_plan(str(row["planPath"])),
        "status": "PLANNED",
        "reason": str(row.get("reason") or ""),
    }
    if row.get("selectionPrep"):
        out["selectionPrep"] = row["selectionPrep"]
    if row.get("workerMode"):
        out["workerMode"] = row["workerMode"]
    return out


def insert_chapter_after(
    repo_root: Path,
    *,
    chapter_id: str,
    after_plan: str,
    apply: bool,
) -> dict[str, Any]:
    repo = repo_root.resolve()
    backlog = load_backlog(repo)
    item = _find_backlog_item(backlog, chapter_id)
    if item is None:
        raise ValueError(f"backlog chapterId not found: {chapter_id}")

    plan_path = norm_plan(str(item.get("planPath") or ""))
    if not plan_path:
        raise ValueError(f"backlog row {chapter_id} missing planPath — charter relay plan first")

    anchor = norm_plan(after_plan)
    if not anchor:
        raise ValueError("after_plan is required")

    plan_fs = repo / plan_path
    if not plan_fs.is_file():
        raise ValueError(f"plan not found: {plan_path}")
    plan = load_phase_plan(repo, plan_path)
    errors = validate_phase_plan(plan)
    if errors:
        raise ValueError("plan invalid: " + "; ".join(errors))

    anchor_fs = repo / anchor
    if not anchor_fs.is_file():
        raise ValueError(f"anchor plan not found: {anchor}")

    if not roadmap_path(repo).is_file():
        raise FileNotFoundError(f"Missing roadmap: {ROADMAP_REL}")

    roadmap = load_roadmap(repo)
    roadmap_items = roadmap.get("items") or []
    if not isinstance(roadmap_items, list):
        raise ValueError("roadmap items must be an array")

    anchor_idx = _index_by_plan(roadmap_items, anchor)
    if anchor_idx is None:
        raise ValueError(f"anchor plan not on roadmap: {anchor}")

    new_roadmap_row = _roadmap_row_from_backlog(item, plan_path)
    roadmap_items = _remove_plan_rows(roadmap_items, plan_path)
    anchor_idx = _index_by_plan(roadmap_items, anchor)
    if anchor_idx is None:
        raise ValueError(f"anchor plan not on roadmap after cleanup: {anchor}")
    roadmap_items.insert(anchor_idx + 1, new_roadmap_row)
    roadmap["items"] = roadmap_items

    queue = load_queue(repo)
    queue_items = queue.get("items") or []
    if not isinstance(queue_items, list):
        raise ValueError("queue items must be an array")
    queue_items = _remove_plan_rows(queue_items, plan_path)
    anchor_q_idx = _index_by_plan(queue_items, anchor)
    if anchor_q_idx is None:
        raise ValueError(f"anchor plan not on queue: {anchor}")
    queue_items.insert(anchor_q_idx + 1, _queue_row_from_roadmap(new_roadmap_row))
    queue["items"] = queue_items

    item["queueAfterPlanPath"] = anchor
    item["status"] = "chartered"
    if not str(item.get("selectionRecord") or "").strip() and new_roadmap_row.get("selectionPrep"):
        item["selectionRecord"] = new_roadmap_row["selectionPrep"]

    result: dict[str, Any] = {
        "chapterId": chapter_id,
        "planPath": plan_path,
        "afterPlanPath": anchor,
        "roadmapIndex": anchor_idx + 1,
        "queueIndex": anchor_q_idx + 1,
        "apply": apply,
    }

    if not apply:
        result["dry_run"] = True
        return result

    save_roadmap(repo, roadmap)
    save_queue(repo, queue)
    save_backlog(repo, backlog)
    sync_roadmap_to_queue(repo, apply=True)
    result["synced"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Insert backlog chapter on roadmap+queue after anchor plan")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--chapter-id", required=True)
    ap.add_argument(
        "--after-plan",
        required=True,
        help="planPath of chapter that must complete before this one runs next",
    )
    ap.add_argument("--apply", action="store_true", help="Write roadmap, queue, and backlog")
    args = ap.parse_args(argv)

    try:
        out = insert_chapter_after(
            args.repo_root.resolve(),
            chapter_id=args.chapter_id,
            after_plan=args.after_plan,
            apply=args.apply,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"ppe_queue_insert_after: ERROR: {exc}", file=sys.stderr)
        return 1

    mode = "applied" if args.apply else "dry-run"
    print(
        f"ppe_queue_insert_after: {mode} chapter={out['chapterId']} "
        f"plan={out['planPath']} after={out['afterPlanPath']} "
        f"roadmap[{out['roadmapIndex']}] queue[{out['queueIndex']}]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
