"""MSOS user state v1 — Command Center snapshot bridge witness."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_command_center_summary_lib_and_api_exist() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "commandCenterSummary.ts").read_text(encoding="utf-8")
    route = (
        MSOS_WEB / "src" / "app" / "api" / "command-center" / "summary" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "loadCommandCenterSummary" in lib
    assert "PPE_SNAPSHOT_DB_PATH" in lib
    assert "From your saved views" in lib
    assert "degradedSummary" in lib
    assert "frozen_evaluations" in lib
    assert "snapshot_reviews" in lib
    assert "export async function GET" in route
    assert "requireProtectedIdentity" in route
    assert "loadCommandCenterSummary" in route


def test_command_center_page_uses_snapshot_summary() -> None:
    page = (MSOS_WEB / "src" / "app" / "command-center" / "page.tsx").read_text(encoding="utf-8")
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(
        encoding="utf-8"
    )
    assert "loadCommandCenterSummary" in page
    assert "summary={summary}" in page
    assert "friendlySnapshotFeedMessage" in content
    assert "summary.kpis" in content
    assert "summary.currentWork" in content


def test_seeded_snapshot_db_matches_summary_queries() -> None:
    """Mirror TS read queries against a fixture SQLite seeded like PPE frozen_evaluations."""
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "ppe_frozen_evaluations.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.executescript(
                """
                CREATE TABLE frozen_evaluations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    expiry TEXT NOT NULL,
                    summary_line TEXT NOT NULL,
                    record_json TEXT NOT NULL
                );
                CREATE TABLE snapshot_reviews (
                    id TEXT PRIMARY KEY NOT NULL,
                    snapshot_id TEXT NOT NULL UNIQUE,
                    review_status TEXT NOT NULL,
                    outcome_notes TEXT,
                    reviewed_at_utc TEXT NOT NULL,
                    review_horizon_ref TEXT,
                    paper_tag TEXT
                );
                INSERT INTO frozen_evaluations VALUES
                  ('snap-a', '2026-06-10T12:00:00Z', '5JUL26', 'BTC width · 5JUL26', '{}'),
                  ('snap-b', '2026-06-11T12:00:00Z', '12JUL26', 'BTC tail · 12JUL26', '{}');
                INSERT INTO snapshot_reviews VALUES
                  ('rev-1', 'snap-a', 'pending', NULL, '2026-06-12T12:00:00Z', NULL, NULL);
                """
            )
            total = conn.execute("SELECT COUNT(*) FROM frozen_evaluations").fetchone()[0]
            pending = conn.execute(
                """
                SELECT COUNT(*) FROM frozen_evaluations fe
                LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
                WHERE sr.snapshot_id IS NULL OR sr.review_status = 'pending'
                """
            ).fetchone()[0]
            rows = conn.execute(
                """
                SELECT fe.id, fe.summary_line, sr.review_status
                FROM frozen_evaluations fe
                LEFT JOIN snapshot_reviews sr ON sr.snapshot_id = fe.id
                ORDER BY fe.created_at DESC
                """
            ).fetchall()
        finally:
            conn.close()

        assert total == 2
        assert pending == 2
        assert rows[0][0] == "snap-b"
        assert rows[0][2] is None
        assert rows[1][0] == "snap-a"
        assert rows[1][2] == "pending"

        lib = (MSOS_WEB / "src" / "lib" / "commandCenterSummary.ts").read_text(encoding="utf-8")
        assert "ORDER BY fe.created_at DESC" in lib
        assert "status: \"live\"" in lib or "status: 'live'" in lib


def test_compose_msos_web_readonly_snapshot_mount() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "PPE_SNAPSHOT_DB_PATH=/ppe-snapshots/ppe_frozen_evaluations.sqlite3" in compose
    assert "ppe_snapshots:/ppe-snapshots:ro" in compose
    mount_doc = REPO_ROOT / "docs/DEPLOY/MSOS_USER_STATE_SNAPSHOT_MOUNT.md"
    assert mount_doc.is_file()
    assert "MSOS-UserStateV1-Platform-Slice003" in mount_doc.read_text(encoding="utf-8")
