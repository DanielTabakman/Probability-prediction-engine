"""Portable sleep for loop wrappers (avoids `timeout` failures in redirected terminals)."""

from __future__ import annotations

import argparse
import sys
import time


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sleep N seconds for operator loop wrappers")
    ap.add_argument("seconds", type=int, help="Sleep duration in seconds")
    args = ap.parse_args(argv)
    seconds = max(1, int(args.seconds))
    time.sleep(seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
