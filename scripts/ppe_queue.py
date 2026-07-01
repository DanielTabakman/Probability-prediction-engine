"""PHASE_QUEUE.json helpers (shared by auto-select and post-relay closeout)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"


def queue_path(repo_root: Path) -> Path:
    return (repo_root / QUEUE_REL).resolve()


def load_queue(repo_root: Path) -> dict[str, Any]:
    p = queue_path(repo_root)
    if not p.is_file():
        raise FileNotFoundError(f"Missing queue file: {QUEUE_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_queue(repo_root: Path, queue: dict[str, Any]) -> None:
    p = queue_path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")


def mark_queue_item_done(
    repo_root: Path,
    *,
    plan_path: str,
    done_reason: str = "marked DONE by post_relay_continue (chapter closeout)",
) -> tuple[bool, str]:
    """Mark the first matching queue item as DONE."""
    queue = load_queue(repo_root)
    raw_items = queue.get("items")
    if isinstance(raw_items, list):
        items = raw_items
    else:
        items = []
        queue["items"] = items

    norm = plan_path.replace("\\", "/").strip()
    marked: list[int] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_plan = str(item.get("planPath") or "").replace("\\", "/").strip()
        if item_plan != norm:
            continue
        if str(item.get("status") or "").upper() == "DONE":
            marked.append(i)
            continue
        item["status"] = "DONE"
        prev = str(item.get("doneReason") or "").strip()
        if not prev:
            item["doneReason"] = done_reason
        queue["items"][i] = item
        marked.append(i)

    if marked:
        save_queue(repo_root, queue)
        if len(marked) == 1:
            return True, f"queue item {marked[0]} marked DONE"
        return True, f"queue items {marked} marked DONE ({len(marked)} duplicates)"

    return False, "no matching planPath in queue"


def find_queue_item_index(queue: dict[str, Any], plan_path: str) -> int | None:
    norm = plan_path.replace("\\", "/").strip()
    for i, item in enumerate(queue.get("items") or []):
        if not isinstance(item, dict):
            continue
        if str(item.get("planPath") or "").replace("\\", "/").strip() == norm:
            return i
    return None


def upsert_queue_item(
    repo_root: Path,
    *,
    plan_path: str,
    status: str,
    **fields: Any,
) -> tuple[bool, str]:
    """Insert or update a queue row by planPath."""
    queue = load_queue(repo_root)
    raw_items = queue.get("items")
    if isinstance(raw_items, list):
        items = raw_items
    else:
        items = []
        queue["items"] = items

    norm = plan_path.replace("\\", "/").strip()
    idx = find_queue_item_index(queue, norm)
    was_ready = (
        idx is not None
        and str(items[idx].get("status") or "").strip().upper() == "READY"
    )
    row: dict[str, Any] = {"planPath": norm, "status": status.upper()}
    for key, val in fields.items():
        if val is not None and val != "":
            row[key] = val

    if idx is None:
        items.append(row)
        item_idx = len(items) - 1
    else:
        prev = items[idx]
        prev.update(row)
        items[idx] = prev
        item_idx = idx
    queue["items"] = items
    save_queue(repo_root, queue)

    msg = (
        f"queue item {item_idx} created ({status})"
        if idx is None
        else f"queue item {item_idx} updated ({status})"
    )
    if status.upper() == "READY" and not was_ready:
        try:
            from scripts.ppe_ide_build_starter import regenerate_starters_for_plan

            regen = regenerate_starters_for_plan(repo_root, norm)
            if regen:
                msg += f"; regen starters: {', '.join(regen)}"
        except Exception as exc:
            print(f"ppe_queue: starter regen skipped: {exc}", file=sys.stderr)
    return True, msg
