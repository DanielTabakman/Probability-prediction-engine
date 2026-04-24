from __future__ import annotations

"""
Converters into the canonical snapshot contracts.

Canonical representation (internal):
- Dataclasses in `src.probability_engine.contracts.snapshots`

External / legacy / wire representations:
- Provider payloads (dicts, DataFrames, etc.)
- Historical TypedDict shapes in `src.probability_engine.contracts.market_rows`

This module provides best-effort converters that:
- never raise on malformed rows (they skip them)
- preserve existing runtime behavior in snapshotting code paths (UI should not break)
"""

from datetime import datetime, timezone
from typing import Any, Iterable

import pandas as pd

from src.probability_engine.contracts.snapshots import (
    DeribitOptionMarkRow,
    PolymarketProbRow,
    YahooPriceRow,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_yahoo_prices_df(
    df: pd.DataFrame, *, source: str = "yahoo", as_of: str | None = None
) -> list[YahooPriceRow]:
    """
    Convert a Yahoo prices DataFrame into canonical `YahooPriceRow` dataclasses.

    Expected columns (best-effort): symbol, asset, timestamp, close, volume
    """
    if df is None or getattr(df, "empty", True):
        return []

    as_of_ = as_of or _utc_now_iso()
    out: list[YahooPriceRow] = []

    for _, row in df.iterrows():
        symbol = row.get("symbol")
        ts = row.get("timestamp")
        if not symbol or ts is None:
            continue

        asset = row.get("asset")
        close = row.get("close", None)
        volume = row.get("volume", None)

        try:
            ts_iso = pd.to_datetime(ts, utc=True).isoformat()
        except Exception:
            ts_iso = str(ts)

        out.append(
            YahooPriceRow(
                symbol=str(symbol),
                asset=str(asset) if asset is not None else None,
                timestamp=ts_iso,
                close=float(close) if close is not None else None,
                volume=float(volume) if volume is not None else None,
                as_of=as_of_,
                source=source,
            )
        )

    return out


def normalize_polymarket_prob_dict_rows(
    rows: Iterable[dict[str, Any]], *, source: str = "polymarket", as_of: str | None = None
) -> list[PolymarketProbRow]:
    """
    Convert Polymarket probability rows (dicts) into canonical `PolymarketProbRow`.

    Expected keys (best-effort): event_slug, market_question, outcome, probability, end_date_iso
    """
    as_of_ = as_of or _utc_now_iso()
    out: list[PolymarketProbRow] = []

    for r in rows or []:
        try:
            prob = float(r.get("probability"))
        except (TypeError, ValueError):
            continue

        event_slug = str(r.get("event_slug") or "")
        market_question = str(r.get("market_question") or "")
        outcome = str(r.get("outcome") or "")
        if not event_slug or not market_question or not outcome:
            continue

        end_date_iso = r.get("end_date_iso")
        out.append(
            PolymarketProbRow(
                event_slug=event_slug,
                market_question=market_question,
                outcome=outcome,
                probability=prob,
                end_date_iso=str(end_date_iso) if end_date_iso else None,
                as_of=as_of_,
                source=source,
            )
        )

    return out


def normalize_deribit_book_marks(
    book_marks: dict[str, float] | None, *, source: str = "deribit", as_of: str | None = None
) -> list[DeribitOptionMarkRow]:
    """
    Convert Deribit book marks mapping into canonical `DeribitOptionMarkRow`.

    Expected shape: { instrument_name: mark_price }
    """
    if not isinstance(book_marks, dict) or not book_marks:
        return []

    as_of_ = as_of or _utc_now_iso()
    out: list[DeribitOptionMarkRow] = []

    for inst, mark in book_marks.items():
        if not inst:
            continue
        try:
            mark_f = float(mark)
        except (TypeError, ValueError):
            continue

        out.append(
            DeribitOptionMarkRow(
                instrument_name=str(inst),
                mark_price=mark_f,
                as_of=as_of_,
                source=source,
            )
        )

    return out

