from __future__ import annotations

"""
Legacy / external row shapes (TypedDict).

These TypedDicts represent older or wire-level shapes used in parts of the codebase.
They are NOT the canonical snapshot representation written to storage.

For snapshotting, convert provider payloads into the canonical dataclasses in
`contracts/snapshots.py` using `contracts/convert.py`.
"""

from typing import Literal, NotRequired, TypedDict

SourceId = Literal["yahoo", "polymarket", "deribit", "derived"]


class YahooPriceRow(TypedDict):
    symbol: str
    asset: str
    timestamp_utc: str
    open: float
    high: float
    low: float
    close: float
    volume: NotRequired[float | int | None]
    source: SourceId
    as_of_utc: str


class PolymarketProbRow(TypedDict):
    event_title: str
    event_slug: str
    market_question: str
    outcome: str
    probability: float  # 0..1
    end_date_iso: NotRequired[str]
    source: SourceId
    as_of_utc: str


class DeribitOptionMarkRow(TypedDict):
    expiry_ts_ms: int
    expiry_date: str  # YYYY-MM-DD
    option_type: Literal["call", "put"]
    strike: float
    mark_btc: float
    source: SourceId
    as_of_utc: str
