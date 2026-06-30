"""Dev loop: collect cross-venue snapshots at high cadence for pipeline smoke."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collect_cross_venue_snapshot import collect_cross_venue_snapshot  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dev cross-venue collector loop")
    ap.add_argument("--interval", type=int, default=300, help="Seconds between snapshots (default 300)")
    ap.add_argument("--count", type=int, default=12, help="Number of snapshots (default 12)")
    ap.add_argument("--max-questions", type=int, default=8)
    ap.add_argument(
        "--snapshot-root",
        type=Path,
        default=ROOT / "artifacts" / "cross_venue_snapshots",
    )
    args = ap.parse_args(argv)

    if args.count < 1:
        print("run_cross_venue_collector_dev: count must be >= 1", file=sys.stderr)
        return 1
    if args.interval < 1:
        print("run_cross_venue_collector_dev: interval must be >= 1", file=sys.stderr)
        return 1

    paths: list[Path] = []
    for i in range(args.count):
        try:
            out = collect_cross_venue_snapshot(
                max_questions=args.max_questions,
                snapshot_root=args.snapshot_root,
            )
        except RuntimeError as exc:
            print(f"run_cross_venue_collector_dev: {exc}", file=sys.stderr)
            return 1
        paths.append(out)
        print(f"run_cross_venue_collector_dev: [{i + 1}/{args.count}] wrote {out}")
        if i + 1 < args.count:
            time.sleep(args.interval)

    print(f"run_cross_venue_collector_dev: done — {len(paths)} snapshot(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
