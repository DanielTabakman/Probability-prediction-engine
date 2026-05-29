"""Phase 5 snapshot review persistence (SQLite alongside frozen_evaluations)."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    PENDING_SORT_EXPIRY,
    PENDING_SORT_NEWEST,
    get_review_for_snapshot,
    insert_record,
    list_distinct_frozen_expiries,
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

    def test_paper_tag_and_pending_sort(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "paper.sqlite"
            conn = open_store(p)
            try:
                v = {
                    "verification_summary": {
                        "as_of_utc": "2026-05-04T12:00:00Z",
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
                        }
                    },
                    "belief_disagreement": {},
                }
                rec_a = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
                rec_b = build_frozen_evaluation_record(verification=v, expiry_str="6MAY26")
                rid_a = insert_record(conn, rec_a)
                insert_record(conn, rec_b)

                upsert_review(
                    conn,
                    snapshot_id=rid_a,
                    review_status="pending",
                    outcome_notes="n",
                    paper_tag="  thesis-A  ",
                )
                got = get_review_for_snapshot(conn, rid_a)
                assert got is not None
                self.assertEqual(got["paper_tag"], "thesis-A")

                exps = list_distinct_frozen_expiries(conn)
                self.assertEqual(exps, ["5MAY26", "6MAY26"])

                pending = list_snapshots_pending_review(
                    conn, limit=10, expiry="6MAY26", sort=PENDING_SORT_NEWEST
                )
                self.assertEqual(len(pending), 1)
                self.assertEqual(pending[0]["expiry"], "6MAY26")

                by_exp = list_snapshots_pending_review(
                    conn, limit=10, sort=PENDING_SORT_EXPIRY
                )
                self.assertEqual(len(by_exp), 2)
                self.assertEqual([r["expiry"] for r in by_exp], ["5MAY26", "6MAY26"])
            finally:
                conn.close()

    def test_foreign_keys_enabled_and_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "fk.sqlite"
            conn = open_store(p)
            try:
                fk_on = conn.execute("PRAGMA foreign_keys").fetchone()
                self.assertIsNotNone(fk_on)
                self.assertEqual(int(fk_on[0]), 1)

                fk_list = conn.execute("PRAGMA foreign_key_list(snapshot_reviews)").fetchall()
                self.assertGreaterEqual(len(fk_list), 1)
                self.assertEqual(fk_list[0]["table"], "frozen_evaluations")

                with self.assertRaises(sqlite3.IntegrityError):
                    upsert_review(
                        conn,
                        snapshot_id="00000000-0000-0000-0000-000000000000",
                        review_status="pending",
                        outcome_notes=None,
                    )
            finally:
                conn.close()

    def test_delete_snapshot_cascades_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "cascade.sqlite"
            conn = open_store(p)
            try:
                v = {
                    "verification_summary": {
                        "as_of_utc": "2026-05-04T12:00:00Z",
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
                        }
                    },
                    "belief_disagreement": {},
                }
                rec = build_frozen_evaluation_record(verification=v, expiry_str="5MAY26")
                rid = insert_record(conn, rec)
                upsert_review(conn, snapshot_id=rid, review_status="supportive", outcome_notes="x")
                self.assertIsNotNone(get_review_for_snapshot(conn, rid))

                conn.execute("DELETE FROM frozen_evaluations WHERE id = ?", (rid,))
                conn.commit()
                self.assertIsNone(get_review_for_snapshot(conn, rid))
            finally:
                conn.close()

    def test_legacy_migration_drops_orphan_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "legacy.sqlite"
            raw = sqlite3.connect(str(p))
            try:
                raw.execute("PRAGMA foreign_keys=ON")
                raw.execute(
                    """
                    CREATE TABLE frozen_evaluations (
                        id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        expiry TEXT NOT NULL,
                        summary_line TEXT NOT NULL,
                        record_json TEXT NOT NULL
                    )
                    """
                )
                raw.execute(
                    """
                    CREATE TABLE snapshot_reviews (
                        id TEXT PRIMARY KEY NOT NULL,
                        snapshot_id TEXT NOT NULL UNIQUE,
                        review_status TEXT NOT NULL,
                        outcome_notes TEXT,
                        reviewed_at_utc TEXT NOT NULL,
                        review_horizon_ref TEXT,
                        paper_tag TEXT
                    )
                    """
                )
                raw.execute(
                    """
                    INSERT INTO snapshot_reviews
                    (id, snapshot_id, review_status, outcome_notes, reviewed_at_utc,
                     review_horizon_ref, paper_tag)
                    VALUES ('orphan-review', 'missing-snapshot', 'pending', NULL,
                            '2026-05-01T00:00:00Z', NULL, NULL)
                    """
                )
                raw.commit()
            finally:
                raw.close()

            conn = open_store(p)
            try:
                rows = conn.execute("SELECT snapshot_id FROM snapshot_reviews").fetchall()
                self.assertEqual(len(rows), 0)
                fk_list = conn.execute("PRAGMA foreign_key_list(snapshot_reviews)").fetchall()
                self.assertGreaterEqual(len(fk_list), 1)
            finally:
                conn.close()
