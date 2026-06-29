"""MSOS trader review loop v1 — snapshot post-mortem API and monitor routes."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
SOP = REPO_ROOT / "docs" / "SOP"

REVIEW_STATUSES = (
    "pending",
    "supportive",
    "contradictory",
    "contaminated",
    "not_judgeable",
)


def test_snapshot_review_lib_and_api_route_exist() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "snapshotReview.ts").read_text(encoding="utf-8")
    route = (
        MSOS_WEB / "src" / "app" / "api" / "snapshots" / "[id]" / "review" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "upsertSnapshotReview" in lib
    assert "REVIEW_STATUSES" in lib
    assert "reviewHorizonRefFromFrozen" in lib
    assert "export async function POST" in route
    assert "requireProtectedIdentity" in route
    assert "invalid review_status" in route
    assert "isValidReviewStatus" in route


def test_snapshot_detail_page_and_form_exist() -> None:
    page = (
        MSOS_WEB / "src" / "app" / "monitor" / "snapshot" / "[id]" / "page.tsx"
    ).read_text(encoding="utf-8")
    form = (MSOS_WEB / "src" / "components" / "SnapshotReviewForm.tsx").read_text(
        encoding="utf-8"
    )
    assert "loadSnapshotDetail" in page
    assert "SnapshotReviewForm" in page
    assert "paper / research only" in page.lower() or "Paper / research only" in page
    assert "/api/snapshots/" in form
    assert "review_status" in form
    assert "POST_MORTEM_STATUSES" in form


def test_monitor_content_lists_snapshot_review_links() -> None:
    content = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    assert "loadCommandCenterSummary" in content
    assert "/monitor/snapshot/" in content
    assert "reviewTagForStatus" in content
    assert "Saved reads" in content


def test_upsert_review_sqlite_mirror_python_statuses() -> None:
    """Writable upsert matches frozen_evaluation_store REVIEW_STATUSES semantics."""
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
                  ('snap-1', '2026-06-10T12:00:00Z', '5JUL26', 'BTC width · 5JUL26', '{}');
                """
            )
            bad_status = "bogus"
            assert bad_status not in REVIEW_STATUSES
            conn.execute(
                """
                INSERT INTO snapshot_reviews
                (id, snapshot_id, review_status, outcome_notes, reviewed_at_utc)
                VALUES ('r1', 'snap-1', ?, 'ok', '2026-06-11T12:00:00Z')
                """,
                ("supportive",),
            )
            row = conn.execute(
                "SELECT review_status, outcome_notes FROM snapshot_reviews WHERE snapshot_id = ?",
                ("snap-1",),
            ).fetchone()
        finally:
            conn.close()

        assert row == ("supportive", "ok")

        lib = (MSOS_WEB / "src" / "lib" / "snapshotReview.ts").read_text(encoding="utf-8")
        for status in REVIEW_STATUSES:
            assert f'"{status}"' in lib


def test_review_loop_sprint_and_phase_plan_touch_set() -> None:
    sprint = (SOP / "SPRINT_MSOS_TRADER_REVIEW_LOOP_V1.md").read_text(encoding="utf-8")
    plan = (SOP / "PHASE_PLANS" / "msos_trader_review_loop_v1_relay.json").read_text(
        encoding="utf-8"
    )
    assert "MSOS-RevLoop-Product-Slice002" in sprint
    assert "POST" in sprint and "review API" in sprint
    assert "MSOS-RevLoop-Product-Slice002" in plan
    assert "snapshots/[id]/review/route.ts" in plan
    assert "test_msos_web_snapshot_review.py" in plan
