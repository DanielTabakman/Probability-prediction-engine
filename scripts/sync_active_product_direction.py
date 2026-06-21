#!/usr/bin/env python3
"""Propagate ACTIVE_PRODUCT_DIRECTION.json to steering doc marker blocks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sync ACTIVE_PRODUCT_DIRECTION.json to steering docs")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true", help="Print JSON report")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    sys.path.insert(0, str(repo))
    from scripts.active_product_direction import propagate  # noqa: PLC0415

    report = propagate(repo, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        updated = report.get("updated") or []
        skipped = report.get("skipped") or []
        print(f"sync_active_product_direction: pivot={report.get('pivotId')}")
        for rel in updated:
            print(f"  updated: {rel}")
        for item in skipped:
            print(f"  skipped: {item['path']} ({item['reason']})")
        if args.dry_run:
            print("sync_active_product_direction: dry-run — no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
