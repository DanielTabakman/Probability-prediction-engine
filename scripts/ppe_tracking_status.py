"""CLI for unified tracking status report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_tracking_hub import (
    collect_tracking_snapshot,
    format_operator_tracking_lines,
    write_tracking_artifacts,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE unified tracking status (factory + product signals)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true", help="Print JSON snapshot to stdout")
    ap.add_argument("--brief", action="store_true", help="One-line operator summary")
    ap.add_argument("--no-write", action="store_true", help="Skip writing TRACKING_STATUS artifacts")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    snap = collect_tracking_snapshot(repo, days=args.days)

    if not args.no_write:
        json_path, md_path = write_tracking_artifacts(repo, snap)
        if not args.json and not args.brief:
            print(f"ppe_tracking_status: wrote {json_path}")
            print(f"ppe_tracking_status: wrote {md_path}")

    if args.json:
        print(json.dumps(snap, indent=2))
    elif args.brief:
        lines = format_operator_tracking_lines(repo, days=args.days)
        print(" | ".join(lines) if lines else "tracking: (no signals)")
    else:
        for line in format_operator_tracking_lines(repo, days=args.days):
            print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
