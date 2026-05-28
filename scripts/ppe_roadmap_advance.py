"""CLI: sync roadmap ↔ queue, bootstrap idle SELECTION, advance after closeout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_roadmap import (
    advance_after_chapter_closeout,
    bootstrap_next_ready,
    maybe_advance_roadmap_and_select,
    prepare_selection_idle,
    sync_roadmap_to_queue,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE PHASE_SELECTION_ROADMAP automation")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true", help="Write queue and roadmap files")
    ap.add_argument(
        "--sync",
        action="store_true",
        help="Sync roadmap statuses into PHASE_QUEUE.json",
    )
    ap.add_argument(
        "--bootstrap",
        action="store_true",
        help="If idle, promote first valid pending roadmap item to READY",
    )
    ap.add_argument(
        "--closed-plan",
        type=str,
        default="",
        help="After chapter closeout: mark this plan done and advance next pending",
    )
    ap.add_argument(
        "--full",
        action="store_true",
        help="sync + bootstrap + advance (if --closed-plan) + auto-select",
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    apply = args.apply

    if args.full:
        out = maybe_advance_roadmap_and_select(
            repo,
            closed_plan_path=args.closed_plan,
            apply=apply,
        )
        print(json.dumps(out, indent=2))
        return int(out.get("auto_select_exit") or 0)

    out: dict[str, object] = {}
    if args.sync or not (args.bootstrap or args.closed_plan):
        changes = sync_roadmap_to_queue(repo, apply=apply)
        out["sync"] = changes

    if args.closed_plan:
        out["advance"] = advance_after_chapter_closeout(
            repo,
            closed_plan_path=args.closed_plan,
            apply=apply,
        )

    if args.bootstrap or args.full:
        out["bootstrap"] = bootstrap_next_ready(repo, apply=apply)

    if args.bootstrap and apply and not args.closed_plan:
        from scripts.ppe_auto_select import run_auto_select

        rc = run_auto_select(repo, apply=True, select_only=False, mark_done=False, force=False)
        out["auto_select_exit"] = rc

    if not args.sync and not args.bootstrap and not args.closed_plan:
        out["prepare"] = prepare_selection_idle(repo, apply=apply)

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
