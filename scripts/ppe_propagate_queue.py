"""Propagate PHASE_CHAPTER_BACKLOG.json → PHASE_SELECTION_ROADMAP + PHASE_QUEUE."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from scripts.ppe_roadmap import (
    ROADMAP_REL,
    _plan_valid,
    load_roadmap,
    norm_plan,
    roadmap_enabled,
    roadmap_path,
    save_roadmap,
    sync_roadmap_to_queue,
)
from scripts.ppe_queue import upsert_queue_item

BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
VALID_BACKLOG_STATUSES = frozenset({"queued", "chartered", "done", "blocked", "skipped"})


def backlog_enabled(repo_root: Path | None = None) -> bool:
    if repo_root is not None:
        from scripts.ppe_operator_config import propagate_backlog_enabled

        return propagate_backlog_enabled(repo_root.resolve())
    env = os.environ.get("PPE_AUTO_PROPAGATE_QUEUE", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    return True


def backlog_path(repo_root: Path) -> Path:
    return (repo_root / BACKLOG_REL).resolve()


def load_backlog(repo_root: Path) -> dict[str, Any]:
    p = backlog_path(repo_root)
    if not p.is_file():
        raise FileNotFoundError(f"Missing backlog: {BACKLOG_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_backlog(repo_root: Path, backlog: dict[str, Any]) -> None:
    p = backlog_path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")


def _roadmap_plan_statuses(roadmap: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if plan:
            out[plan] = str(item.get("status") or "").strip().lower()
    return out


def sync_backlog_from_roadmap(repo_root: Path, *, apply: bool) -> list[dict[str, Any]]:
    """Align backlog chartered/done with roadmap rows."""
    repo = repo_root.resolve()
    if not backlog_path(repo).is_file() or not roadmap_path(repo).is_file():
        return []
    backlog = load_backlog(repo)
    roadmap = load_roadmap(repo)
    by_plan = _roadmap_plan_statuses(roadmap)
    changes: list[dict[str, Any]] = []
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if not plan or plan not in by_plan:
            continue
        rs = by_plan[plan]
        prev = str(item.get("status") or "").strip().lower()
        if rs == "done" and prev != "done":
            if apply:
                item["status"] = "done"
            changes.append({"chapterId": item.get("chapterId"), "status": "done", "planPath": plan})
        elif rs in ("pending", "ready") and prev == "queued":
            if apply:
                item["status"] = "chartered"
            changes.append({"chapterId": item.get("chapterId"), "status": "chartered", "planPath": plan})
    if apply and changes:
        save_backlog(repo, backlog)
    return changes


def _first_queued_item(backlog: dict[str, Any]) -> dict[str, Any] | None:
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() == "queued":
            return item
    return None


_TERMINAL_BACKLOG = frozenset({"done", "skipped"})


def _prior_backlog_items_terminal(items: list[Any], index: int) -> bool:
    """True when every backlog row before index is done or skipped."""
    for prior in items[:index]:
        if not isinstance(prior, dict):
            continue
        prev = str(prior.get("status") or "").strip().lower()
        if prev not in _TERMINAL_BACKLOG:
            return False
    return True


def promote_first_blocked_with_plan(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Promote the first blocked backlog row with a valid planPath when all prior rows are done/skipped."""
    repo = repo_root.resolve()
    if not backlog_enabled(repo):
        return {"promoted": False, "reason": "PPE_AUTO_PROPAGATE_QUEUE disabled"}
    if not backlog_path(repo).is_file():
        return {"promoted": False, "reason": "no backlog file"}

    backlog = load_backlog(repo)
    items = backlog.get("items") or []
    if not isinstance(items, list):
        return {"promoted": False, "reason": "invalid backlog items"}

    if _first_queued_item(backlog) is not None:
        return {"promoted": False, "reason": "queued backlog item already exists"}

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() != "blocked":
            continue
        plan_path = norm_plan(str(item.get("planPath") or ""))
        if not plan_path:
            continue
        if not _prior_backlog_items_terminal(items, index):
            return {
                "promoted": False,
                "reason": "prior backlog chapters not terminal",
                "chapterId": item.get("chapterId"),
            }
        ok, err = _plan_valid(repo, plan_path)
        if not ok:
            return {
                "promoted": False,
                "reason": f"plan invalid: {err}",
                "planPath": plan_path,
                "chapterId": item.get("chapterId"),
            }
        if not apply:
            return {
                "promoted": True,
                "dry_run": True,
                "planPath": plan_path,
                "chapterId": item.get("chapterId"),
            }
        item["status"] = "queued"
        save_backlog(repo, backlog)
        return {
            "promoted": True,
            "planPath": plan_path,
            "chapterId": item.get("chapterId"),
        }

    return {"promoted": False, "reason": "no blocked backlog item with planPath"}


def _plan_on_roadmap(roadmap: dict[str, Any], plan_path: str) -> bool:
    norm = norm_plan(plan_path)
    return any(
        isinstance(it, dict) and norm_plan(str(it.get("planPath") or "")) == norm
        for it in (roadmap.get("items") or [])
    )


