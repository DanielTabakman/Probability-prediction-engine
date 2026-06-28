"""Score cross-venue snapshot history: Brier scores and gap-bucket calibration."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.cross_venue_backtest import (  # noqa: E402
    DEFAULT_MIN_SNAPSHOTS,
    DEFAULT_REPORT_ROOT,
    DEFAULT_SNAPSHOT_ROOT,
    build_cross_venue_backtest_report,
    discover_snapshot_csvs,
    render_cross_venue_backtest_markdown,
    write_cross_venue_backtest_reports,
)


def run_cross_venue_backtest(
    *,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
    min_snapshots: int = DEFAULT_MIN_SNAPSHOTS,
) -> tuple[dict[str, Any], Path, Path]:
    csv_paths = discover_snapshot_csvs(snapshot_root)
    report = build_cross_venue_backtest_report(
        csv_paths,
        min_snapshots=min_snapshots,
        as_of_utc=datetime.now(tz=UTC).isoformat(),
    )
    md_path, json_path = write_cross_venue_backtest_reports(report, report_root=report_root)
    return report, md_path, json_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Backtest cross-venue gap signals from snapshots")
    ap.add_argument("--snapshot-root", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    ap.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    ap.add_argument("--min-snapshots", type=int, default=DEFAULT_MIN_SNAPSHOTS)
    args = ap.parse_args(argv)

    report, md_path, json_path = run_cross_venue_backtest(
        snapshot_root=args.snapshot_root,
        report_root=args.report_root,
        min_snapshots=args.min_snapshots,
    )

    if not report.get("snapshot_files"):
        print(f"run_cross_venue_backtest: no snapshots under {args.snapshot_root}", file=sys.stderr)
    elif report.get("resolved_count", 0) == 0:
        print(
            f"run_cross_venue_backtest: no resolved questions yet "
            f"(pending={report.get('pending_count', 0)}; need >= {args.min_snapshots} snapshots)",
            file=sys.stderr,
        )

    print(render_cross_venue_backtest_markdown(report))
    print(f"run_cross_venue_backtest: wrote {md_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
