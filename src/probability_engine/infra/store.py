from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable, Protocol

from src.probability_engine.contracts.canonical_events import (
    CanonicalEvent,
    ProbabilityObservation,
)
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
        conn = self._connect()
        try:
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

                -- Canonical events + probability time series (additive).
                CREATE TABLE IF NOT EXISTS canonical_events (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    asset TEXT,
                    threshold REAL,
                    resolution_date TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_canonical_events_type ON canonical_events(type);
                CREATE INDEX IF NOT EXISTS ix_canonical_events_asset ON canonical_events(asset);

                CREATE TABLE IF NOT EXISTS probability_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canonical_event_id TEXT NOT NULL,
                    probability REAL NOT NULL,
                    source TEXT NOT NULL,
                    as_of_utc TEXT NOT NULL,
                    raw_ref TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(canonical_event_id) REFERENCES canonical_events(id)
                );
                CREATE INDEX IF NOT EXISTS ix_prob_obs_event_asof ON probability_observations(canonical_event_id, as_of_utc);
                CREATE INDEX IF NOT EXISTS ix_prob_obs_source_asof ON probability_observations(source, as_of_utc);
                """
            )
            conn.commit()
        finally:
            conn.close()

    def write_yahoo_prices(self, rows: Iterable[YahooPriceRow]) -> None:
        data = [
            (r.symbol, r.asset, r.timestamp, r.close, r.volume, r.as_of, r.source)
            for r in rows
        ]
        if not data:
            return
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO yahoo_prices (symbol, asset, timestamp, close, volume, as_of, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

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
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO polymarket_probs (event_slug, market_question, outcome, probability, end_date_iso, as_of, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def write_deribit_option_marks(self, rows: Iterable[DeribitOptionMarkRow]) -> None:
        data = [(r.instrument_name, r.mark_price, r.as_of, r.source) for r in rows]
        if not data:
            return
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO deribit_option_marks (instrument_name, mark_price, as_of, source)
                VALUES (?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def upsert_canonical_events(self, events: Iterable[CanonicalEvent]) -> None:
        data = [
            (e.id, e.type, e.asset, e.threshold, e.resolution_date, e.description)
            for e in events
        ]
        if not data:
            return
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO canonical_events (id, type, asset, threshold, resolution_date, description)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    asset=excluded.asset,
                    threshold=excluded.threshold,
                    resolution_date=excluded.resolution_date,
                    description=excluded.description,
                    updated_at=CURRENT_TIMESTAMP
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def write_probability_observations(
        self, observations: Iterable[ProbabilityObservation]
    ) -> None:
        data = [
            (o.canonical_event_id, o.probability, o.source, o.as_of_utc, o.raw_ref)
            for o in observations
        ]
        if not data:
            return
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT INTO probability_observations (canonical_event_id, probability, source, as_of_utc, raw_ref)
                VALUES (?, ?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()
        finally:
            conn.close()

    def read_probability_observations(
        self, canonical_event_id: str, limit: int | None = None
    ) -> list[ProbabilityObservation]:
        sql = """
            SELECT canonical_event_id, probability, source, as_of_utc, raw_ref
            FROM probability_observations
            WHERE canonical_event_id = ?
            ORDER BY as_of_utc ASC, id ASC
        """
        params: list[object] = [canonical_event_id]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))

        conn = self._connect()
        try:
            rows = conn.execute(sql, params).fetchall()
        finally:
            conn.close()
        return [
            ProbabilityObservation(
                canonical_event_id=r[0],
                probability=float(r[1]),
                source=r[2],
                as_of_utc=r[3],
                raw_ref=r[4],
            )
            for r in rows
        ]


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
