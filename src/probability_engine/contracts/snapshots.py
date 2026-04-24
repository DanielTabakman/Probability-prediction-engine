from __future__ import annotations

from dataclasses import dataclass


"""
Snapshot contracts (canonical).

These dataclasses are the canonical internal representation used by the snapshot
normalization layer and the snapshot store implementations.

Anything shaped as TypedDicts (e.g. `contracts/market_rows.py`) or provider payloads
(DataFrames, dicts) is considered external/legacy and should be converted into
these dataclasses via explicit converter functions (see `contracts/convert.py`).
"""


@dataclass(frozen=True, slots=True)
class YahooPriceRow:
    symbol: str
    asset: str | None
    timestamp: str
    close: float | None
    volume: float | None
    as_of: str
    source: str


@dataclass(frozen=True, slots=True)
class PolymarketProbRow:
    event_slug: str
    market_question: str
    outcome: str
    probability: float
    end_date_iso: str | None
    as_of: str
    source: str


@dataclass(frozen=True, slots=True)
class DeribitOptionMarkRow:
    instrument_name: str
    mark_price: float
    as_of: str
    source: str
