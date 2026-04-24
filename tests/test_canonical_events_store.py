from __future__ import annotations

import sqlite3
import tempfile
import unittest

from src.probability_engine.contracts.canonical_events import (
    CanonicalEvent,
    ProbabilityObservation,
)
from src.probability_engine.infra.store import SQLiteStore


class TestCanonicalEventsStore(unittest.TestCase):
    def test_schema_and_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = f"{td}/test.sqlite"
            store = SQLiteStore(path=db_path)

            # Schema: new tables exist (additive).
            conn = sqlite3.connect(db_path)
            try:
                tables = {
                    r[0]
                    for r in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
            finally:
                conn.close()

            self.assertIn("canonical_events", tables)
            self.assertIn("probability_observations", tables)

            # Upsert canonical event.
            e1 = CanonicalEvent(
                id="evt_1",
                type="threshold_crossing",
                asset="BTC",
                threshold=100000.0,
                resolution_date="2026-12-31T00:00:00Z",
                description="BTC >= 100k by year end",
            )
            store.upsert_canonical_events([e1])

            # Write + read observations.
            obs = [
                ProbabilityObservation(
                    canonical_event_id="evt_1",
                    probability=0.12,
                    source="unit_test",
                    as_of_utc="2026-01-01T00:00:00Z",
                    raw_ref="ref_a",
                ),
                ProbabilityObservation(
                    canonical_event_id="evt_1",
                    probability=0.34,
                    source="unit_test",
                    as_of_utc="2026-01-02T00:00:00Z",
                    raw_ref=None,
                ),
            ]
            store.write_probability_observations(obs)
            got = store.read_probability_observations("evt_1")

            self.assertEqual(got, obs)


if __name__ == "__main__":
    unittest.main()

