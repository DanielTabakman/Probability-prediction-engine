"""MVP1 feedback store and §15F category validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.viz.mvp1_feedback_store import (
    CONFUSION_CATEGORIES,
    insert_feedback,
    list_recent,
    open_store,
)


class TestMvp1FeedbackStore(unittest.TestCase):
    def test_insert_and_list_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "feedback.sqlite3"
            conn = open_store(p)
            try:
                rid = insert_feedback(
                    conn,
                    confusion_category=CONFUSION_CATEGORIES[0],
                    usefulness=4,
                    repeat_use_intent=3,
                    objections_text="Hard to tell trust status at a glance.",
                    session_note="first pass",
                    context={"primary_output_state": "watch_only"},
                )
                rows = list_recent(conn, limit=10)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["id"], rid)
                self.assertEqual(rows[0]["confusion_category"], CONFUSION_CATEGORIES[0])
                self.assertEqual(rows[0]["usefulness"], 4)
                self.assertEqual(rows[0]["repeat_use_intent"], 3)
                self.assertIn("trust status", rows[0]["objections_text"] or "")
            finally:
                conn.close()

    def test_rejects_invalid_category(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            conn = open_store(Path(td) / "t.sqlite3")
            try:
                with self.assertRaises(ValueError):
                    insert_feedback(
                        conn,
                        confusion_category="not-a-category",
                        usefulness=3,
                        repeat_use_intent=3,
                    )
            finally:
                conn.close()

    def test_rejects_invalid_likert(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            conn = open_store(Path(td) / "t.sqlite3")
            try:
                with self.assertRaises(ValueError):
                    insert_feedback(
                        conn,
                        confusion_category=CONFUSION_CATEGORIES[1],
                        usefulness=0,
                        repeat_use_intent=3,
                    )
            finally:
                conn.close()

    def test_confusion_categories_match_master_15f(self) -> None:
        expected = (
            "naming confusion",
            "market-read confusion",
            "trust/provenance confusion",
            "belief-control confusion",
            "candidate/recommendation confusion",
            "no-trade/watch-only confusion",
            "layout/visual hierarchy confusion",
            "value/desirability signal",
            "feature request / later-scope item",
        )
        self.assertEqual(CONFUSION_CATEGORIES, expected)
        json.dumps(list(CONFUSION_CATEGORIES))
