"""Tests for ppe_steward_nudge."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_steward_nudge import (
    already_sent_this_week,
    load_state,
    mark_sent,
    run_nudge,
    week_key,
)


class TestPpeStewardNudge(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "MSOS_P8_VALIDATION_REPORT_V1.md").write_text(
            "**Status:** **DRAFT**\n",
            encoding="utf-8",
        )
        (sop / "VALIDATION_REALITY_CHECKS.md").write_text(
            "## MSOS P8 friends-first tester metrics\n\n"
            "| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | "
            "Return to monitor/history | Paid interest (steward call) | Notes |\n"
            "|------|---|---|---|---|---|---|\n"
            "| _fill_ | x | Y | Y | Y | N | |\n",
            encoding="utf-8",
        )
        (sop / "COMMERCIAL_OPS_COMPLETION.md").write_text("steward follow-up\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_week_dedup(self) -> None:
        mark_sent(self.repo, {}, "wednesday", ref=date(2026, 6, 10))
        state = load_state(self.repo)
        self.assertTrue(already_sent_this_week(state, "wednesday", ref=date(2026, 6, 11)))
        self.assertFalse(already_sent_this_week(state, "wednesday", ref=date(2026, 6, 17)))

    def test_dry_run_wednesday(self) -> None:
        result = run_nudge(self.repo, slot="wednesday", dry_run=True, ref=date(2026, 6, 10))
        self.assertTrue(result.get("dry_run"))
        self.assertIn("plan outreach", result.get("title", "").lower())
        self.assertIn("Do next:", result.get("body", ""))

    def test_not_wed_or_sun_auto(self) -> None:
        result = run_nudge(self.repo, slot="auto", dry_run=True, ref=date(2026, 6, 9))
        self.assertEqual(result.get("reason"), "not_wed_or_sun")

    @patch.dict(os.environ, {"PPE_NTFY_STEWARD_TOPIC": "test-steward-topic"})
    @patch("scripts.ppe_steward_nudge.send_steward_ntfy", return_value=True)
    def test_send_when_configured(self, send_mock) -> None:
        result = run_nudge(
            self.repo,
            slot="wednesday",
            force=True,
            ref=date(2026, 6, 10),
        )
        self.assertTrue(result.get("sent"))
        send_mock.assert_called_once()
        state = load_state(self.repo)
        self.assertEqual(state.get("last_wednesday_week"), week_key(date(2026, 6, 10)))

    def test_steward_topic_unset(self) -> None:
        with patch("scripts.ppe_steward_nudge.steward_ntfy_configured", return_value=False):
            result = run_nudge(self.repo, slot="wednesday", force=True, ref=date(2026, 6, 10))
        self.assertEqual(result.get("reason"), "steward_topic_unset")


if __name__ == "__main__":
    unittest.main()
