"""Automate SELECTION in a bounded, explicit way.

This script is intentionally conservative:
- It only selects from an explicit queue file (docs/SOP/PHASE_QUEUE.json).
- It only writes docs/SOP/ACTIVE_PHASE_MANIFEST.json when invoked with --apply.
- It refuses to override an in-flight/selected manifest (READY/RUNNING).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import (
    MANIFEST_REL,
    load_manifest,
    load_phase_plan,
    save_manifest,
    validate_phase_plan,
)


QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"


def _load_queue(repo_root: Path) -> dict[str, Any]:
    p = (repo_root / QUEUE_REL).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Missing queue file: {QUEUE_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


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
    queue = _load_queue(repo_root)
    items = queue.get("items") or []
    if not isinstance(items, list):
        raise ValueError("queue: items must be an array")

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").strip().upper()
        if status != "READY":
            continue
        plan_path = str(item.get("planPath") or "").strip()
        if not plan_path:
            continue
        errors = _plan_exists_and_valid(repo_root, plan_path)
        if errors:
            return None, f"queue item {i} invalid: " + "; ".join(errors)
        reason = str(item.get("reason") or "").strip() or f"queue item {i} READY"
        return plan_path, reason

    return None, "no READY items in queue"


def mark_queue_item_done(repo_root: Path, *, plan_path: str) -> tuple[bool, str]:
    """Mark the first matching queue item as DONE."""
    queue_path = (repo_root / QUEUE_REL).resolve()
    queue = _load_queue(repo_root)
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
            item["doneReason"] = "marked DONE by ppe_auto_select.py"
        queue["items"][i] = item
        queue_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
        return True, f"queue item {i} marked DONE"

    return False, "no matching planPath in queue"


def _print_result(*, selected: bool, plan_path: str | None, reason: str) -> None:
    obj = {"selected": selected, "plan_path": plan_path, "reason": reason}
    print(json.dumps(obj, indent=2))


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

    repo = args.repo_root.resolve()

    try:
        manifest = load_manifest(repo)
    except Exception as e:
        print(f"ERROR: could not load {MANIFEST_REL}: {e}", file=sys.stderr)
        return 2

    status = str(manifest.get("status") or "").strip().upper()
    current_plan = str(manifest.get("phasePlanPath") or "").strip()

    if args.apply and args.select_only:
        print("ERROR: --apply and --select-only are mutually exclusive", file=sys.stderr)
        return 2

    if args.mark_done:
        if not args.apply:
            print("ERROR: --mark-done requires --apply", file=sys.stderr)
            return 2
        if not current_plan:
            _print_result(selected=False, plan_path=None, reason="no phasePlanPath to mark DONE")
            return 1
        ok, reason = mark_queue_item_done(repo, plan_path=current_plan)
        _print_result(selected=ok, plan_path=current_plan, reason=reason)
        return 0 if ok else 1

    if status in {"READY", "RUNNING"}:
        _print_result(selected=False, plan_path=current_plan or None, reason=f"manifest is {status}")
        return 0

    if current_plan and not args.force:
        _print_result(
            selected=False,
            plan_path=current_plan,
            reason="manifest already names a plan; refusing without --force",
        )
        return 0

    plan_path, reason = choose_next_plan(repo)
    if not plan_path:
        _print_result(selected=False, plan_path=None, reason=reason)
        return 1

    if args.apply and not args.select_only:
        # Keep existing selectionRecord/sprintSpecPath unless queue/plan provides better info later.
        # For now we set minimal required fields for run_ppe.cmd.
        plan = load_phase_plan(repo, plan_path)
        manifest["phasePlanPath"] = plan_path
        manifest["sprintSpecPath"] = str(plan.get("sprintSpecPath") or manifest.get("sprintSpecPath") or "").strip()
        manifest["selectionRecord"] = str(plan.get("selectionRecord") or manifest.get("selectionRecord") or "").strip()
        manifest["status"] = "READY"
        manifest["notes"] = f"auto-selected from {QUEUE_REL}: {reason}"
        save_manifest(repo, manifest)

    _print_result(selected=True, plan_path=plan_path, reason=reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

