"""Phase 6 class summary rollups from completed reviews."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    list_completed_review_snapshots,
    open_store,
    upsert_review,
    insert_record,
)
from src.viz.reviewed_class_summary import (
    build_class_summary,
    extract_summary_dimensions,
    operator_guidance_line,
    serialize_rollup_csv,
)
from collections import Counter


class TestReviewedClassSummary(unittest.TestCase):
    def test_empty_rollup(self) -> None:
        s = build_class_summary([])
        self.assertEqual(s["n_reviewed"], 0)
        self.assertIn("No completed reviews", s["operator_summary_line"])

    def test_extract_dimensions(self) -> None:
        v = {
            "verification_summary": {"disagreement_category_id": "width_vol"},
            "belief_disagreement": {
                "classification_trace": {"shape_gap_strength": "Low", "category_id": "width_vol"},
            },
            "belief_vs_market_glance": {"shape_gap_strength": "Low"},
            "density": {"market_implied": {"breeden_litzenberger": "computed"}},
        }
        rec = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
        d = extract_summary_dimensions(rec)
        self.assertEqual(d["disagreement_category_id"], "width_vol")
        self.assertEqual(d["shape_gap_strength"], "Low")
        self.assertEqual(d["trust_breeden"], "computed")

    def test_guidance_mixed(self) -> None:
        c = Counter({"supportive": 2, "contradictory": 2})
        g = operator_guidance_line(c)
        self.assertTrue(g)

    def test_serialize_rollup_csv(self) -> None:
        rollup = build_class_summary([])
        rollup["n_reviewed"] = 1
        rollup["by_review_status"] = {"supportive": 1}
        csv_text = serialize_rollup_csv(rollup)
        self.assertIn("metric,bucket,count", csv_text.splitlines()[0])
        self.assertIn("by_review_status,supportive,1", csv_text)
        self.assertIn("operator_summary_line", csv_text)

    def test_sqlite_list_completed_and_rollup(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "cls.sqlite"
            conn = open_store(p)
            try:
                v = {
                    "verification_summary": {
                        "as_of_utc": "2026-05-04T12:00:00Z",
                        "disagreement_category_id": "aligned",
                    },
                    "density": {
                        "reference_risk_neutral": {
                            "method": "Black–Scholes lognormal",
                            "forward_usd": 90_000.0,
                            "atm_iv_annual": 0.55,
                            "T_years": 0.25,
                            "grid_price_min_usd": 50_000.0,
                            "grid_price_max_usd": 150_000.0,
                            "grid_points": 100,
                        },
                        "market_implied": {"breeden_litzenberger": "computed"},
                    },
                    "belief_disagreement": {"contract_schema_version": "bd-x"},
                    "belief_vs_market_glance": {"shape_gap_strength": "Moderate"},
                }
                rec = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
                rid = insert_record(conn, rec)
                upsert_review(
                    conn,
                    snapshot_id=rid,
                    review_status="supportive",
                    outcome_notes="ok",
                    review_horizon_ref="ref",
                )
                rows = list_completed_review_snapshots(conn, limit=50)
                self.assertEqual(len(rows), 1)
                s = build_class_summary(rows)
                self.assertEqual(s["n_reviewed"], 1)
                self.assertEqual(s["by_review_status"].get("supportive"), 1)
                self.assertIn("aligned", s["by_disagreement_category"])

                rows2 = list_completed_review_snapshots(conn, limit=50, review_statuses=["supportive"])
                self.assertEqual(len(rows2), 1)
                rows3 = list_completed_review_snapshots(conn, limit=50, review_statuses=["contradictory"])
                self.assertEqual(len(rows3), 0)
                rows4 = list_completed_review_snapshots(conn, limit=50, expiry="5MAY26")
                self.assertEqual(len(rows4), 1)
                rows5 = list_completed_review_snapshots(conn, limit=50, expiry="6MAY26")
                self.assertEqual(len(rows5), 0)
                rows6 = list_completed_review_snapshots(
                    conn,
                    limit=50,
                    reviewed_after_utc="2020-01-01T00:00:00Z",
                    reviewed_before_utc="2099-12-31T23:59:59Z",
                )
                self.assertEqual(len(rows6), 1)
            finally:
                conn.close()
