"""Loop wrapper helper: keep alive vs exit on guard stop (exit code 7)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_operator_config import guard_stop_sleep_seconds, keep_loop_alive_on_guard_stop


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Guard-stop loop policy")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if keep_loop_alive_on_guard_stop(repo):
        print(guard_stop_sleep_seconds(repo))
        return 0
    print(-1)
    return 7


if __name__ == "__main__":
    raise SystemExit(main())
