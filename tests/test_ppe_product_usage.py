"""Tests for ppe_product_usage."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_product_usage import read_usage_events, summarize_usage


class TestPpeProductUsage(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_summarize_empty(self) -> None:
        summary = summarize_usage(self.repo, days=7)
        self.assertEqual(summary["total_events"], 0)
        self.assertFalse(summary["exists"])

    def test_read_jsonl_rows(self) -> None:
        path = self.repo / "data" / "ppe_product_usage.jsonl"
        path.parent.mkdir(parents=True)
        row = {"event_name": "page_view", "created_at_utc": "2026-06-30T12:00:00Z"}
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")
        rows = read_usage_events(path)
        self.assertEqual(len(rows), 1)
        summary = summarize_usage(self.repo, days=7)
        self.assertEqual(summary["total_events"], 1)
        self.assertEqual(summary["top_event"], "page_view")


if __name__ == "__main__":
    unittest.main()
