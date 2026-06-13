"""
Daily collector for cross-venue probability panel CSV snapshots.

Fetches live Polymarket BTC questions + Deribit option marks (same path as
implied-lab download) and writes one timestamped CSV under
artifacts/cross_venue_snapshots/ by default.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.fetch_deribit import (
    fetch_deribit_btc_index,
    fetch_deribit_btc_option_book_marks,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_btc_options_instruments,
    fetch_deribit_forward_and_iv_for_expiry,
)
from src.data.fetch_polymarket import fetch_polymarket_markets, markets_to_probabilities
from src.data.parse_btc_markets import btc_price_questions_from_polymarket
from src.viz.cross_venue_export import (
    build_cross_venue_panel_rows,
    serialize_cross_venue_export_csv,
)

DEFAULT_SNAPSHOT_ROOT = ROOT / "artifacts" / "cross_venue_snapshots"
DEFAULT_TOPIC_KEYWORDS = ("bitcoin", "btc")


def default_snapshot_path(
    *,
    as_of_utc: datetime,
    root: Path = DEFAULT_SNAPSHOT_ROOT,
) -> Path:
    day = as_of_utc.astimezone(UTC).strftime("%Y-%m-%d")
    stamp = as_of_utc.astimezone(UTC).strftime("%H%M%S")
    return root / day / f"ppe_cross_venue_prob_panel_{stamp}Z.csv"


def _btc_questions_from_polymarket(
    *,
    polymarket_fn: Callable[[bool, bool, int], list[dict[str, Any]]],
    topic_keywords: tuple[str, ...],
    limit: int,
) -> list[dict[str, Any]]:
    events = polymarket_fn(True, False, limit) or []
    if not events:
        return []
    probs = markets_to_probabilities(events, topic_keywords=list(topic_keywords))
    return btc_price_questions_from_polymarket(probs) if probs else []


def collect_cross_venue_snapshot(
    *,
    max_questions: int = 8,
    polymarket_limit: int = 150,
    topic_keywords: tuple[str, ...] = DEFAULT_TOPIC_KEYWORDS,
    output: Path | None = None,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    spot_fn: Callable[[], float | None] | None = None,
    polymarket_fn: Callable[[bool, bool, int], list[dict[str, Any]]] | None = None,
    instruments_fn: Callable[[], list[dict[str, Any]]] | None = None,
    option_book_marks_fn: Callable[[], dict[str, float]] | None = None,
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None] | None = None,
    marks_full_fn: Callable[[int], dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> Path:
    """Build cross-venue panel rows and write CSV; returns output path."""
    spot_loader = spot_fn or fetch_deribit_btc_index
    pm_loader = polymarket_fn or fetch_polymarket_markets
    inst_loader = instruments_fn or (lambda: fetch_deribit_btc_options_instruments(expired=False))
    marks_loader = option_book_marks_fn or fetch_deribit_btc_option_book_marks
    fwd_iv_loader = forward_iv_fn or fetch_deribit_forward_and_iv_for_expiry
    marks_full_loader = marks_full_fn or fetch_deribit_btc_option_marks_by_expiry_full

    run_ts = now or datetime.now(tz=UTC)
    as_of_utc = run_ts.isoformat()

    spot = spot_loader()
    if spot is None or float(spot) <= 0:
        raise RuntimeError("spot price unavailable from Deribit index")

    btc_questions = _btc_questions_from_polymarket(
        polymarket_fn=pm_loader,
        topic_keywords=topic_keywords,
        limit=polymarket_limit,
    )
    if not btc_questions:
        raise RuntimeError("no BTC Polymarket price-target questions returned")

    rows = build_cross_venue_panel_rows(
        as_of_utc=as_of_utc,
        spot_usd=float(spot),
        btc_questions=btc_questions,
        forward_iv_fn=fwd_iv_loader,
        marks_full_fn=marks_full_loader,
        instruments_fn=inst_loader,
        option_book_marks_fn=marks_loader,
        max_questions=max_questions,
    )
    if not rows:
        raise RuntimeError("cross-venue panel builder returned no rows")

    out = output or default_snapshot_path(as_of_utc=run_ts, root=snapshot_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Collect cross-venue probability panel CSV snapshot")
    ap.add_argument("--max-questions", type=int, default=8)
    ap.add_argument("--polymarket-limit", type=int, default=150)
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="CSV output path (default: artifacts/cross_venue_snapshots/YYYY-MM-DD/...)",
    )
    ap.add_argument(
        "--snapshot-root",
        type=Path,
        default=DEFAULT_SNAPSHOT_ROOT,
        help="Root directory for dated snapshot folders",
    )
    args = ap.parse_args(argv)

    try:
        out = collect_cross_venue_snapshot(
            max_questions=args.max_questions,
            polymarket_limit=args.polymarket_limit,
            output=args.output,
            snapshot_root=args.snapshot_root,
        )
    except RuntimeError as exc:
        print(f"collect_cross_venue_snapshot: {exc}", file=sys.stderr)
        return 1

    print(f"collect_cross_venue_snapshot: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
