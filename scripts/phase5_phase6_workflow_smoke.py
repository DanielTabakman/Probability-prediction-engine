"""
Non-UI workflow smoke for Phase 4–6:

- Freeze (insert frozen record)
- Review (upsert review status)
- Pending list drops the reviewed snapshot when non-pending
- Class rollup counts the reviewed snapshot

This is not a replacement for Streamlit manual checks; it is a fast regression guard
that exercises the same SQLite paths as the UI.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    insert_record,
    list_completed_review_snapshots,
    list_snapshots_pending_review,
    open_store,
    upsert_review,
)
from src.viz.reviewed_class_summary import build_class_summary


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "ppe_smoke.sqlite3"
        conn = open_store(db_path)
        try:
            v = {
                "verification_summary": {
                    "as_of_utc": "2026-05-05T00:00:00Z",
                    "disagreement_category_id": "width_vol",
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
                    },
                    "market_implied": {"breeden_litzenberger": "computed"},
                },
                "belief_disagreement": {"contract_schema_version": "bd-test-1"},
                "belief_vs_market_glance": {"shape_gap_strength": "Low"},
            }
            rec = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
            rid = insert_record(conn, rec)

            pending0 = list_snapshots_pending_review(conn, limit=50)
            assert any(r["id"] == rid for r in pending0), "expected snapshot to be pending before review"

            upsert_review(
                conn,
                snapshot_id=rid,
                review_status="supportive",
                outcome_notes="ok",
                review_horizon_ref="ref",
            )

            pending1 = list_snapshots_pending_review(conn, limit=50)
            assert not any(r["id"] == rid for r in pending1), "expected snapshot to be non-pending after review"

            completed = list_completed_review_snapshots(conn, limit=50)
            roll = build_class_summary(completed)
            assert int(roll.get("n_reviewed") or 0) == 1, "expected one reviewed snapshot in class rollup"
        finally:
            conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

