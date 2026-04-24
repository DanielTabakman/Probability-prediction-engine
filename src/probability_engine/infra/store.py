from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable, Protocol

from src.probability_engine.contracts.snapshots import (
    DeribitOptionMarkRow,
    PolymarketProbRow,
    YahooPriceRow,
)

ENABLE_SNAPSHOTS_ENV = "ENABLE_SNAPSHOTS"
SNAPSHOT_DB_PATH_ENV = "SNAPSHOT_DB_PATH"
DEFAULT_SNAPSHOT_DB_PATH = "data/probability_engine.sqlite"


class Store(Protocol):
    def write_yahoo_prices(self, rows: Iterable[YahooPriceRow]) -> None: ...
    def write_polymarket_probs(self, rows: Iterable[PolymarketProbRow]) -> None: ...
    def write_deribit_option_marks(
        self, rows: Iterable[DeribitOptionMarkRow]
    ) -> None: ...


class NullStore:
    def write_yahoo_prices(self, rows: Iterable[YahooPriceRow]) -> None:
        return None

    def write_polymarket_probs(self, rows: Iterable[PolymarketProbRow]) -> None:
        return None

    def write_deribit_option_marks(self, rows: Iterable[DeribitOptionMarkRow]) -> None:
        return None


class SQLiteStore:
    def __init__(self, path: str | None = None) -> None:
        self._path = path or os.environ.get(
            SNAPSHOT_DB_PATH_ENV, DEFAULT_SNAPSHOT_DB_PATH
        )
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS yahoo_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    asset TEXT,
                    timestamp TEXT NOT NULL,
                    close REAL,
                    volume REAL,
                    as_of TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_yahoo_prices_symbol_ts ON yahoo_prices(symbol, timestamp);
                CREATE INDEX IF NOT EXISTS ix_yahoo_prices_as_of ON yahoo_prices(as_of);

                CREATE TABLE IF NOT EXISTS polymarket_probs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_slug TEXT NOT NULL,
                    market_question TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    probability REAL NOT NULL,
                    end_date_iso TEXT,
                    as_of TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_polymarket_probs_slug ON polymarket_probs(event_slug);
                CREATE INDEX IF NOT EXISTS ix_polymarket_probs_as_of ON polymarket_probs(as_of);

                CREATE TABLE IF NOT EXISTS deribit_option_marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instrument_name TEXT NOT NULL,
                    mark_price REAL NOT NULL,
                    as_of TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_deribit_option_marks_inst ON deribit_option_marks(instrument_name);
                CREATE INDEX IF NOT EXISTS ix_deribit_option_marks_as_of ON deribit_option_marks(as_of);
                """
            )

    def write_yahoo_prices(self, rows: Iterable[YahooPriceRow]) -> None:
        data = [
            (r.symbol, r.asset, r.timestamp, r.close, r.volume, r.as_of, r.source)
            for r in rows
        ]
        if not data:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO yahoo_prices (symbol, asset, timestamp, close, volume, as_of, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )

    def write_polymarket_probs(self, rows: Iterable[PolymarketProbRow]) -> None:
        data = [
            (
                r.event_slug,
                r.market_question,
                r.outcome,
                r.probability,
                r.end_date_iso,
                r.as_of,
                r.source,
            )
            for r in rows
        ]
        if not data:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO polymarket_probs (event_slug, market_question, outcome, probability, end_date_iso, as_of, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )

    def write_deribit_option_marks(self, rows: Iterable[DeribitOptionMarkRow]) -> None:
        data = [(r.instrument_name, r.mark_price, r.as_of, r.source) for r in rows]
        if not data:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO deribit_option_marks (instrument_name, mark_price, as_of, source)
                VALUES (?, ?, ?, ?)
                """,
                data,
            )


def store_from_env() -> Store:
    enabled = os.environ.get(ENABLE_SNAPSHOTS_ENV, "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if not enabled:
        return NullStore()
    return SQLiteStore()
