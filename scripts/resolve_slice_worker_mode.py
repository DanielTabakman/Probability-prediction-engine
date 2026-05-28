"""Print resolved worker mode for run_slice.cmd (acp | deterministic | local-agent)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_slice_worker_mode import resolve_worker_mode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", required=True)
    ap.add_argument("--phase-plan", default="")
    args = ap.parse_args(argv)

    slice_obj = None
    if args.phase_plan.strip():
        try:
            plan = load_phase_plan(args.repo_root, args.phase_plan)
            for sl in plan.get("slices") or []:
                if str(sl.get("sliceId") or "") == args.slice_id:
                    slice_obj = sl
                    break
        except Exception as e:
            print(f"WARN: {e}", file=sys.stderr)

    mode = resolve_worker_mode(slice_id=args.slice_id, slice_obj=slice_obj)
    print(mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
