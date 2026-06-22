"""IDE product slice closeout with bounded gate repair."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="IDE BUILD closeout: bounded gate, mark ready, run_ppe_local")
    ap.add_argument("slice_id")
    ap.add_argument("plan_path")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--gate-only", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    slice_id = args.slice_id.strip()
    plan_path = args.plan_path.strip()

    from scripts.ppe_build_repair import run_bounded_gate

    print(f"ppe_ide_build_closeout: slice={slice_id} plan={plan_path}")
    gate = run_bounded_gate(repo, slice_id=slice_id)
    if not gate.get("ok"):
        print(f"ppe_ide_build_closeout: gate failed — {gate.get('message')}")
        if gate.get("hint_path"):
            print(f"  hint: {gate.get('hint_path')}")
        return 1

    print(f"ppe_ide_build_closeout: gate OK (attempts={gate.get('attempts')})")
    if args.gate_only:
        return 0

    if (
        subprocess.run(["git", "diff", "--quiet"], cwd=repo, check=False).returncode != 0
        or subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo, check=False).returncode != 0
    ):
        print("ppe_ide_build_closeout: uncommitted changes — commit on build branch before mark_ready")
        return 1

    mark = subprocess.run(
        [str(repo / "mark_ide_product_ready.cmd"), slice_id, plan_path],
        cwd=repo,
        shell=True,
        check=False,
    )
    if mark.returncode != 0:
        return mark.returncode

    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    cur = (branch.stdout or "").strip()
    run_env = os.environ.copy()
    if cur.lower().startswith("build/auto/"):
        run_env["PPE_GIT_SYNC_PULL"] = "0"
        run_env["PPE_GIT_SYNC_PUSH"] = "0"

    return subprocess.run(
        [str(repo / "run_ppe_local.cmd")],
        cwd=repo,
        env=run_env,
        shell=True,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
