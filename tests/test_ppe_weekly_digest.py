"""Tests for ppe_weekly_digest."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from scripts.ppe_dev_changelog import save_changelog, ParsedChangelog
from scripts.ppe_weekly_digest import (
    build_week_section,
    classify_bullet,
    cmd_backfill,
    cmd_generate,
    cmd_write_notify_payload,
    humanize_product_bullet,
    last_completed_week_monday,
    load_state,
    notify_payload_path,
    parse_latest_week_summary,
    week_dates,
)


class TestPpeWeeklyDigest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs" / "RELEASES").mkdir(parents=True)
        (self.repo / "docs" / "SOP").mkdir(parents=True)
        (self.repo / "docs" / "SOP" / "MSOS_FRONTIER.md").write_text(
            "\n".join(
                [
                    "### Current execution focus",
                    "- **Active BUILD chapter:** **MSOS P3** — **READY**",
                    "",
                    "| **NEXT** | `MSOS-P3-Control-Slice001` — charter | EVIDENCE |",
                ]
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(
            "### MVP1\n| **CLOSED** | slice |\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _seed_changelog(self) -> None:
        parsed = ParsedChangelog(
            sections={
                "2026-06-03": [
                    "- `4169985` — MSOS P3: Command Center shell (#85) (`apps/msos-web/`)",
                    "- `a3b50ed` — control: SELECTION MSOS P3 Command Center (#82) (`docs/SOP/`)",
                ],
                "2026-06-02": [
                    "- `d89b321` — MSOS P2: public homepage + chapter closeout (#80) (`apps/msos-web/`)",
                ],
            }
        )
        save_changelog(self.repo, parsed)

    def test_classify_product_vs_ops(self) -> None:
        self.assertEqual(
            classify_bullet("- `x` — control: SELECTION MSOS P3 (`docs/SOP/`)"),
            "ops",
        )
        self.assertEqual(
            classify_bullet("- MSOS P3: Command Center shell (`apps/msos-web/`)"),
            "product",
        )

    def test_humanize_msos_product(self) -> None:
        line = humanize_product_bullet(
            "- `d89b321` — MSOS P2: public homepage + chapter closeout (#80) (`apps/msos-web/`)"
        )
        self.assertIn("homepage (P2)", line)

    def test_build_week_section(self) -> None:
        self._seed_changelog()
        week_monday = date(2026, 6, 1)
        section = build_week_section(self.repo, week_monday)
        self.assertEqual(section.week_monday, "2026-06-01")
        self.assertTrue(section.product_lines)
        self.assertIn("homepage", section.in_short.lower())
        self.assertGreaterEqual(section.merge_count, 2)

    def test_week_dates_monday_to_sunday(self) -> None:
        mon = date(2026, 6, 1)
        self.assertEqual(week_dates(mon)[0], "2026-06-01")
        self.assertEqual(week_dates(mon)[-1], "2026-06-07")

    def test_last_completed_week_monday(self) -> None:
        # Monday 2026-06-08 -> prior week starts 2026-06-01
        ref = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)
        self.assertEqual(last_completed_week_monday(ref), date(2026, 6, 1))

    def test_parse_latest_week_summary(self) -> None:
        md = "\n".join(
            [
                "# Weekly digest",
                "",
                "## Week of 2026-06-01 (Mon–Sun UTC)",
                "",
                "**In short:** This week: homepage shipped.",
                "",
                "### Receipt",
                "- 3 merge(s) to `main` — detail in [DEV_CHANGELOG.md](DEV_CHANGELOG.md).",
                "",
                "## Week of 2026-05-25 (Mon–Sun UTC)",
                "",
                "**In short:** Older week.",
            ]
        )
        summary = parse_latest_week_summary(md)
        assert summary is not None
        assert summary["week_monday"] == "2026-06-01"
        assert "homepage" in summary["in_short"]
        assert summary["merge_count"] == 3

    def test_write_notify_payload(self) -> None:
        self._seed_changelog()
        cmd_backfill(self.repo, weeks=1)
        self.assertEqual(cmd_write_notify_payload(self.repo), 0)
        payload = notify_payload_path(self.repo)
        self.assertTrue(payload.is_file())
        assert "in_short" in payload.read_text(encoding="utf-8")

    def test_generate_and_backfill_idempotent(self) -> None:
        self._seed_changelog()
        self.assertEqual(cmd_backfill(self.repo, weeks=2), 0)
        text = (self.repo / "docs" / "RELEASES" / "WEEKLY_DIGEST.md").read_text(encoding="utf-8")
        self.assertIn("Week of", text)
        self.assertIn("What shipped", text)
        state1 = load_state(self.repo)
        self.assertGreaterEqual(len(state1.recorded_weeks), 1)
        self.assertEqual(cmd_generate(self.repo, week_monday=date(2026, 6, 1)), 0)
        self.assertEqual(cmd_generate(self.repo, week_monday=date(2026, 6, 1)), 0)


if __name__ == "__main__":
    unittest.main()
