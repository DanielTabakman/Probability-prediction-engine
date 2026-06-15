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
from scripts.ppe_queue_health import chapter_marked_complete_in_repo, finalize_chapter_evidence_complete

BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
VALID_BACKLOG_STATUSES = frozenset({"queued", "chartered", "done", "blocked", "skipped"})
VALID_BACKLOG_PRIORITIES = frozenset({"high", "medium", "low"})
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
_DEFAULT_BACKLOG_PRIORITY = "medium"


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


def _queue_done_plans(repo_root: Path) -> set[str]:
    from scripts.ppe_queue import load_queue

    queue = load_queue(repo_root)
    done: set[str] = set()
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().upper() != "DONE":
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if plan:
            done.add(plan)
    return done


def sync_backlog_from_queue(repo_root: Path, *, apply: bool) -> list[dict[str, Any]]:
    """Mark backlog rows done when PHASE_QUEUE shows DONE (closeout drift repair)."""
    repo = repo_root.resolve()
    if not backlog_path(repo).is_file():
        return []
    done_plans = _queue_done_plans(repo)
    if not done_plans:
        return []
    backlog = load_backlog(repo)
    changes: list[dict[str, Any]] = []
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if not plan or plan not in done_plans:
            continue
        prev = str(item.get("status") or "").strip().lower()
        if prev != "done":
            if apply:
                item["status"] = "done"
            changes.append({"chapterId": item.get("chapterId"), "status": "done", "planPath": plan, "source": "queue"})
    if apply and changes:
        save_backlog(repo, backlog)
    return changes


def sync_roadmap_from_queue(repo_root: Path, *, apply: bool) -> list[dict[str, Any]]:
    """Mark roadmap rows done when PHASE_QUEUE shows DONE (closeout drift repair)."""
    repo = repo_root.resolve()
    if not roadmap_path(repo).is_file():
        return []
    done_plans = _queue_done_plans(repo)
    if not done_plans:
        return []
    roadmap = load_roadmap(repo)
    changes: list[dict[str, Any]] = []
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if not plan or plan not in done_plans:
            continue
        prev = str(item.get("status") or "").strip().lower()
        if prev != "done":
            if apply:
                item["status"] = "done"
            changes.append({"planPath": plan, "status": "done", "source": "queue"})
    if apply and changes:
        save_roadmap(repo, roadmap)
    return changes


