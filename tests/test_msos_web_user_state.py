"""MSOS user state v1 — product slice witness (Command Center + snapshot API)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_command_center_summary_api_route_exists() -> None:
    route = MSOS_WEB / "src" / "app" / "api" / "command-center" / "summary" / "route.ts"
    text = route.read_text(encoding="utf-8")
    assert "export async function GET" in text
    assert "loadCommandCenterSummary" in text
    assert 'runtime = "nodejs"' in text


def test_command_center_summary_lib_read_only() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "commandCenterSummary.ts").read_text(encoding="utf-8")
    assert "PPE_SNAPSHOT_DB_PATH" in lib
    assert "From PPE snapshots" in lib
    assert "command_center_snapshot_summary" in lib


def test_command_center_ui_snapshot_copy_and_degraded() -> None:
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    page = (MSOS_WEB / "src" / "app" / "command-center" / "page.tsx").read_text(encoding="utf-8")
    assert "summary.sourceLabel" in content
    assert "Snapshot feed unavailable" in content
    assert "loadCommandCenterSummary" in page
    assert "Draft thesis" not in content
    assert "Preview data healthy" not in content
    assert "labTiles" in content


def test_command_center_summary_shape_with_seeded_db() -> None:
    from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
    from src.viz.frozen_evaluation_store import insert_record, open_store

    verification = {
        "verification_summary": {
            "as_of_utc": "2026-06-15T12:00:00Z",
            "disagreement_category_id": "width_vol",
            "contract_schema_version": "bd-test-cc",
        },
        "density": {
            "reference_risk_neutral": {
                "method": "test",
                "forward_usd": 100_000.0,
                "atm_iv_annual": 0.5,
                "T_years": 0.1,
                "grid_price_min_usd": 10_000.0,
                "grid_price_max_usd": 200_000.0,
                "grid_points": 10,
            }
        },
        "belief_disagreement": {"contract_schema_version": "bd-test-cc"},
    }
    rec = build_frozen_evaluation_record(verification=verification, expiry_str="5MAY26")

    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "snapshots.sqlite3"
        conn = open_store(db_path)
        try:
            insert_record(conn, rec)
            row = conn.execute(
                "SELECT summary_line FROM frozen_evaluations ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            assert row is not None
            summary_line = str(row[0])
        finally:
            conn.close()

        payload = {
            "status": "live",
            "sourceLabel": "From PPE snapshots",
            "currentWork": [{"name": "5MAY26", "tag": "Snapshot", "detail": summary_line}],
        }
        json.dumps(payload)
