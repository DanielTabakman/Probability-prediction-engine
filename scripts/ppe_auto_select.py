"""Automate SELECTION in a bounded, explicit way.

This script is intentionally conservative:
- It only selects from an explicit queue file (docs/SOP/PHASE_QUEUE.json).
- It only writes docs/SOP/ACTIVE_PHASE_MANIFEST.json when invoked with --apply.
- It refuses to override an in-flight/selected manifest (READY/RUNNING).
- On COMPLETE with a stale phasePlanPath it marks the queue item DONE and clears the plan.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import (
    MANIFEST_REL,
    clear_manifest_plan_path,
    load_manifest,
    load_phase_plan,
    save_manifest,
    validate_phase_plan,
)
from scripts.ppe_queue import QUEUE_REL, find_queue_item_index, load_queue, mark_queue_item_done
from scripts.ppe_queue_health import chapter_marked_complete_in_repo, repair_backlog, repair_queue


def _plan_exists_and_valid(repo_root: Path, plan_path: str) -> list[str]:
    errors: list[str] = []
    plan_fs = Path(plan_path)
    if not plan_fs.is_absolute():
        plan_fs = repo_root / plan_fs
    if not plan_fs.is_file():
        return [f"plan not found: {plan_path}"]
    try:
        plan = load_phase_plan(repo_root, plan_path)
    except json.JSONDecodeError as e:
        return [f"plan JSON invalid: {e}"]
    errors.extend(validate_phase_plan(plan))
    return errors


def choose_next_plan(repo_root: Path) -> tuple[str | None, str]:
    """Return (plan_path, reason). plan_path is None when nothing is selectable."""
    result = choose_next_plan_result(repo_root)
    return result.plan_path, result.reason


def choose_next_plan_result(repo_root: Path):
    from scripts.ppe_queue_selection import choose_next_selectable

    queue = load_queue(repo_root)
    items = queue.get("items") or []
    if not isinstance(items, list):
        raise ValueError("queue: items must be an array")
    return choose_next_selectable(repo_root, items, status="READY")


def maybe_notify_selection_skips(
    repo_root: Path,
    *,
    skipped: list[Any],
    selected_plan: str | None,
    apply: bool,
) -> None:
    if not apply or not skipped:
        return
    try:
        from scripts.ppe_progress_notify import notify_queue_selection_skips
        from scripts.ppe_queue_selection import chapter_id_for_plan

        selected_cid = chapter_id_for_plan(repo_root, selected_plan) if selected_plan else ""
        notify_queue_selection_skips(
            repo_root,
            skipped,
            selected_plan=selected_plan,
            selected_chapter_id=selected_cid,
        )
    except ImportError:
        pass


def finalize_complete_manifest_plan(repo_root: Path, *, apply: bool) -> tuple[bool, str]:
    """If manifest is COMPLETE with phasePlanPath set, mark queue DONE and clear plan."""
    manifest = load_manifest(repo_root)
    status = str(manifest.get("status") or "").strip().upper()
    current_plan = str(manifest.get("phasePlanPath") or "").strip()
    if status != "COMPLETE" or not current_plan:
        return False, "manifest not COMPLETE with phasePlanPath"
    if not apply:
        return True, f"would finalize COMPLETE manifest plan {current_plan}"
    ok, reason = mark_queue_item_done(
        repo_root,
        plan_path=current_plan,
        done_reason="marked DONE by ppe_auto_select.py (COMPLETE manifest finalize)",
    )
    clear_manifest_plan_path(
        repo_root,
        note="Auto-finalized COMPLETE manifest before next SELECTION.",
    )
    return ok, reason


def _print_result(*, selected: bool, plan_path: str | None, reason: str) -> None:
    obj = {"selected": selected, "plan_path": plan_path, "reason": reason}
    print(json.dumps(obj, indent=2))


def run_auto_select(
    repo_root: Path,
    *,
    apply: bool,
    select_only: bool,
    mark_done: bool,
    force: bool,
) -> int:
    """Core selection logic; returns process exit code."""
    repo = repo_root.resolve()

    if apply and not select_only:
        backlog_fixes, _ = repair_backlog(repo, apply=True)
        fixes, remaining = repair_queue(repo, apply=True)
        fixes = backlog_fixes + fixes
        if fixes:
            print(f"ppe_auto_select: queue auto-repair applied {len(fixes)} fix(es)")
        if remaining:
            print(
                f"ppe_auto_select: queue health warnings: {len(remaining)} issue(s) remain",
                file=sys.stderr,
            )
        try:
            from scripts.ppe_roadmap import prepare_selection_idle

            prep = prepare_selection_idle(repo, apply=True)
            if not prep.get("skipped"):
                print(f"ppe_auto_select: roadmap prepare {json.dumps(prep)}")
        except FileNotFoundError:
            pass
        except Exception as exc:
            print(f"ppe_auto_select: roadmap prepare warning: {exc}", file=sys.stderr)

    try:
        manifest = load_manifest(repo)
    except Exception as e:
        print(f"ERROR: could not load {MANIFEST_REL}: {e}", file=sys.stderr)
        return 2

    status = str(manifest.get("status") or "").strip().upper()
    current_plan = str(manifest.get("phasePlanPath") or "").strip()

    if mark_done:
        if not apply:
            print("ERROR: --mark-done requires --apply", file=sys.stderr)
            return 2
        if not current_plan:
            _print_result(selected=False, plan_path=None, reason="no phasePlanPath to mark DONE")
            return 0
        ok, reason = mark_queue_item_done(
            repo,
            plan_path=current_plan,
            done_reason="marked DONE by ppe_auto_select.py (--mark-done)",
        )
        _print_result(selected=ok, plan_path=current_plan, reason=reason)
        return 0

    if status in {"READY", "RUNNING"} and current_plan:
        _print_result(selected=False, plan_path=current_plan, reason=f"manifest is {status}")
        return 0

    if status == "COMPLETE" and current_plan:
        fin_apply = apply and not select_only
        finalize_complete_manifest_plan(repo, apply=fin_apply)
        if fin_apply:
            manifest = load_manifest(repo)
            current_plan = str(manifest.get("phasePlanPath") or "").strip()
            status = str(manifest.get("status") or "").strip().upper()

    if current_plan and not force and status != "COMPLETE":
        _print_result(
            selected=False,
            plan_path=current_plan,
            reason="manifest already names a plan; refusing without --force",
        )
        return 0

    if current_plan and not force and status == "COMPLETE":
        _print_result(
            selected=False,
            plan_path=None,
            reason="COMPLETE manifest still has plan after finalize; use --force",
        )
        return 1

    plan_result = choose_next_plan_result(repo)
    plan_path = plan_result.plan_path
    reason = plan_result.reason
    if apply and not select_only:
        maybe_notify_selection_skips(
            repo,
            skipped=plan_result.skipped,
            selected_plan=plan_path,
            apply=True,
        )
    if not plan_path:
        _print_result(selected=False, plan_path=None, reason=reason)
        return 0

    if apply and not select_only:
        plan = load_phase_plan(repo, plan_path)
        manifest = load_manifest(repo)
        manifest["phasePlanPath"] = plan_path
        manifest["sprintSpecPath"] = str(plan.get("sprintSpecPath") or manifest.get("sprintSpecPath") or "").strip()
        manifest["selectionRecord"] = str(plan.get("selectionRecord") or manifest.get("selectionRecord") or "").strip()
        manifest["status"] = "READY"
        manifest["notes"] = f"auto-selected from {QUEUE_REL}: {reason}"
        queue = load_queue(repo)
        idx = find_queue_item_index(queue, plan_path)
        if idx is not None:
            item = (queue.get("items") or [])[idx]
            if isinstance(item, dict):
                wm = str(item.get("workerMode") or "").strip()
                if wm:
                    manifest["workerMode"] = wm
        save_manifest(repo, manifest)

    _print_result(selected=True, plan_path=plan_path, reason=reason)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE bounded selection automation")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true", help="Write ACTIVE_PHASE_MANIFEST.json")
    ap.add_argument(
        "--select-only",
        action="store_true",
        help="Print what would be selected, but never write the manifest.",
    )
    ap.add_argument(
        "--mark-done",
        action="store_true",
        help="Mark the currently selected phasePlanPath as DONE in PHASE_QUEUE.json (requires --apply).",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Allow selecting even if manifest is COMPLETE but still has a planPath (rare).",
    )
    args = ap.parse_args(argv)

    if args.apply and args.select_only:
        print("ERROR: --apply and --select-only are mutually exclusive", file=sys.stderr)
        return 2

    return run_auto_select(
        args.repo_root.resolve(),
        apply=args.apply,
        select_only=args.select_only,
        mark_done=args.mark_done,
        force=args.force,
    )


if __name__ == "__main__":
    raise SystemExit(main())
