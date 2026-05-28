"""PHASE_QUEUE integrity audit and auto-repair (duplicate READY, stale re-queue)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_queue import load_queue, save_queue

Issue = dict[str, Any]
Fix = dict[str, Any]


def _norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _closeout_meta(plan: dict[str, Any]) -> dict[str, Any]:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and isinstance(sl.get("closeout"), dict):
            return sl["closeout"]
    return {}


def chapter_marked_complete_in_repo(repo_root: Path, plan_path: str) -> bool:
    """True when phase-plan closeout evidence doc shows chapter COMPLETE."""
    try:
        plan = load_phase_plan(repo_root, plan_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    closeout = _closeout_meta(plan)
    evidence_rel = str(closeout.get("evidenceDoc") or "").strip()
    if not evidence_rel:
        return False
    evidence = repo_root / evidence_rel
    if not evidence.is_file():
        return False
    head = evidence.read_text(encoding="utf-8", errors="replace")[:1200]
    if re.search(r"\*\*Status:\*\*\s*\*\*COMPLETE\*\*", head, re.I):
        return True
    if re.search(r"chapter\s+\*\*COMPLETE\*\*", head, re.I):
        return True
    return False


def audit_queue(repo_root: Path) -> tuple[list[Issue], list[Fix]]:
    repo = repo_root.resolve()
    queue = load_queue(repo)
    items = queue.get("items") or []
    if not isinstance(items, list):
        return [{"code": "INVALID_QUEUE", "detail": "items must be an array"}], []

    issues: list[Issue] = []
    fixes: list[Fix] = []
    by_plan: dict[str, list[int]] = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append({"code": "INVALID_ITEM", "index": i, "detail": "not an object"})
            continue
        plan = _norm_plan(str(item.get("planPath") or ""))
        if not plan:
            issues.append({"code": "MISSING_PLAN", "index": i})
            continue
        by_plan.setdefault(plan, []).append(i)

    for plan, indices in by_plan.items():
        if len(indices) <= 1:
            continue
        statuses = [str(items[i].get("status") or "").upper() for i in indices]
        if len(set(statuses)) == 1 and statuses[0] == "DONE":
            continue
        issues.append(
            {
                "code": "DUPLICATE_PLAN",
                "planPath": plan,
                "indices": indices,
                "statuses": statuses,
            }
        )

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").upper()
        plan = _norm_plan(str(item.get("planPath") or ""))
        if status != "READY" or not plan:
            continue
        done_idxs = [
            j
            for j in by_plan.get(plan, [i])
            if str(items[j].get("status") or "").upper() == "DONE"
        ]
        if done_idxs:
            issues.append(
                {
                    "code": "READY_AFTER_DONE",
                    "index": i,
                    "planPath": plan,
                    "doneIndex": done_idxs[0],
                }
            )
        elif chapter_marked_complete_in_repo(repo, plan):
            issues.append(
                {
                    "code": "READY_BUT_CHAPTER_COMPLETE",
                    "index": i,
                    "planPath": plan,
                }
            )

    return issues, fixes


def repair_queue(repo_root: Path, *, apply: bool) -> tuple[list[Fix], list[Issue]]:
    """Apply safe repairs; return (fixes_applied, remaining_issues)."""
    repo = repo_root.resolve()
    queue = load_queue(repo)
    items = list(queue.get("items") or [])
    fixes: list[Fix] = []

    if not isinstance(items, list):
        return fixes, [{"code": "INVALID_QUEUE", "detail": "items must be an array"}]

    by_plan: dict[str, list[int]] = {}
    for i, item in enumerate(items):
        if isinstance(item, dict):
            plan = _norm_plan(str(item.get("planPath") or ""))
            if plan:
                by_plan.setdefault(plan, []).append(i)

    def _mark_done(i: int, *, reason: str) -> None:
        item = items[i]
        if str(item.get("status") or "").upper() == "DONE":
            return
        item["status"] = "DONE"
        if not str(item.get("doneReason") or "").strip():
            item["doneReason"] = reason
        fixes.append({"action": "mark_done", "index": i, "planPath": _norm_plan(str(item.get("planPath") or "")), "reason": reason})

    # Duplicate planPath: collapse READY rows when chapter already DONE or evidence COMPLETE.
    for plan, indices in list(by_plan.items()):
        if len(indices) < 2:
            continue
        done_idxs = [j for j in indices if str(items[j].get("status") or "").upper() == "DONE"]
        ready_idxs = [j for j in indices if str(items[j].get("status") or "").upper() == "READY"]
        if not ready_idxs:
            if len(done_idxs) > 1:
                for j in sorted(done_idxs[1:], reverse=True):
                    fixes.append(
                        {
                            "action": "remove_duplicate_done",
                            "index": j,
                            "planPath": plan,
                            "reason": "auto-repair: drop duplicate DONE row",
                        }
                    )
                    del items[j]
            continue
        if done_idxs or chapter_marked_complete_in_repo(repo, plan):
            for j in ready_idxs:
                _mark_done(
                    j,
                    reason="auto-repair: duplicate READY removed (chapter already DONE in queue or evidence)",
                )

    # Rebuild index map after possible status changes.
    by_plan = {}
    for i, item in enumerate(items):
        if isinstance(item, dict):
            plan = _norm_plan(str(item.get("planPath") or ""))
            if plan:
                by_plan.setdefault(plan, []).append(i)

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").upper()
        plan = _norm_plan(str(item.get("planPath") or ""))
        if status != "READY" or not plan:
            continue
        done_idxs = [j for j in by_plan.get(plan, []) if str(items[j].get("status") or "").upper() == "DONE"]
        if done_idxs and i not in done_idxs:
            _mark_done(
                i,
                reason="auto-repair: READY while same planPath already DONE",
            )
        elif chapter_marked_complete_in_repo(repo, plan):
            _mark_done(
                i,
                reason="auto-repair: evidence doc shows chapter COMPLETE",
            )

    if apply and fixes:
        queue["items"] = items
        save_queue(repo, queue)

    remaining, _ = audit_queue(repo)
    return fixes, remaining


def run_queue_health(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    fixes, remaining = repair_queue(repo_root, apply=apply)
    return {
        "apply": apply,
        "fixes": fixes,
        "fix_count": len(fixes),
        "remaining_issues": remaining,
        "ok": len(remaining) == 0,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit/repair PHASE_QUEUE.json")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true", help="Write repairs to PHASE_QUEUE.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    result = run_queue_health(args.repo_root.resolve(), apply=args.apply)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for fix in result["fixes"]:
            print(f"FIX: {fix}")
        for issue in result["remaining_issues"]:
            print(f"ISSUE: {issue}", file=sys.stderr)
        if result["fixes"]:
            print(f"ppe_queue_health: applied {result['fix_count']} repair(s)")
        if result["ok"]:
            print("ppe_queue_health: OK")
        else:
            print(f"ppe_queue_health: {len(result['remaining_issues'])} issue(s) remain", file=sys.stderr)
    return 0 if result["ok"] or not args.apply else (1 if result["remaining_issues"] else 0)


if __name__ == "__main__":
    raise SystemExit(main())
