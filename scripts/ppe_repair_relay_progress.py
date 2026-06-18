"""One-shot: clear stale phase progress, heal operator artifacts, re-sync slice completion from main."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_manifest import load_manifest
from scripts.ppe_phase_plan_window import clear_progress, load_progress
from scripts.ppe_vm_bootstrap import (
    detach_worktrees_holding_branch,
    heal_operator_artifacts,
    heal_stale_relay_state,
    sync_slice_progress,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Repair relay progress and heal stale operator state")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--plan-path", default="", help="Override phase plan path")
    ap.add_argument("--mark-complete", default="", help="Mark a slice complete in progress")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    plan_path = args.plan_path.strip()
    if not plan_path:
        manifest = load_manifest(repo)
        plan_path = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_path:
        print("ppe_repair_relay_progress: no active phase plan", file=sys.stderr)
        return 1

    mark_id = str(args.mark_complete or "").strip()
    if mark_id:
        from scripts.ppe_phase_plan_window import mark_slice_complete

        mark_slice_complete(repo, plan_path, mark_id)
        print(json.dumps({"marked": mark_id, "progress": load_progress(repo)}, indent=2))
        return 0

    clear_progress(repo, plan_path)
    detached = detach_worktrees_holding_branch(repo, "main")
    heal_ops = heal_operator_artifacts(repo)
    heal_relay = heal_stale_relay_state(repo)
    sync = sync_slice_progress(repo, plan_path)
    report = {
        "plan_path": plan_path,
        "detached_worktrees": detached,
        "heal_artifacts": heal_ops,
        "heal_relay": heal_relay,
        "sync": sync,
        "progress": load_progress(repo),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
