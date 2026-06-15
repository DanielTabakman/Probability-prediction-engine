"""Refuse to start a second run_ppe_auto_loop instance on the same desktop."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Single-instance guard for run_ppe_auto_loop")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    _ = args.repo_root.resolve()

    import os

    if os.environ.get("PPE_HEADLESS_SUPERVISED_LOOP", "").strip() == "1":
        return 0

    from scripts.ppe_desktop_operator_stack import is_loop_running

    if is_loop_running():
        print(
            "ppe_loop_singleton: another run_ppe_auto_loop is already running — stop it first",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
