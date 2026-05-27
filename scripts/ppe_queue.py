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
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_plan = str(item.get("planPath") or "").replace("\\", "/").strip()
        if item_plan != norm:
            continue
        item["status"] = "DONE"
        prev = str(item.get("doneReason") or "").strip()
        if not prev:
            item["doneReason"] = done_reason
        queue["items"][i] = item
        save_queue(repo_root, queue)
        return True, f"queue item {i} marked DONE"

    return False, "no matching planPath in queue"
