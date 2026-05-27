"""Local SQLite persistence for MVP1 friends-first tester feedback (§15F rubric)."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Master §15F tester result categories (confusion + value/feature signals).
CONFUSION_CATEGORIES: tuple[str, ...] = (
    "naming confusion",
    "market-read confusion",
    "trust/provenance confusion",
    "belief-control confusion",
    "candidate/recommendation confusion",
    "no-trade/watch-only confusion",
    "layout/visual hierarchy confusion",
    "value/desirability signal",
    "feature request / later-scope item",
)

LIKERT_MIN = 1
LIKERT_MAX = 5

_DB_ENV = "PPE_FEEDBACK_DB_PATH"
_DEFAULT_REL = Path("data") / "ppe_mvp1_feedback.sqlite3"


def default_db_path() -> Path:
    raw = (os.environ.get(_DB_ENV) or "").strip()
    if raw:
        return Path(raw).expanduser()
    repo = Path(__file__).resolve().parents[2]
    return repo / _DEFAULT_REL


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mvp1_feedback (
            id TEXT PRIMARY KEY,
            created_at_utc TEXT NOT NULL,
            confusion_category TEXT NOT NULL,
            usefulness INTEGER NOT NULL,
            repeat_use_intent INTEGER NOT NULL,
            objections_text TEXT,
            session_note TEXT,
            context_json TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_mvp1_feedback_created ON mvp1_feedback(created_at_utc DESC)"
    )
    conn.commit()


def _validate_likert(value: int, *, field: str) -> None:
    if not isinstance(value, int) or value < LIKERT_MIN or value > LIKERT_MAX:
        raise ValueError(
            f"invalid {field} {value!r}; expected integer in [{LIKERT_MIN}, {LIKERT_MAX}]"
        )


def insert_feedback(
    conn: sqlite3.Connection,
    *,
    confusion_category: str,
    usefulness: int,
    repeat_use_intent: int,
    objections_text: str | None = None,
    session_note: str | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    init_schema(conn)
    cat = (confusion_category or "").strip()
    if cat not in CONFUSION_CATEGORIES:
        raise ValueError(
            f"invalid confusion_category {cat!r}; expected one of {CONFUSION_CATEGORIES}"
        )
    _validate_likert(usefulness, field="usefulness")
    _validate_likert(repeat_use_intent, field="repeat_use_intent")
    objections = (objections_text or "").strip() or None
    note = (session_note or "").strip() or None
    if note and len(note) > 500:
        note = note[:500]
    if objections and len(objections) > 4000:
        objections = objections[:4000]
    ctx_json = None
    if context:
        ctx_json = json.dumps(context, separators=(",", ":"), ensure_ascii=False)
    rid = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO mvp1_feedback
        (id, created_at_utc, confusion_category, usefulness, repeat_use_intent,
         objections_text, session_note, context_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (rid, _utc_iso(), cat, int(usefulness), int(repeat_use_intent), objections, note, ctx_json),
    )
    conn.commit()
    return rid


def list_recent(conn: sqlite3.Connection, *, limit: int = 50) -> list[dict[str, Any]]:
    init_schema(conn)
    cur = conn.execute(
        """
        SELECT id, created_at_utc, confusion_category, usefulness, repeat_use_intent,
               objections_text, session_note
        FROM mvp1_feedback
        ORDER BY created_at_utc DESC
        LIMIT ?
        """,
        (int(limit),),
    )
    return [dict(row) for row in cur.fetchall()]


def open_store(path: Path | None = None) -> sqlite3.Connection:
    p = path or default_db_path()
    c = _connect(p)
    init_schema(c)
    return c
