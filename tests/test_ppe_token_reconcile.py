"""Tests for ppe_token_reconcile."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_token_reconcile import (
    billing_recommendation,
    digest_reconcile_line,
    record_manual_month,
    reconcile,
)


class TestPpeTokenReconcile(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_record_and_reconcile(self) -> None:
        record_manual_month(self.repo, month="2026-06", cursor_usd=120.0)
        data = reconcile(self.repo, days=30)
        self.assertEqual(data["cursor_usd"], 120.0)
        self.assertEqual(data["manual_month"], "2026-06")

    def test_billing_recommendation_without_manual(self) -> None:
        rec = billing_recommendation(self.repo)
        self.assertIsNotNone(rec)
        self.assertIn("BILLING", rec or "")

    def test_digest_line_none_without_manual(self) -> None:
        self.assertIsNone(digest_reconcile_line(self.repo))


if __name__ == "__main__":
    unittest.main()
