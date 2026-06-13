"""
Daily MVP collector for cross-venue probability panel CSV snapshots.

Fetches Polymarket BTC questions + Deribit-aligned spreads (same path as implied lab)
and writes one timestamped CSV under artifacts/cross_venue_snapshots/ by default.
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
    fetch_deribit_btc_option_instruments,
    fetch_deribit_forward_and_iv_for_expiry,
)
from src.data.fetch_polymarket import fetch_polymarket_markets, markets_to_probabilities
from src.data.parse_btc_markets import btc_price_questions_from_polymarket
from src.viz.cross_venue_export import (
    build_cross_venue_panel_rows,
    serialize_cross_venue_export_csv,
)

DEFAULT_SNAPSHOT_ROOT = ROOT / "artifacts" / "cross_venue_snapshots"


def default_snapshot_path(
    *,
    as_of_utc: datetime,
    root: Path = DEFAULT_SNAPSHOT_ROOT,
) -> Path:
    day = as_of_utc.astimezone(UTC).strftime("%Y-%m-%d")
    stamp = as_of_utc.astimezone(UTC).strftime("%H%M%S")
    return root / day / f"ppe_cross_venue_prob_panel_{stamp}Z.csv"


def collect_cross_venue_snapshot(
    *,
    max_questions: int = 8,
    output: Path | None = None,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    spot_fn: Callable[[], float | None] | None = None,
    polymarket_fn: Callable[[], list[dict[str, Any]]] | None = None,
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None] | None = None,
    marks_full_fn: Callable[[int], dict[str, Any]] | None = None,
    instruments_fn: Callable[[], list[dict[str, Any]]] | None = None,
    option_book_marks_fn: Callable[[], dict[str, float]] | None = None,
    now: datetime | None = None,
) -> Path:
    """Build cross-venue rows and write CSV; returns output path."""
    from src.data.fetch_deribit import fetch_deribit_btc_option_marks_by_expiry_full

    spot_loader = spot_fn or _default_spot
    pm_loader = polymarket_fn or _default_polymarket_questions
    fwd_iv_loader = forward_iv_fn or fetch_deribit_forward_and_iv_for_expiry
    marks_loader = marks_full_fn or fetch_deribit_btc_option_marks_by_expiry_full
    instruments_loader = instruments_fn or fetch_deribit_btc_option_instruments
    book_marks_loader = option_book_marks_fn or fetch_deribit_btc_option_book_marks

    run_ts = now or datetime.now(tz=UTC)
    as_of_utc = run_ts.isoformat()
    spot = spot_loader()
    if spot is None or float(spot) <= 0:
        raise RuntimeError("spot price unavailable from Deribit index")

    btc_questions = pm_loader()
    if not btc_questions:
        raise RuntimeError("no Polymarket BTC price questions returned")

    rows = build_cross_venue_panel_rows(
        as_of_utc=as_of_utc,
        spot_usd=float(spot),
        btc_questions=btc_questions,
        forward_iv_fn=fwd_iv_loader,
        marks_full_fn=marks_loader,
        instruments_fn=instruments_loader,
        option_book_marks_fn=book_marks_loader,
        max_questions=max_questions,
    )
    if not rows:
        raise RuntimeError("cross-venue row builder returned no rows")

    out = output or default_snapshot_path(as_of_utc=run_ts, root=snapshot_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")
    return out


def _default_spot() -> float | None:
    return fetch_deribit_btc_index()


def _default_polymarket_questions() -> list[dict[str, Any]]:
    events = fetch_polymarket_markets(active=True, closed=False, limit=150)
    probs = markets_to_probabilities(events)
    return btc_price_questions_from_polymarket(probs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Collect cross-venue probability panel CSV snapshot")
    ap.add_argument("--max-questions", type=int, default=8)
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
