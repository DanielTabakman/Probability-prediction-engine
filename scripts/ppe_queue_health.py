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

BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
BACKLOG_ACTIVE_STATUSES = frozenset({"blocked", "chartered", "queued"})
BACKLOG_TERMINAL_STATUSES = frozenset({"done", "skipped"})
FINALIZE_DONE_REASON = "auto-repair: evidence doc shows chapter COMPLETE"
PREMATURE_REOPEN_REASON = "auto-repair: chapter closeout reverted — evidence/slices still pending"
ROADMAP_REPAIR_REASON = "auto-repair: backlog status on roadmap normalized"
# Backlog-only statuses sometimes land on PHASE_SELECTION_ROADMAP by hand; map to valid roadmap rows.
ROADMAP_INVALID_TO_VALID = {
    "chartered": "pending",
    "blocked": "skipped",
    "queued": "pending",
}


def roadmap_row_should_activate_for_backlog(roadmap_status: str, backlog_status: str) -> bool:
    """True when a backlog row is ready to run but the roadmap row is still idle."""
    rs = str(roadmap_status or "").strip().lower()
    bs = str(backlog_status or "").strip().lower()
    if bs not in ("queued", "chartered"):
        return False
    if rs in ROADMAP_INVALID_TO_VALID:
        return True
    return rs == "skipped"


def _norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _closeout_meta(plan: dict[str, Any]) -> dict[str, Any]:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and isinstance(sl.get("closeout"), dict):
            return sl["closeout"]
    return {}


def _evidence_has_pending_slices(body: str) -> bool:
    """True when the evidence slice table still lists PENDING rows."""
    for line in body.splitlines():
        if "|" not in line:
            continue
        for cell in line.split("|"):
            cell = cell.strip()
            if re.fullmatch(r"\*{0,2}PENDING\*{0,2}", cell, re.I):
                return True
    return False


