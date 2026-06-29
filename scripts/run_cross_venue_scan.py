"""Rank cross-venue probability gaps and write scan reports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collect_cross_venue_snapshot import collect_cross_venue_snapshot  # noqa: E402
from src.viz.cross_venue_backtest import (  # noqa: E402
    DEFAULT_SNAPSHOT_ROOT,
    find_latest_snapshot_csv,
    load_cross_venue_snapshot_csv,
)
from src.viz.cross_venue_scan import (  # noqa: E402
    DEFAULT_REPORT_ROOT,
    build_cross_venue_scan_report,
    render_cross_venue_scan_markdown,
    write_cross_venue_scan_reports,
)


def run_cross_venue_scan(
    *,
    rows: list[dict[str, str]],
    min_gap: float = 0.0,
    top: int | None = None,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> tuple[dict[str, Any], Path, Path]:
    report = build_cross_venue_scan_report(rows, min_abs_gap_pct=min_gap, max_rows=top)
    md_path, json_path = write_cross_venue_scan_reports(report, report_root=report_root)
    return report, md_path, json_path


def _configure_stdio_utf8() -> None:
    """Avoid UnicodeEncodeError on Windows cp1252 consoles (e.g. minus sign in gap table)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main(argv: list[str] | None = None) -> int:
    _configure_stdio_utf8()
    ap = argparse.ArgumentParser(description="Rank cross-venue probability gaps")
    ap.add_argument("--from-snapshot", type=Path, default=None)
    ap.add_argument("--latest-snapshot", action="store_true")
    ap.add_argument("--snapshot-root", type=Path, default=DEFAULT_SNAPSHOT_ROOT)
    ap.add_argument("--min-gap", type=float, default=0.0)
    ap.add_argument("--top", type=int, default=None)
    ap.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    ap.add_argument("--save-snapshot", action="store_true")
    ap.add_argument("--max-questions", type=int, default=8)
    args = ap.parse_args(argv)

    try:
        if args.from_snapshot is not None:
            rows = load_cross_venue_snapshot_csv(args.from_snapshot)
        elif args.latest_snapshot:
            latest = find_latest_snapshot_csv(args.snapshot_root)
            if latest is None:
                raise RuntimeError(f"no snapshots under {args.snapshot_root}")
            rows = load_cross_venue_snapshot_csv(latest)
        elif args.save_snapshot:
            snap_path = collect_cross_venue_snapshot(
                max_questions=args.max_questions,
                snapshot_root=args.snapshot_root,
            )
            rows = load_cross_venue_snapshot_csv(snap_path)
        else:
            from datetime import UTC, datetime

            from scripts.collect_cross_venue_snapshot import _btc_questions_from_polymarket
            from src.data.fetch_deribit import (
                fetch_deribit_btc_index,
                fetch_deribit_btc_option_book_marks,
                fetch_deribit_btc_option_marks_by_expiry_full,
                fetch_deribit_btc_options_instruments,
                fetch_deribit_forward_and_iv_for_expiry,
            )
            from src.data.fetch_polymarket import fetch_polymarket_markets
            from src.viz.cross_venue_export import build_cross_venue_panel_rows

            spot = fetch_deribit_btc_index()
            if spot is None or float(spot) <= 0:
                raise RuntimeError("spot price unavailable from Deribit index")
            btc_questions = _btc_questions_from_polymarket(
                polymarket_fn=fetch_polymarket_markets,
                topic_keywords=("bitcoin", "btc"),
                limit=150,
            )
            if not btc_questions:
                raise RuntimeError("no BTC Polymarket price-target questions returned")
            rows = build_cross_venue_panel_rows(
                as_of_utc=datetime.now(tz=UTC).isoformat(),
                spot_usd=float(spot),
                btc_questions=btc_questions,
                forward_iv_fn=fetch_deribit_forward_and_iv_for_expiry,
                marks_full_fn=fetch_deribit_btc_option_marks_by_expiry_full,
                instruments_fn=lambda: fetch_deribit_btc_options_instruments(expired=False),
                option_book_marks_fn=fetch_deribit_btc_option_book_marks,
                max_questions=args.max_questions,
            )

        if not rows:
            raise RuntimeError("no cross-venue rows to scan")

        report, md_path, json_path = run_cross_venue_scan(
            rows=rows,
            min_gap=args.min_gap,
            top=args.top,
            report_root=args.report_root,
        )
    except RuntimeError as exc:
        print(f"run_cross_venue_scan: {exc}", file=sys.stderr)
        return 1

    print(render_cross_venue_scan_markdown(report))
    print(f"run_cross_venue_scan: wrote {md_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
