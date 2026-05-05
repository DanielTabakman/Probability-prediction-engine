"""Phase 5 snapshot review persistence (SQLite alongside frozen_evaluations)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    get_review_for_snapshot,
    insert_record,
    list_snapshots_pending_review,
    open_store,
    upsert_review,
)


class TestFrozenReviewStore(unittest.TestCase):
    def test_upsert_get_list_pending(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "r.sqlite"
            conn = open_store(p)
            try:
                v = {
                    "verification_summary": {
                        "as_of_utc": "2026-05-04T12:00:00Z",
                        "disagreement_category_id": "width_vol",
                        "contract_schema_version": "bd-test-1",
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
                    "belief_disagreement": {"contract_schema_version": "bd-test-1"},
                }
                rec = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
                rid = insert_record(conn, rec)

                pending0 = list_snapshots_pending_review(conn, limit=10)
                self.assertEqual(len(pending0), 1)
                self.assertEqual(pending0[0]["id"], rid)

                self.assertIsNone(get_review_for_snapshot(conn, rid))

                upsert_review(
                    conn,
                    snapshot_id=rid,
                    review_status="supportive",
                    outcome_notes="ok",
                    review_horizon_ref="5MAY26 · 2026-05-04T12:00:00Z · width_vol",
                )
                got = get_review_for_snapshot(conn, rid)
                assert got is not None
                self.assertEqual(got["snapshot_id"], rid)
                self.assertEqual(got["review_status"], "supportive")
                self.assertEqual(got["outcome_notes"], "ok")
                self.assertTrue(got["reviewed_at_utc"])

                pending1 = list_snapshots_pending_review(conn, limit=10)
                self.assertEqual(len(pending1), 0)

                upsert_review(conn, snapshot_id=rid, review_status="pending", outcome_notes=None)
                pending2 = list_snapshots_pending_review(conn, limit=10)
                self.assertEqual(len(pending2), 1)
                self.assertEqual(pending2[0]["id"], rid)
            finally:
                conn.close()
