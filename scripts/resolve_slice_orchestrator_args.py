"""Resolve orchestrator sus/hard/maxAttempts for run_slice.cmd from phase plan."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.ppe_manifest import load_phase_plan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Slice orchestrator timeout args")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", required=True)
    ap.add_argument("--phase-plan", default="")
    ap.add_argument("--default-sus", type=int, default=15)
    ap.add_argument("--default-hard", type=int, default=30)
    ap.add_argument("--default-max", type=int, default=2)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    sus, hard, mx = args.default_sus, args.default_hard, args.default_max
    plan_rel = (args.phase_plan or os.environ.get("PPE_PHASE_PLAN") or "").strip()
    if plan_rel:
        try:
            plan = load_phase_plan(repo, plan_rel)
            for sl in plan.get("slices") or []:
                if str(sl.get("sliceId") or "") == args.slice_id:
                    sus = int(sl.get("susMinutes") or sus)
                    hard = int(sl.get("hardMinutes") or hard)
                    mx = int(sl.get("maxAttempts") or mx)
                    break
        except Exception as e:
            print(f"WARN: could not load phase plan: {e}", file=sys.stderr)

    print(f"{sus} {hard} {mx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
