#!/usr/bin/env python3
"""Scheduled warm for ppe_display_api (cache ops meta infra).

Usage (cron / compose sidecar):
  python scripts/run_display_cache_refresh.py
  python scripts/run_display_cache_refresh.py --base-url http://127.0.0.1:8765
  python scripts/run_display_cache_refresh.py --loop --base-url http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.warm_display_payload_cache import main as warm_main  # noqa: E402
from src.viz.display_payload_cache import display_cache_refresh_seconds  # noqa: E402


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Warm display payload cache on a schedule")
    ap.add_argument(
        "--base-url",
        default="",
        help="HTTP base for ppe_display_api (default: in-process build)",
    )
    ap.add_argument(
        "--loop",
        action="store_true",
        help="Run warm repeatedly every PPE_DISPLAY_CACHE_REFRESH_SECONDS",
    )
    ap.add_argument("--json", action="store_true", help="Pass --json to warm script")
    return ap.parse_args(argv)


def _warm_once(args: argparse.Namespace) -> int:
    warm_argv: list[str] = []
    if args.base_url:
        warm_argv.extend(["--base-url", args.base_url])
    if args.json:
        warm_argv.append("--json")
    return warm_main(warm_argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.loop:
        return _warm_once(args)

    interval = display_cache_refresh_seconds()
    target = args.base_url or "in-process"
    print(
        f"run_display_cache_refresh: loop interval={interval}s target={target}",
        file=sys.stderr,
    )
    while True:
        rc = _warm_once(args)
        if rc != 0:
            print(f"run_display_cache_refresh: warm failed exit={rc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
