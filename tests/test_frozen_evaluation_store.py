"""Frozen evaluation SQLite store."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import get_by_id, insert_record, list_recent, open_store


class TestFrozenEvaluationStore(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.sqlite"
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
                rows = list_recent(conn, limit=10)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["id"], rid)
                got = get_by_id(conn, rid)
                assert got is not None
                self.assertEqual(got["snapshot_id"], rid)
                self.assertEqual(got["payload_schema_version"], rec["payload_schema_version"])
                self.assertEqual(got["classifier_version"], "bd-test-1")
                self.assertEqual(got["benchmark_witness"]["forward_usd"], 100_000.0)
                json.dumps(got)  # serializable
            finally:
                conn.close()
