"""Run tiered tests (local convenience wrapper).

This does NOT change the canonical commit/CI policy; it just makes it easy to run:
- tier0: ruff + pytest
- tier1: tier0 + single UI smoke
- tier2: tier0 + dual smoke
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path) -> int:
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=cwd).returncode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run PPE test tiers (local wrapper).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--tier", type=int, choices=(0, 1, 2), default=0)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    tier = int(args.tier)

    cmds: list[list[str]] = [
        ["python", "-m", "ruff", "check", "src", "tests", "scripts"],
        ["python", "-m", "pytest", "-q"],
    ]
    if tier == 1:
        cmds.append(["python", "scripts/run_implied_lab_ui_smoke.py"])
    if tier == 2:
        cmds.append(["python", "scripts/run_mvp1_dual_implied_lab_smoke.py"])

    for c in cmds:
        rc = _run(c, cwd=repo)
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

