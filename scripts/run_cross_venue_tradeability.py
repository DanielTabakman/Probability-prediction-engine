"""Score cross-venue gaps for tradeability after spread proxy costs."""

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
    DEFAULT_SNAPSHOT_ROOT,
    find_latest_snapshot_csv,
    load_cross_venue_snapshot_csv,
)
from src.viz.cross_venue_tradeability import (  # noqa: E402
    DEFAULT_REPORT_ROOT,
    build_cross_venue_tradeability_report,
    render_cross_venue_tradeability_markdown,
    write_cross_venue_tradeability_reports,
)


def run_cross_venue_tradeability(
    *,
    rows: list[dict[str, str]] | None = None,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> tuple[dict[str, Any], Path, Path]:
    if rows is None:
        latest = find_latest_snapshot_csv(snapshot_root)
        if latest is None:
            raise RuntimeError(f"no snapshots under {snapshot_root}")
        rows = load_cross_venue_snapshot_csv(latest)
    report = build_cross_venue_tradeability_report(
        rows,
        as_of_utc=datetime.now(tz=UTC).isoformat(),
    )
    md_path, json_path = write_cross_venue_tradeability_reports(report, report_root=report_root)
    return report, md_path, json_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cross-venue tradeability after spread proxy")
    ap.add_argument("--from-snapshot", type=Path, default=None)
    ap.add_argument("--latest-snapshot", action="store_true")
    ap.add_argument("--snapshot-root", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    ap.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    args = ap.parse_args(argv)

    try:
        if args.from_snapshot is not None:
            rows = load_cross_venue_snapshot_csv(args.from_snapshot)
            report, md_path, json_path = run_cross_venue_tradeability(
                rows=rows,
                report_root=args.report_root,
            )
        else:
            report, md_path, json_path = run_cross_venue_tradeability(
                snapshot_root=args.snapshot_root,
                report_root=args.report_root,
            )
    except RuntimeError as exc:
        print(f"run_cross_venue_tradeability: {exc}", file=sys.stderr)
        return 1

    print(render_cross_venue_tradeability_markdown(report))
    print(f"run_cross_venue_tradeability: wrote {md_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