def propagate_from_backlog(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Append first queued backlog row to roadmap as pending (with optional scaffold)."""
    repo = repo_root.resolve()
    if not backlog_enabled(repo):
        return {"propagated": False, "reason": "PPE_AUTO_PROPAGATE_QUEUE disabled"}
    if not backlog_path(repo).is_file():
        return {"propagated": False, "reason": "no backlog file"}
    if not roadmap_enabled(repo):
        return {"propagated": False, "reason": "roadmap disabled"}

    sync_backlog_from_roadmap(repo, apply=apply)
    backlog = load_backlog(repo)
    item = _first_queued_item(backlog)
    if item is None:
        promoted = promote_first_blocked_with_plan(repo, apply=apply)
        if promoted.get("promoted"):
            sync_backlog_from_roadmap(repo, apply=apply)
            backlog = load_backlog(repo)
            item = _first_queued_item(backlog)
        if item is None:
            out: dict[str, Any] = {"propagated": False, "reason": "no queued backlog item"}
            if promoted.get("promoted") or promoted.get("reason"):
                out["promote"] = promoted
            return out

    plan_path = norm_plan(str(item.get("planPath") or ""))
    if not plan_path:
        return {"propagated": False, "reason": "queued item missing planPath"}

    if roadmap_path(repo).is_file():
        roadmap = load_roadmap(repo)
    else:
        roadmap = {"version": 1, "notes": "Auto from PHASE_CHAPTER_BACKLOG", "items": []}

    if _plan_on_roadmap(roadmap, plan_path):
        if apply:
            item["status"] = "chartered"
            save_backlog(repo, backlog)
        return {"propagated": False, "reason": "plan already on roadmap", "planPath": plan_path}

    if str(item.get("scaffold", False)).lower() in ("1", "true", "yes") or item.get("scaffold") is True:
        if apply:
            from scripts.ppe_steward_cursor import scaffold_chapter_files

            proposal = {
                "chapterId": str(item.get("chapterId") or "chapter"),
                "chapterTitle": str(item.get("chapterTitle") or item.get("chapterId") or "chapter"),
                "planPath": plan_path,
                "sprintSpecPath": item.get("sprintSpecPath"),
                "selectionRecord": item.get("selectionRecord"),
                "evidenceDoc": item.get("evidenceDoc"),
                "workerMode": str(item.get("workerMode") or "deterministic"),
                "scaffold": True,
            }
            scaffold_chapter_files(repo, proposal)

    ok, err = _plan_valid(repo, plan_path)
    if not ok:
        return {"propagated": False, "reason": f"plan invalid: {err}", "planPath": plan_path}

    if not apply:
        return {
            "propagated": True,
            "dry_run": True,
            "planPath": plan_path,
            "chapterId": item.get("chapterId"),
        }

    row = {
        "planPath": plan_path,
        "status": "pending",
        "reason": str(item.get("reason") or "backlog propagation"),
    }
    wm = str(item.get("workerMode") or "").strip()
    if wm:
        row["workerMode"] = wm
    sel = str(item.get("selectionRecord") or item.get("selectionPrep") or "").strip()
    if sel:
        row["selectionPrep"] = sel

    items = roadmap.setdefault("items", [])
    if not isinstance(items, list):
        items = []
        roadmap["items"] = items
    items.append(row)
    save_roadmap(repo, roadmap)
    item["status"] = "chartered"
    save_backlog(repo, backlog)
    sync_roadmap_to_queue(repo, apply=True)
    upsert_queue_item(
        repo,
        plan_path=plan_path,
        status="PLANNED",
        reason=row["reason"],
        workerMode=wm or None,
        selectionPrep=sel or None,
    )
    return {
        "propagated": True,
        "planPath": plan_path,
        "chapterId": item.get("chapterId"),
    }


def maybe_propagate_queue(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Hook: sync backlog statuses, propagate first queued row if roadmap has no pending."""
    repo = repo_root.resolve()
    from scripts.ppe_roadmap import _first_pending_with_valid_plan, load_roadmap

    out: dict[str, Any] = {"skipped": False}
    synced = sync_backlog_from_roadmap(repo, apply=apply)
    if synced:
        out["backlog_sync"] = synced

    if roadmap_path(repo).is_file():
        roadmap = load_roadmap(repo)
        if _first_pending_with_valid_plan(repo, roadmap) is not None:
            out["propagated"] = False
            out["reason"] = "roadmap already has valid pending"
            return out
        pending_any = any(
            isinstance(it, dict) and str(it.get("status") or "").lower() == "pending"
            for it in (roadmap.get("items") or [])
        )
        if pending_any:
            out["propagated"] = False
            out["reason"] = "roadmap has pending without valid plan (fix manually)"
            return out

    prop = propagate_from_backlog(repo, apply=apply)
    out.update(prop)
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Propagate PHASE_CHAPTER_BACKLOG to roadmap/queue")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sync-only", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if args.sync_only:
        changes = sync_backlog_from_roadmap(repo, apply=args.apply)
        print(json.dumps({"sync": changes}, indent=2))
        return 0
    out = maybe_propagate_queue(repo, apply=args.apply)
    print(json.dumps(out, indent=2))
    return 0 if out.get("propagated") or out.get("reason") else 0


if __name__ == "__main__":
    raise SystemExit(main())
