"""PHASE_QUEUE.json helpers (shared by auto-select and post-relay closeout)."""

from __future__ import annotations

import json
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
    items = queue.get("items") or []
    if not isinstance(items, list):
        raise ValueError("queue: items must be an array")

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
    items = queue.get("items") or []
    if not isinstance(items, list):
        raise ValueError("queue: items must be an array")

    norm = plan_path.replace("\\", "/").strip()
    idx = find_queue_item_index(queue, norm)
    row: dict[str, Any] = {"planPath": norm, "status": status.upper()}
    for key, val in fields.items():
        if val is not None and val != "":
            row[key] = val

    if idx is None:
        items.append(row)
        save_queue(repo_root, queue)
        return True, f"queue item {len(items) - 1} created ({status})"

    prev = items[idx]
    prev.update(row)
    items[idx] = prev
    queue["items"] = items
    save_queue(repo_root, queue)
    return True, f"queue item {idx} updated ({status})"


def list_ready_queue_items(repo_root: Path, *, limit: int = 3) -> list[dict[str, Any]]:
    """First N READY queue rows in file order."""
    queue = load_queue(repo_root)
    ready: list[dict[str, Any]] = []
    cap = max(1, limit)
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").upper() != "READY":
            continue
        plan = str(item.get("planPath") or "").replace("\\", "/").strip()
        if not plan:
            continue
        ready.append(
            {
                "planPath": plan,
                "reason": str(item.get("reason") or "").strip() or None,
                "workerMode": str(item.get("workerMode") or "").strip() or None,
            }
        )
        if len(ready) >= cap:
            break
    return ready
