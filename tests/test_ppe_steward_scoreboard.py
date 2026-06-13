"""Tests for ppe_steward_scoreboard."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.ppe_steward_scoreboard import (
    build_next_actions,
    build_nudge_message,
    build_scoreboard,
    format_plan_walkthrough,
    format_scoreboard_text,
    parse_msos_p8_sessions,
    resolve_plan_phase,
    resolve_nudge_slot,
    sessions_this_week,
    MsosP8Session,
)


class TestPpeStewardScoreboard(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "MSOS_P8_VALIDATION_REPORT_V1.md").write_text(
            "**Status:** **DRAFT**\n",
            encoding="utf-8",
        )
        (sop / "COMMERCIAL_OPS_COMPLETION.md").write_text(
            "| VPS repo-root `.env` | **steward follow-up** |\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_reality_checks(self, body: str) -> None:
        path = self.repo / "docs" / "SOP" / "VALIDATION_REALITY_CHECKS.md"
        path.write_text(body, encoding="utf-8")

    def test_parse_msos_p8_sessions_skips_fill_rows(self) -> None:
        text = (
            "## MSOS P8 friends-first tester metrics\n\n"
            "| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | "
            "Return to monitor/history | Paid interest (steward call) | Notes |\n"
            "|------|----------------|------------------------|----------------------|"
            "---------------------------|------------------------------|-------|\n"
            "| _fill_ | friend | Y | Y | Y | N | pending |\n"
            "| 2026-06-10 | trader A | Y | Y | N | N | good session |\n"
        )
        sessions = parse_msos_p8_sessions(text)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].profile, "trader A")

    def test_build_scoreboard_counts_sessions(self) -> None:
        self._write_reality_checks(
            "## MSOS P8 friends-first tester metrics\n\n"
            "| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | "
            "Return to monitor/history | Paid interest (steward call) | Notes |\n"
            "|------|---|---|---|---|---|---|\n"
            "| 2026-06-10 | A | Y | Y | Y | N | x |\n"
            "| 2026-06-11 | B | Y | N | Y | N | y |\n"
        )
        sb = build_scoreboard(self.repo, ref=date(2026, 6, 11))
        self.assertEqual(sb["sessions_logged"], 2)
        self.assertEqual(sb["sessions_remaining"], 8)
        self.assertEqual(sb["sessions_this_week"], 2)
        self.assertEqual(sb["validation_report_status"], "DRAFT")

    def test_next_actions_when_no_sessions_this_week(self) -> None:
        actions = build_next_actions(
            logged=0,
            remaining=10,
            week_count=0,
            report_status="DRAFT",
            vps_pending=True,
            paid_yes=0,
        )
        self.assertTrue(any("Book 1 guided tester" in a for a in actions))

    def test_format_scoreboard_text(self) -> None:
        self._write_reality_checks(
            "## MSOS P8 friends-first tester metrics\n\n"
            "| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | "
            "Return to monitor/history | Paid interest (steward call) | Notes |\n"
            "|------|---|---|---|---|---|---|\n"
        )
        text = format_scoreboard_text(build_scoreboard(self.repo))
        self.assertIn("0/10", text)
        self.assertIn("Do next:", text)

    def test_resolve_nudge_slot_auto(self) -> None:
        self.assertEqual(resolve_nudge_slot("auto", ref=date(2026, 6, 8)), "monday")
        self.assertEqual(resolve_nudge_slot("auto", ref=date(2026, 6, 11)), "thursday")
        self.assertIsNone(resolve_nudge_slot("auto", ref=date(2026, 6, 9)))

    def test_sessions_this_week_monday_boundary(self) -> None:
        sessions = [
            MsosP8Session("2026-06-09", "x", "Y", "Y", "Y", "N", ""),
            MsosP8Session("2026-06-15", "y", "Y", "Y", "Y", "N", ""),
        ]
        self.assertEqual(sessions_this_week(sessions, ref=date(2026, 6, 11)), 1)

    def test_nudge_includes_why_and_moves(self) -> None:
        self._write_reality_checks(
            "## MSOS P8 friends-first tester metrics\n\n"
            "| Date | Tester profile | Comprehension (~5 min) | Thesis confirm honest | "
            "Return to monitor/history | Paid interest (steward call) | Notes |\n"
            "|------|---|---|---|---|---|---|\n"
        )
        sb = build_scoreboard(self.repo)
        title, body = build_nudge_message(sb, "monday")
        self.assertIn("outreach", title.lower())
        self.assertIn("Why this ping", body)
        self.assertIn("What you get out of it", body)
        self.assertIn("Your moves now", body)

    def test_walkthrough_covers_both_days(self) -> None:
        text = format_plan_walkthrough(build_scoreboard(self.repo))
        self.assertIn("Monday 13:00", text)
        self.assertIn("Thursday 20:00", text)
        self.assertIn("Why this plan exists", text)

    def test_plan_phase_start_at_zero(self) -> None:
        sb = build_scoreboard(self.repo)
        self.assertEqual(resolve_plan_phase(sb), "start")


if __name__ == "__main__":
    unittest.main()