def chapter_marked_complete_in_repo(repo_root: Path, plan_path: str) -> bool:
    """True when closeout evidence shows chapter COMPLETE and no slice rows are PENDING."""
    try:
        plan = load_phase_plan(repo_root, plan_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    closeout = _closeout_meta(plan)
    recurring = closeout.get("recurring")
    if recurring is True or str(recurring or "").strip().lower() in ("1", "true", "yes", "on"):
        return False
    evidence_rel = str(closeout.get("evidenceDoc") or "").strip()
    if not evidence_rel:
        return False
    evidence = repo_root / evidence_rel
    if not evidence.is_file():
        return False
    body = evidence.read_text(encoding="utf-8", errors="replace")
    head = body[:1200]
    complete_header = bool(
        re.search(r"\*\*Status:\*\*\s*\*\*COMPLETE\*\*", head, re.I)
        or re.search(r"chapter\s+\*\*COMPLETE\*\*", head, re.I)
        or re.search(r"##\s*Chapter status\s*[\r\n]+\s*\*\*COMPLETE\*\*", head, re.I)
    )
    if not complete_header:
        return False
    if _evidence_has_pending_slices(body):
        return False
    return True


def finalize_chapter_evidence_complete(
    repo_root: Path,
    plan_path: str,
    *,
    apply: bool,
    done_reason: str = FINALIZE_DONE_REASON,
) -> bool:
    """Mark queue, roadmap, and backlog done when closeout evidence is COMPLETE."""
    repo = repo_root.resolve()
    norm = _norm_plan(plan_path)
    if not norm or not chapter_marked_complete_in_repo(repo, norm):
        return False
    if not apply:
        return True

    from scripts.ppe_queue import mark_queue_item_done

    mark_queue_item_done(repo, plan_path=norm, done_reason=done_reason)

    try:
        from scripts.ppe_roadmap import (
            _set_roadmap_status,
            load_roadmap,
            roadmap_enabled,
            roadmap_path,
            save_roadmap,
        )

        if roadmap_enabled(repo) and roadmap_path(repo).is_file():
            roadmap = load_roadmap(repo)
            if _set_roadmap_status(roadmap, norm, "done"):
                save_roadmap(repo, roadmap)
    except FileNotFoundError:
        pass

    try:
        from scripts.ppe_propagate_queue import backlog_path, load_backlog, save_backlog

        if backlog_path(repo).is_file():
            backlog = load_backlog(repo)
            for item in backlog.get("items") or []:
                if not isinstance(item, dict):
                    continue
                if _norm_plan(str(item.get("planPath") or "")) == norm:
                    item["status"] = "done"
            save_backlog(repo, backlog)
    except FileNotFoundError:
        pass

    return True


def audit_backlog(repo_root: Path) -> list[Issue]:
    """Detect backlog rows still active while closeout evidence is COMPLETE."""
    repo = repo_root.resolve()
    try:
        from scripts.ppe_propagate_queue import backlog_path, load_backlog
    except ImportError:
        return []

    if not backlog_path(repo).is_file():
        return []

    backlog = load_backlog(repo)
    issues: list[Issue] = []
    for i, item in enumerate(backlog.get("items") or []):
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").strip().lower()
        plan = _norm_plan(str(item.get("planPath") or ""))
        if not plan or status not in BACKLOG_ACTIVE_STATUSES:
            continue
        if chapter_marked_complete_in_repo(repo, plan):
            issues.append(
                {
                    "code": "BACKLOG_ACTIVE_BUT_EVIDENCE_COMPLETE",
                    "index": i,
                    "planPath": plan,
                    "status": status,
                    "chapterId": item.get("chapterId"),
                }
            )
    return issues


def audit_roadmap(repo_root: Path) -> list[Issue]:
    """Detect roadmap rows using backlog vocabulary or other invalid statuses."""
    repo = repo_root.resolve()
    try:
        from scripts.ppe_roadmap import VALID_ROADMAP_STATUSES, load_roadmap, roadmap_enabled, roadmap_path
    except ImportError:
        return []

    if not roadmap_enabled(repo) or not roadmap_path(repo).is_file():
        return []

    roadmap = load_roadmap(repo)
    issues: list[Issue] = []
    for i, item in enumerate(roadmap.get("items") or []):
        if not isinstance(item, dict):
            continue
        rs = str(item.get("status") or "").strip().lower()
        if rs in VALID_ROADMAP_STATUSES:
            continue
        plan = _norm_plan(str(item.get("planPath") or ""))
        issues.append(
            {
                "code": "ROADMAP_INVALID_STATUS",
                "index": i,
                "planPath": plan,
                "status": rs,
            }
        )
    return issues


def _roadmap_repair_target(
    repo: Path,
    *,
    status: str,
    plan_path: str,
    has_pending: bool,
) -> tuple[str, bool]:
    """Return (new_status, has_pending_after)."""
    if plan_path and chapter_marked_complete_in_repo(repo, plan_path):
        return "done", has_pending
    mapped = ROADMAP_INVALID_TO_VALID.get(status)
    if mapped == "pending":
        if has_pending:
            return "skipped", has_pending
        return "pending", True
    if mapped:
        return mapped, has_pending
    return "skipped", has_pending


def repair_roadmap(repo_root: Path, *, apply: bool) -> tuple[list[Fix], list[Issue]]:
    """Normalize invalid roadmap statuses (e.g. chartered/blocked from backlog vocabulary)."""
    repo = repo_root.resolve()
    fixes: list[Fix] = []
    try:
        from scripts.ppe_roadmap import load_roadmap, roadmap_enabled, roadmap_path, save_roadmap
    except ImportError:
        return fixes, []

    if not roadmap_enabled(repo) or not roadmap_path(repo).is_file():
        return fixes, []

    roadmap = load_roadmap(repo)
    items = roadmap.get("items") or []
    if not isinstance(items, list):
        return fixes, [{"code": "INVALID_ROADMAP", "detail": "items must be an array"}]

    has_pending = any(
        isinstance(it, dict) and str(it.get("status") or "").strip().lower() == "pending" for it in items
    )
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        prev = str(item.get("status") or "").strip().lower()
        try:
            from scripts.ppe_roadmap import VALID_ROADMAP_STATUSES
        except ImportError:
            VALID_ROADMAP_STATUSES = frozenset({"done", "pending", "ready", "skipped"})
        if prev in VALID_ROADMAP_STATUSES:
            continue
        plan = _norm_plan(str(item.get("planPath") or ""))
        new_status, has_pending = _roadmap_repair_target(
            repo,
            status=prev,
            plan_path=plan,
            has_pending=has_pending,
        )
        if apply:
            item["status"] = new_status
        fixes.append(
            {
                "action": "normalize_roadmap_status",
                "index": i,
                "planPath": plan,
                "from": prev,
                "to": new_status,
                "reason": ROADMAP_REPAIR_REASON,
            }
        )

    if apply and fixes:
        save_roadmap(repo, roadmap)

    remaining = audit_roadmap(repo) if apply else audit_roadmap(repo)
    return fixes, remaining


def repair_backlog(repo_root: Path, *, apply: bool) -> tuple[list[Fix], list[Issue]]:
    """Mark active backlog rows done when evidence already shows COMPLETE."""
    repo = repo_root.resolve()
    fixes: list[Fix] = []
    issues = audit_backlog(repo)
    for issue in issues:
        plan = str(issue.get("planPath") or "")
        if not plan:
            continue
        if apply:
            finalize_chapter_evidence_complete(repo, plan, apply=True)
        fixes.append(
            {
                "action": "finalize_backlog_evidence_complete",
                "planPath": plan,
                "index": issue.get("index"),
                "reason": FINALIZE_DONE_REASON,
            }
        )
    remaining = audit_backlog(repo) if apply else issues
    return fixes, remaining


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


def heal_premature_chapter_closeout(repo_root: Path, *, apply: bool) -> tuple[list[Fix], list[str]]:
    """Re-open manifest/queue when a chapter was marked DONE/COMPLETE but evidence is not complete."""
    repo = repo_root.resolve()
    fixes: list[Fix] = []
    actions: list[str] = []

    try:
        from scripts.ppe_manifest import load_manifest, save_manifest

        manifest = load_manifest(repo)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fixes, actions

    manifest_status = str(manifest.get("status") or "").upper()
    manifest_plan = _norm_plan(str(manifest.get("phasePlanPath") or ""))
    queue = load_queue(repo)
    items = list(queue.get("items") or [])
    if not isinstance(items, list):
        return fixes, actions

    reopened_plan: str | None = None

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        plan = _norm_plan(str(item.get("planPath") or ""))
        if not plan:
            continue
        qst = str(item.get("status") or "").upper()
        if qst == "READY" and not chapter_marked_complete_in_repo(repo, plan):
            if manifest_status == "COMPLETE" and not manifest_plan:
                reopened_plan = reopened_plan or plan
                actions.append(f"queue READY {plan} while manifest idle COMPLETE")
            continue
        if qst != "DONE" or chapter_marked_complete_in_repo(repo, plan):
            continue
        fixes.append(
            {
                "action": "reopen_chapter",
                "index": i,
                "planPath": plan,
                "reason": PREMATURE_REOPEN_REASON,
            }
        )
        if apply:
            item["status"] = "READY"
            item.pop("doneReason", None)
            reopened_plan = plan

    if apply and fixes:
        queue["items"] = items
        save_queue(repo, queue)

    target_plan = reopened_plan or (
        manifest_plan
        if manifest_status in ("READY", "RUNNING") and manifest_plan
        else None
    )
    if apply and manifest_status == "COMPLETE" and not manifest_plan and target_plan:
        manifest["status"] = "READY"
        manifest["phasePlanPath"] = target_plan
        prev = str(manifest.get("notes") or "").strip()
        manifest["notes"] = f"{prev} {PREMATURE_REOPEN_REASON}".strip() if prev else PREMATURE_REOPEN_REASON
        save_manifest(repo, manifest)
        actions.append(f"manifest reopened -> READY {target_plan}")

        try:
            from scripts.ppe_roadmap import load_roadmap, roadmap_enabled, roadmap_path, save_roadmap

            if roadmap_enabled(repo) and roadmap_path(repo).is_file():
                road = load_roadmap(repo)
                for row in road.get("items") or []:
                    if not isinstance(row, dict):
                        continue
                    if _norm_plan(str(row.get("planPath") or "")) != target_plan:
                        continue
                    if str(row.get("status") or "").strip().lower() == "done":
                        row["status"] = "ready"
                        actions.append(f"roadmap {target_plan} -> ready")
                save_roadmap(repo, road)
        except Exception:
            pass

    return fixes, actions


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
    roadmap_fixes, roadmap_remaining = repair_roadmap(repo_root, apply=apply)
    backlog_fixes, backlog_remaining = repair_backlog(repo_root, apply=apply)
    queue_fixes, queue_remaining = repair_queue(repo_root, apply=apply)
    fixes = roadmap_fixes + backlog_fixes + queue_fixes
    remaining = roadmap_remaining + backlog_remaining + queue_remaining
    return {
        "apply": apply,
        "fixes": fixes,
        "fix_count": len(fixes),
        "remaining_issues": remaining,
        "roadmap_issues": roadmap_remaining,
        "backlog_issues": backlog_remaining,
        "queue_issues": queue_remaining,
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
