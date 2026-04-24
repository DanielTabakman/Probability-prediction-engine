from __future__ import annotations

from typing import Any

import pandas as pd

from src.data.fetch_polymarket import markets_to_probabilities
from src.data.fetch_polymarket import fetch_polymarket_markets as _fetch_polymarket_markets
from src.data.fetch_yahoo import fetch_yahoo_prices as _fetch_yahoo_prices
from src.probability_engine.infra.store import Store
from src.probability_engine.services.snapshots import (
    write_deribit_option_marks_snapshot,
    write_polymarket_probs_snapshot,
    write_yahoo_prices_snapshot,
)


def get_yahoo_prices(
    symbols: dict[str, list[str]] | None,
    period: str,
    *,
    store: Store | None = None,
) -> pd.DataFrame:
    """
    Service seam for Yahoo market prices.

    Keeps behavior stable: returns the raw fetcher DataFrame, and snapshotting is best-effort.
    """
    df = _fetch_yahoo_prices(symbols=symbols, period=period)
    try:
        write_yahoo_prices_snapshot(df, store=store)
    except Exception:
        # Preserve prior behavior: snapshotting should never break the UI.
        pass
    return df


def get_polymarket_markets(
    active: bool,
    closed: bool,
    limit: int,
    *,
    store: Store | None = None,
) -> list[dict[str, Any]]:
    """
    Service seam for Polymarket events/markets.

    Keeps behavior stable: returns the raw Gamma events list. If snapshots are enabled,
    also writes a derived probability snapshot (best-effort) for later analysis.
    """
    events = _fetch_polymarket_markets(active=active, closed=closed, limit=limit)
    try:
        probs = markets_to_probabilities(events) if events else []
        write_polymarket_probs_snapshot(probs, store=store)
    except Exception:
        # Preserve UI behavior: snapshotting is optional and must not break fetch.
        pass
    return events


def snapshot_deribit_option_book_marks(
    book_marks: dict[str, float] | None,
    *,
    store: Store | None = None,
) -> None:
    """
    Best-effort snapshot helper for Deribit option book marks.

    This keeps the `src/viz/app_cache.py` cache wrapper thin while ensuring
    snapshotting stays outside the UI layer.
    """
    try:
        write_deribit_option_marks_snapshot(book_marks, store=store)
    except Exception:
        pass

