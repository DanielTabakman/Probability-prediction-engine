"""
SQLite schema for prices, canonical events, and implied probabilities.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH_ENV = "DB_PATH"
DEFAULT_DB_PATH = "data/engine.db"


def get_db_path() -> str:
    return os.environ.get(DB_PATH_ENV, DEFAULT_DB_PATH)


def init_db(path: str | None = None) -> sqlite3.Connection:
    path = path or get_db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            asset TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_market_prices_symbol_ts ON market_prices(symbol, timestamp);
        CREATE INDEX IF NOT EXISTS ix_market_prices_asset_ts ON market_prices(asset, timestamp);

        CREATE TABLE IF NOT EXISTS prediction_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_title TEXT,
            event_slug TEXT,
            end_date_iso TEXT,
            market_question TEXT,
            outcome TEXT,
            probability REAL NOT NULL,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_prediction_prices_source ON prediction_prices(source);
        CREATE INDEX IF NOT EXISTS ix_prediction_prices_fetched ON prediction_prices(fetched_at);

        CREATE TABLE IF NOT EXISTS canonical_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            description TEXT,
            asset TEXT NOT NULL,
            threshold REAL,
            resolution_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS event_probabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_event_id TEXT NOT NULL,
            source TEXT NOT NULL,
            probability REAL NOT NULL,
            raw_identifier TEXT,
            observed_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_event_probabilities_event ON event_probabilities(canonical_event_id);
    """)
    conn.commit()
    return conn