def reconcile_closed_chapters(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Repair backlog/roadmap drift when queue already marks chapters DONE."""
    backlog_q = sync_backlog_from_queue(repo_root, apply=apply)
    roadmap_q = sync_roadmap_from_queue(repo_root, apply=apply)
    backlog_r = sync_backlog_from_roadmap(repo_root, apply=apply)
    return {
        "backlog_from_queue": backlog_q,
        "roadmap_from_queue": roadmap_q,
        "backlog_from_roadmap": backlog_r,
    }


def _backlog_items(backlog: dict[str, Any]) -> list[Any]:
    items = backlog.get("items") or []
    return items if isinstance(items, list) else []


def _backlog_item_status(item: dict[str, Any]) -> str:
    return str(item.get("status") or "").strip().lower()


def normalize_backlog_priority(item: dict[str, Any]) -> str:
    """Return high | medium | low; missing or invalid values default to medium."""
    raw = str(item.get("priority") or _DEFAULT_BACKLOG_PRIORITY).strip().lower()
    return raw if raw in VALID_BACKLOG_PRIORITIES else _DEFAULT_BACKLOG_PRIORITY


def _priority_sort_key(index: int, item: dict[str, Any]) -> tuple[int, int]:
    """Lower rank runs first; array index breaks ties (stable FIFO within tier)."""
    return (PRIORITY_RANK[normalize_backlog_priority(item)], index)


def _pipeline_busy(backlog: dict[str, Any]) -> bool:
    """True when a chapter is already queued or chartered in the backlog pipeline."""
    for item in _backlog_items(backlog):
        if not isinstance(item, dict):
            continue
        if _backlog_item_status(item) in ("chartered", "queued"):
            return True
    return False


def _best_queued_item(backlog: dict[str, Any]) -> dict[str, Any] | None:
    """Highest-priority queued backlog row (high before medium before low)."""
    candidates: list[tuple[int, dict[str, Any]]] = []
    for index, item in enumerate(_backlog_items(backlog)):
        if not isinstance(item, dict):
            continue
        if _backlog_item_status(item) == "queued":
            candidates.append((index, item))
    if not candidates:
        return None
    _index, item = min(candidates, key=lambda pair: _priority_sort_key(pair[0], pair[1]))
    return item


def _focus_gate_blocks(repo: Path, plan_path: str) -> str | None:
    try:
        from scripts.ppe_focus_gate import evaluate_focus_gate

        focus = evaluate_focus_gate(repo, plan_path)
    except ImportError:
        return None
    if focus.allowed:
        return None
    return focus.reason


def _blocked_with_plan_sorted(
    backlog: dict[str, Any],
) -> list[tuple[int, dict[str, Any], str]]:
    """Blocked rows with planPath, sorted by priority then list index."""
    candidates: list[tuple[int, dict[str, Any], str]] = []
    for index, item in enumerate(_backlog_items(backlog)):
        if not isinstance(item, dict):
            continue
        if _backlog_item_status(item) != "blocked":
            continue
        plan_path = norm_plan(str(item.get("planPath") or ""))
        if not plan_path:
            continue
        candidates.append((index, item, plan_path))
    candidates.sort(key=lambda row: _priority_sort_key(row[0], row[1]))
    return candidates


def promote_first_blocked_with_plan(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Promote highest-priority blocked row with valid planPath when pipeline is idle."""
    repo = repo_root.resolve()
    if not backlog_enabled(repo):
        return {"promoted": False, "reason": "PPE_AUTO_PROPAGATE_QUEUE disabled"}
    if not backlog_path(repo).is_file():
        return {"promoted": False, "reason": "no backlog file"}

    backlog = load_backlog(repo)
    if not isinstance(backlog.get("items"), list):
        return {"promoted": False, "reason": "invalid backlog items"}

    if _best_queued_item(backlog) is not None:
        return {"promoted": False, "reason": "queued backlog item already exists"}

    if _pipeline_busy(backlog):
        return {"promoted": False, "reason": "pipeline busy (chartered or queued chapter in backlog)"}

    finalized_plans: list[str] = []
    focus_blocked: list[str] = []
    for _index, item, plan_path in _blocked_with_plan_sorted(backlog):
        fg = _focus_gate_blocks(repo, plan_path)
        if fg:
            focus_blocked.append(f"{plan_path}: {fg}")
            continue
        ok, err = _plan_valid(repo, plan_path)
        if not ok:
            return {
                "promoted": False,
                "reason": f"plan invalid: {err}",
                "planPath": plan_path,
                "chapterId": item.get("chapterId"),
            }
        if chapter_marked_complete_in_repo(repo, plan_path):
            if not apply:
                return {
                    "promoted": False,
                    "finalized": True,
                    "dry_run": True,
                    "planPath": plan_path,
                    "chapterId": item.get("chapterId"),
                    "reason": "evidence COMPLETE — would mark backlog done",
                }
            item["status"] = "done"
            save_backlog(repo, backlog)
            finalize_chapter_evidence_complete(repo, plan_path, apply=True)
            finalized_plans.append(plan_path)
            continue
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

    if finalized_plans:
        return {
            "promoted": False,
            "finalized": True,
            "planPath": finalized_plans[-1],
            "finalizedPlans": finalized_plans,
            "reason": "evidence COMPLETE — marked backlog done",
        }
    if focus_blocked:
        return {
            "promoted": False,
            "reason": "focus gate blocked eligible backlog rows",
            "focusGate": focus_blocked,
        }
    return {"promoted": False, "reason": "no blocked backlog item with planPath"}


def _plan_on_roadmap(roadmap: dict[str, Any], plan_path: str) -> bool:
    norm = norm_plan(plan_path)
    return any(
        isinstance(it, dict) and norm_plan(str(it.get("planPath") or "")) == norm
        for it in (roadmap.get("items") or [])
    )


def propagate_from_backlog(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Append highest-priority queued backlog row to roadmap as pending (with optional scaffold)."""
    repo = repo_root.resolve()
    if not backlog_enabled(repo):
        return {"propagated": False, "reason": "PPE_AUTO_PROPAGATE_QUEUE disabled"}
    if not backlog_path(repo).is_file():
        return {"propagated": False, "reason": "no backlog file"}
    if not roadmap_enabled(repo):
        return {"propagated": False, "reason": "roadmap disabled"}

    sync_backlog_from_roadmap(repo, apply=apply)
    backlog = load_backlog(repo)
    item = _best_queued_item(backlog)
    if item is None:
        promoted = promote_first_blocked_with_plan(repo, apply=apply)
        if promoted.get("promoted"):
            sync_backlog_from_roadmap(repo, apply=apply)
            backlog = load_backlog(repo)
            item = _best_queued_item(backlog)
        if item is None:
            out: dict[str, Any] = {"propagated": False, "reason": "no queued backlog item"}
            if promoted.get("promoted") or promoted.get("reason"):
                out["promote"] = promoted
            return out

    plan_path = norm_plan(str(item.get("planPath") or ""))
    if not plan_path:
        return {"propagated": False, "reason": "queued item missing planPath"}

    fg = _focus_gate_blocks(repo, plan_path)
    if fg:
        return {
            "propagated": False,
            "reason": f"focus gate: {fg}",
            "planPath": plan_path,
            "chapterId": item.get("chapterId"),
        }

    if chapter_marked_complete_in_repo(repo, plan_path):
        if not apply:
            return {
                "propagated": False,
                "finalized": True,
                "dry_run": True,
                "planPath": plan_path,
                "reason": "evidence COMPLETE — would mark backlog done",
            }
        item["status"] = "done"
        save_backlog(repo, backlog)
        finalize_chapter_evidence_complete(repo, plan_path, apply=True)
        return {
            "propagated": False,
            "finalized": True,
            "planPath": plan_path,
            "reason": "evidence COMPLETE — marked backlog done",
        }

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


def _next_roadmap_item_after(
    repo: Path,
    roadmap: dict[str, Any],
    *,
    after_plan: str | None,
) -> dict[str, Any] | None:
    """First non-done roadmap row after after_plan (or first eligible when after_plan is None)."""
    from scripts.ppe_roadmap import _plan_valid

    items = roadmap.get("items") or []
    passed = after_plan is None or not str(after_plan).strip()
    after_norm = norm_plan(str(after_plan or ""))
    for item in items:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if not plan:
            continue
        if not passed:
            if plan == after_norm:
                passed = True
            continue
        status = str(item.get("status") or "").strip().lower()
        if status in ("done", "skipped"):
            continue
        if chapter_marked_complete_in_repo(repo, plan):
            continue
        ok, _ = _plan_valid(repo, plan)
        if not ok:
            continue
        return item
    return None


def preview_next_chapter(repo_root: Path) -> dict[str, Any]:
    """Read-only: next chapter after closeout (or bootstrap candidate when idle)."""
    repo = repo_root.resolve()
    preview: dict[str, Any] = {"preview": True}
    active_plan: str | None = None

    try:
        from scripts.ppe_manifest import load_manifest

        manifest = load_manifest(repo)
        preview["manifest_status"] = str(manifest.get("status") or "")
        active_plan = str(manifest.get("phasePlanPath") or "").strip() or None
        preview["active_plan_path"] = active_plan
    except Exception as exc:
        preview["manifest_error"] = str(exc)

    try:
        from scripts.ppe_roadmap import (
            _first_pending_with_valid_plan,
            load_roadmap,
            roadmap_path,
        )

        if not roadmap_path(repo).is_file():
            preview["reason"] = "no roadmap file"
            return preview

        roadmap = load_roadmap(repo)
        if active_plan:
            item = _next_roadmap_item_after(repo, roadmap, after_plan=active_plan)
            if item:
                plan = norm_plan(str(item.get("planPath") or ""))
                preview.update(
                    {
                        "next_plan_path": plan,
                        "next_chapter_id": _chapter_id_from_plan(plan),
                        "next_source": "roadmap_after_active",
                        "roadmap_status": str(item.get("status") or ""),
                    }
                )
                return preview

        pending = _first_pending_with_valid_plan(repo, roadmap, apply=False)
        if pending:
            plan = norm_plan(str(pending.get("planPath") or ""))
            preview.update(
                {
                    "next_plan_path": plan,
                    "next_chapter_id": _chapter_id_from_plan(plan),
                    "next_source": "roadmap_pending_bootstrap",
                    "roadmap_status": "pending",
                }
            )
            return preview
    except Exception as exc:
        preview["roadmap_error"] = str(exc)

    prom = promote_first_blocked_with_plan(repo, apply=False)
    if prom.get("promoted"):
        preview["would_promote"] = {
            "chapterId": prom.get("chapterId"),
            "planPath": prom.get("planPath"),
        }

    prop = propagate_from_backlog(repo, apply=False)
    if prop.get("propagated") or prop.get("dry_run"):
        preview.update(
            {
                "next_plan_path": prop.get("planPath"),
                "next_chapter_id": prop.get("chapterId") or _chapter_id_from_plan(str(prop.get("planPath") or "")),
                "next_source": "backlog_propagation",
            }
        )
        return preview

    preview["reason"] = prop.get("reason") or prom.get("reason") or "no next chapter found"
    return preview


def _chapter_id_from_plan(plan_path: str) -> str:
    name = Path(plan_path).name
    if name.endswith("_relay.json"):
        return name[: -len("_relay.json")]
    return name.replace(".json", "")


def maybe_propagate_queue(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Hook: sync backlog statuses, propagate first queued row if roadmap has no pending."""
    repo = repo_root.resolve()
    from scripts.ppe_roadmap import _first_pending_with_valid_plan, load_roadmap

    out: dict[str, Any] = {"skipped": False}
    recon = reconcile_closed_chapters(repo, apply=apply)
    if any(recon.get(k) for k in recon):
        out["reconcile"] = {k: v for k, v in recon.items() if v}
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
