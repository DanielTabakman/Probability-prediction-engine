"""Frozen evaluation SQLite store."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.frozen_evaluation_store import (
    get_snapshot_review_payload,
    get_by_id,
    insert_record,
    list_recent,
    normalize_owner_email,
    open_store,
)


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
                self.assertEqual(got["record_header"]["snapshot_id"], rid)
                self.assertEqual(got["record_header"]["payload_schema_version"], "ppe_frozen_eval_v1")
                self.assertEqual(got["classifier_version"], "bd-test-1")
                self.assertEqual(got["benchmark_witness"]["forward_usd"], 100_000.0)
                json.dumps(got)  # serializable

                raw = conn.execute(
                    "SELECT record_json FROM frozen_evaluations WHERE id = ?",
                    (rid,),
                ).fetchone()["record_json"]
                self.assertEqual(raw, json.dumps(got, separators=(",", ":"), sort_keys=True, ensure_ascii=False))

                review_payload = get_snapshot_review_payload(conn, rid)
                assert review_payload is not None
                self.assertEqual(review_payload["schema_version"], "snapshot_review_v1")
                self.assertEqual(review_payload["snapshot_id"], rid)
                self.assertEqual(review_payload["record_header"]["snapshot_id"], rid)
                self.assertNotIn("owner_email", review_payload)
                self.assertNotIn("owner_email", review_payload["record_header"])
            finally:
                conn.close()

    def test_current_version_record_without_header_is_read_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "legacy-current.sqlite"
            conn = open_store(p)
            try:
                rec = build_frozen_evaluation_record(verification={}, expiry_str="5MAY26")
                rec.pop("record_header")
                raw = json.dumps(rec, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
                conn.execute(
                    """
                    INSERT INTO frozen_evaluations
                    (id, created_at, expiry, summary_line, record_json, owner_email)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (rec["snapshot_id"], rec["created_at_utc"], rec["expiry"], "legacy-current", raw, None),
                )
                conn.commit()

                got = get_by_id(conn, rec["snapshot_id"])
                assert got is not None
                self.assertEqual(got["payload_schema_version"], "ppe_frozen_eval_v1")
                self.assertEqual(got["record_header"]["snapshot_id"], rec["snapshot_id"])
            finally:
                conn.close()

    def test_unsupported_frozen_record_versions_fail_at_store_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "unsupported.sqlite"
            conn = open_store(p)
            try:
                rec = build_frozen_evaluation_record(verification={}, expiry_str="5MAY26")
                rec["payload_schema_version"] = "frozen_evaluation_v1"
                rec["record_header"]["payload_schema_version"] = "frozen_evaluation_v1"
                with self.assertRaisesRegex(ValueError, "unsupported frozen evaluation payload_schema_version"):
                    insert_record(conn, rec)

                valid = build_frozen_evaluation_record(verification={}, expiry_str="5MAY26")
                bad = dict(valid)
                bad["payload_schema_version"] = "frozen_evaluation_v1"
                bad["record_header"] = dict(valid["record_header"])
                bad["record_header"]["payload_schema_version"] = "frozen_evaluation_v1"
                conn.execute(
                    """
                    INSERT INTO frozen_evaluations
                    (id, created_at, expiry, summary_line, record_json, owner_email)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bad["snapshot_id"],
                        bad["created_at_utc"],
                        bad["expiry"],
                        "bad-version",
                        json.dumps(bad, separators=(",", ":"), sort_keys=True, ensure_ascii=False),
                        None,
                    ),
                )
                conn.commit()

                with self.assertRaisesRegex(ValueError, "unsupported frozen evaluation payload_schema_version"):
                    get_by_id(conn, bad["snapshot_id"])
            finally:
                conn.close()

    def test_owner_email_migration_and_filter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "legacy.sqlite"

            conn = sqlite3.connect(str(p))
            try:
                conn.execute(
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
                conn.execute(
                    "INSERT INTO frozen_evaluations (id, created_at, expiry, summary_line, record_json) "
                    "VALUES (?, ?, ?, ?, ?)",
                    ("legacy-1", "2026-05-04T12:00:00Z", "5MAY26", "legacy", "{}"),
                )
                conn.commit()
            finally:
                conn.close()

            conn2 = open_store(p)
            try:
                v = {
                    "verification_summary": {"as_of_utc": "2026-05-04T12:00:00Z"},
                    "density": {"reference_risk_neutral": {"method": "test"}},
                    "belief_disagreement": {"contract_schema_version": "bd-test-1"},
                }
                rec_a = build_frozen_evaluation_record(
                    verification=v,
                    expiry_str="5MAY26",
                    owner_email="Alice@Example.COM",
                )
                rec_b = build_frozen_evaluation_record(
                    verification=v,
                    expiry_str="5MAY26",
                    owner_email="bob@example.com",
                )
                insert_record(conn2, rec_a)
                insert_record(conn2, rec_b)

                alice_rows = list_recent(conn2, owner_email="alice@example.com")
                self.assertEqual(len(alice_rows), 1)
                self.assertEqual(alice_rows[0]["owner_email"], "alice@example.com")

                all_rows = list_recent(conn2, limit=10)
                self.assertEqual(len(all_rows), 3)
                self.assertEqual(normalize_owner_email(" Alice@Example.COM "), "alice@example.com")
                got = get_by_id(conn2, rec_a["snapshot_id"])
                assert got is not None
                self.assertEqual(got["owner_email"], "alice@example.com")
            finally:
                conn2.close()
