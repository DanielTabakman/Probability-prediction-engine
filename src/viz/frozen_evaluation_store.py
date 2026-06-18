"""SQLite persistence for frozen implied-lab evaluation records."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.viz.frozen_evaluation_record import summary_line_for_record

REVIEW_STATUSES: tuple[str, ...] = (
    "pending",
    "supportive",
    "contradictory",
    "contaminated",
    "not_judgeable",
)

_DB_ENV = "PPE_SNAPSHOT_DB_PATH"
_DEFAULT_REL = Path("data") / "ppe_frozen_evaluations.sqlite3"
_ACCESS_EMAIL_HEADER_NAMES: tuple[str, ...] = (
    "Cf-Access-Authenticated-User-Email",
    "cf-access-authenticated-user-email",
    "X-Forwarded-Email",
    "x-forwarded-email",
)


def normalize_owner_email(raw: str | None) -> str | None:
    email = (raw or "").strip().lower()
    return email or None


def resolve_snapshot_owner_email() -> str | None:
    """Cloudflare Access email from dev override, WSGI env, or Streamlit request headers."""
    for env_key in ("PPE_SNAPSHOT_OWNER_EMAIL", "PPE_OWNER_EMAIL", "MSOS_IDENTITY_EMAIL"):
        email = normalize_owner_email(os.environ.get(env_key))
        if email:
            return email
    for wsgi_key in ("HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL", "HTTP_X_FORWARDED_EMAIL"):
        email = normalize_owner_email(os.environ.get(wsgi_key))
        if email:
            return email
    try:
        import streamlit as st

        ctx = getattr(st, "context", None)
        headers = getattr(ctx, "headers", None) if ctx is not None else None
        if headers is not None:
            for name in _ACCESS_EMAIL_HEADER_NAMES:
                raw = headers.get(name) if hasattr(headers, "get") else None
                email = normalize_owner_email(str(raw) if raw is not None else None)
                if email:
                    return email
    except Exception:
        pass
    return None


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
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _snapshot_reviews_has_fk(conn: sqlite3.Connection) -> bool:
    rows = conn.execute("PRAGMA foreign_key_list(snapshot_reviews)").fetchall()
    return len(rows) > 0


def _frozen_evaluations_has_owner_email(conn: sqlite3.Connection) -> bool:
    rows = conn.execute("PRAGMA table_info(frozen_evaluations)").fetchall()
    return any(str(row["name"]) == "owner_email" for row in rows)


def _migrate_owner_email_column(conn: sqlite3.Connection) -> None:
    if _frozen_evaluations_has_owner_email(conn):
        return
    conn.execute("ALTER TABLE frozen_evaluations ADD COLUMN owner_email TEXT")
    conn.commit()


def _migrate_snapshot_reviews_fk(conn: sqlite3.Connection) -> None:
    """Recreate snapshot_reviews with FK to frozen_evaluations; drop orphan review rows."""
    if _snapshot_reviews_has_fk(conn):
        return
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='snapshot_reviews'"
    ).fetchone()
    if not exists:
        return
    conn.execute(
        """
        CREATE TABLE snapshot_reviews__fk_migrated (
            id TEXT PRIMARY KEY NOT NULL,
            snapshot_id TEXT NOT NULL UNIQUE
                REFERENCES frozen_evaluations(id) ON DELETE CASCADE,
            review_status TEXT NOT NULL,
            outcome_notes TEXT,
            reviewed_at_utc TEXT NOT NULL,
            review_horizon_ref TEXT,
            paper_tag TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO snapshot_reviews__fk_migrated
        (id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
         review_horizon_ref, paper_tag)
        SELECT sr.id, sr.snapshot_id, sr.review_status, sr.outcome_notes,
               sr.reviewed_at_utc, sr.review_horizon_ref, sr.paper_tag
        FROM snapshot_reviews sr
        INNER JOIN frozen_evaluations fe ON fe.id = sr.snapshot_id
        """
    )
    conn.execute("DROP TABLE snapshot_reviews")
    conn.execute("ALTER TABLE snapshot_reviews__fk_migrated RENAME TO snapshot_reviews")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_snapshot_reviews_status ON snapshot_reviews(review_status)"
    )
    conn.commit()


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS frozen_evaluations (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            expiry TEXT NOT NULL,
            summary_line TEXT NOT NULL,
            record_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_frozen_eval_created ON frozen_evaluations(created_at DESC)"
    )
    reviews_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='snapshot_reviews'"
    ).fetchone()
    if not reviews_exists:
        conn.execute(
            """
            CREATE TABLE snapshot_reviews (
                id TEXT PRIMARY KEY NOT NULL,
                snapshot_id TEXT NOT NULL UNIQUE
                    REFERENCES frozen_evaluations(id) ON DELETE CASCADE,
                review_status TEXT NOT NULL,
                outcome_notes TEXT,
                reviewed_at_utc TEXT NOT NULL,
                review_horizon_ref TEXT,
                paper_tag TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_snapshot_reviews_status ON snapshot_reviews(review_status)"
        )
    else:
        try:
            conn.execute("ALTER TABLE snapshot_reviews ADD COLUMN paper_tag TEXT")
        except sqlite3.OperationalError:
            pass
        _migrate_snapshot_reviews_fk(conn)
    _migrate_owner_email_column(conn)
    conn.commit()


PENDING_SORT_NEWEST = "newest"
PENDING_SORT_EXPIRY = "expiry"
PENDING_SORT_HORIZON = "horizon"
PENDING_SORT_OPTIONS: tuple[str, ...] = (
    PENDING_SORT_NEWEST,
    PENDING_SORT_EXPIRY,
    PENDING_SORT_HORIZON,
)


def review_horizon_ref_from_frozen(record: dict[str, Any]) -> str:
    """Stable digest line from frozen verification (for review audit trail)."""
    vs = record.get("verification") if isinstance(record.get("verification"), dict) else {}
    inner = vs.get("verification_summary") if isinstance(vs.get("verification_summary"), dict) else {}
    parts = [
        str(record.get("expiry") or "").strip(),
        str(inner.get("as_of_utc") or "").strip(),
        str(inner.get("disagreement_category_id") or "").strip(),
    ]
    return " · ".join(p for p in parts if p)


def upsert_review(
    conn: sqlite3.Connection,
    *,
    snapshot_id: str,
    review_status: str,
    outcome_notes: str | None,
    review_horizon_ref: str | None = None,
    paper_tag: str | None = None,
) -> None:
    init_schema(conn)
    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"invalid review_status {review_status!r}; expected one of {REVIEW_STATUSES}")
    sid = str(snapshot_id)
    notes = (outcome_notes or "").strip() or None
    href = (review_horizon_ref or "").strip() or None
    tag = (paper_tag or "").strip() or None
    if tag and len(tag) > 120:
        tag = tag[:120]
    now = _utc_iso()
    row = conn.execute("SELECT id FROM snapshot_reviews WHERE snapshot_id = ?", (sid,)).fetchone()
    if row:
        conn.execute(
            """
            UPDATE snapshot_reviews
            SET review_status = ?, outcome_notes = ?, reviewed_at_utc = ?,
                review_horizon_ref = ?, paper_tag = ?
            WHERE snapshot_id = ?
            """,
            (review_status, notes, now, href, tag, sid),
        )
    else:
        conn.execute(
            """
            INSERT INTO snapshot_reviews
            (id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
             review_horizon_ref, paper_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), sid, review_status, notes, now, href, tag),
        )
    conn.commit()


def get_review_for_snapshot(conn: sqlite3.Connection, snapshot_id: str) -> dict[str, Any] | None:
    init_schema(conn)
    cur = conn.execute(
        """
        SELECT id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
               review_horizon_ref, paper_tag
        FROM snapshot_reviews WHERE snapshot_id = ?
        """,
        (str(snapshot_id),),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def _pending_order_clause(sort: str) -> str:
    s = (sort or PENDING_SORT_NEWEST).strip().lower()
    if s == PENDING_SORT_EXPIRY:
        return "fe.expiry ASC, fe.created_at DESC"
    if s == PENDING_SORT_HORIZON:
        return "COALESCE(sr.review_horizon_ref, fe.expiry) ASC, fe.created_at DESC"
    return "fe.created_at DESC"


def list_snapshots_pending_review(
    conn: sqlite3.Connection,
    *,
    limit: int = 20,
    expiry: str | None = None,
    sort: str = PENDING_SORT_NEWEST,
) -> list[dict[str, Any]]:
    """Frozen rows with no review row or review_status = pending."""
    init_schema(conn)
    exp = (expiry or "").strip() or None
    where = "sr.snapshot_id IS NULL OR sr.review_status = 'pending'"
    params: list[Any] = []
    if exp:
        where = f"({where}) AND fe.expiry = ?"
        params.append(exp)
    order = _pending_order_clause(sort)
    cur = conn.execute(
        f"""
        SELECT fe.id, fe.created_at, fe.expiry, fe.summary_line,
               sr.review_horizon_ref
        FROM frozen_evaluations fe
        LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
        WHERE {where}
        ORDER BY {order}
        LIMIT ?
        """,
        (*params, int(limit)),
    )
    return [dict(r) for r in cur.fetchall()]


def list_distinct_frozen_expiries(conn: sqlite3.Connection, *, limit: int = 200) -> list[str]:
    """Distinct expiry labels from frozen_evaluations (for filter dropdowns)."""
    init_schema(conn)
    cur = conn.execute(
        """
        SELECT DISTINCT expiry FROM frozen_evaluations
        WHERE TRIM(expiry) != ''
        ORDER BY expiry ASC
        LIMIT ?
        """,
        (int(limit),),
    )
    return [str(r[0]) for r in cur.fetchall()]


def list_completed_review_snapshots(
    conn: sqlite3.Connection,
    *,
    limit: int = 500,
    review_statuses: list[str] | None = None,
    expiry: str | None = None,
    reviewed_after_utc: str | None = None,
    reviewed_before_utc: str | None = None,
) -> list[dict[str, Any]]:
    """Frozen rows joined to reviews with status other than `pending` (Phase 6 rollup input)."""
    init_schema(conn)
    statuses = (
        [str(s) for s in (review_statuses or []) if str(s).strip()]
        if review_statuses is not None
        else None
    )
    exp = (expiry or "").strip() or None
    after = (reviewed_after_utc or "").strip() or None
    before = (reviewed_before_utc or "").strip() or None
    where_parts = ["sr.review_status != 'pending'"]
    params: list[Any] = []
    if statuses is not None:
        where_parts.append("sr.review_status IN (" + ",".join(["?"] * len(statuses)) + ")")
        params.extend(statuses)
    if exp:
        where_parts.append("fe.expiry = ?")
        params.append(exp)
    if after:
        where_parts.append("sr.reviewed_at_utc >= ?")
        params.append(after)
    if before:
        where_parts.append("sr.reviewed_at_utc <= ?")
        params.append(before)
    where = " AND ".join(where_parts)
    cur = conn.execute(
        f"""
        SELECT fe.id AS snapshot_id, fe.created_at, fe.expiry, fe.summary_line, fe.record_json,
               sr.id AS review_row_id, sr.review_status, sr.outcome_notes,
               sr.reviewed_at_utc, sr.review_horizon_ref, sr.paper_tag
        FROM frozen_evaluations fe
        INNER JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
        WHERE {where}
        ORDER BY sr.reviewed_at_utc DESC
        LIMIT ?
        """,
        (*params, int(limit)),
    )
    out: list[dict[str, Any]] = []
    for row in cur.fetchall():
        r = dict(row)
        rec_json = r.pop("record_json")
        out.append(
            {
                "snapshot_id": r["snapshot_id"],
                "created_at": r.get("created_at"),
                "expiry": r.get("expiry"),
                "summary_line": r.get("summary_line"),
                "record": json.loads(rec_json),
                "review": {
                    "id": r["review_row_id"],
                    "review_status": r["review_status"],
                    "outcome_notes": r["outcome_notes"],
                    "reviewed_at_utc": r["reviewed_at_utc"],
                    "review_horizon_ref": r["review_horizon_ref"],
                    "paper_tag": r.get("paper_tag"),
                },
            }
        )
    return out


def insert_record(conn: sqlite3.Connection, record: dict[str, Any]) -> str:
    init_schema(conn)
    rid = str(record["snapshot_id"])
    created = str(record["created_at_utc"])
    exp = str(record.get("expiry") or "")
    summary = summary_line_for_record(record)
    owner_email = normalize_owner_email(record.get("owner_email") if isinstance(record.get("owner_email"), str) else None)
    conn.execute(
        """
        INSERT INTO frozen_evaluations
        (id, created_at, expiry, summary_line, record_json, owner_email)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            rid,
            created,
            exp,
            summary,
            json.dumps(record, separators=(",", ":"), ensure_ascii=False),
            owner_email,
        ),
    )
    conn.commit()
    return rid


def list_recent(
    conn: sqlite3.Connection,
    *,
    limit: int = 50,
    owner_email: str | None = None,
) -> list[dict[str, Any]]:
    init_schema(conn)
    norm_owner = normalize_owner_email(owner_email) if owner_email is not None else None
    if norm_owner:
        cur = conn.execute(
            """
            SELECT id, created_at, expiry, summary_line, owner_email
            FROM frozen_evaluations
            WHERE owner_email = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (norm_owner, int(limit)),
        )
    else:
        cur = conn.execute(
            """
            SELECT id, created_at, expiry, summary_line, owner_email
            FROM frozen_evaluations
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (int(limit),),
        )
    return [dict(row) for row in cur.fetchall()]


def get_by_id(conn: sqlite3.Connection, snapshot_id: str) -> dict[str, Any] | None:
    init_schema(conn)
    cur = conn.execute(
        "SELECT record_json FROM frozen_evaluations WHERE id = ?",
        (str(snapshot_id),),
    )
    row = cur.fetchone()
    if not row:
        return None
    return json.loads(row["record_json"])


def open_store(path: Path | None = None) -> sqlite3.Connection:
    p = path or default_db_path()
    c = _connect(p)
    init_schema(c)
    return c
