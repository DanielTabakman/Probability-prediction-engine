"""Backtest tradeable-at-first cross-venue gaps vs resolved accuracy."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.cross_venue_backtest import DEFAULT_MIN_SNAPSHOTS, DEFAULT_SNAPSHOT_ROOT, discover_snapshot_csvs
from src.viz.cross_venue_tradeability_backtest import (
    DEFAULT_REPORT_ROOT,
    build_cross_venue_tradeability_backtest_report,
    render_tradeability_backtest_markdown,
    write_tradeability_backtest_reports,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tradeability + accuracy backtest")
    ap.add_argument("--snapshot-root", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    ap.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    ap.add_argument("--min-snapshots", type=int, default=DEFAULT_MIN_SNAPSHOTS)
    args = ap.parse_args(argv)

    paths = discover_snapshot_csvs(args.snapshot_root)
    report = build_cross_venue_tradeability_backtest_report(
        paths,
        min_snapshots=args.min_snapshots,
        as_of_utc=datetime.now(tz=UTC).isoformat(),
    )
    md_path, json_path = write_tradeability_backtest_reports(report, report_root=args.report_root)
    print(render_tradeability_backtest_markdown(report))
    print(f"run_cross_venue_tradeability_backtest: wrote {md_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
