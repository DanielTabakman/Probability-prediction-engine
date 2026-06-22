"""Tests for ppe_monday_morning_prep."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.ppe_monday_morning_prep import (
    cmd_prep,
    run_monday_prep,
    wait_until_report_time,
)


class TestPpeMondayMorningPrep(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "artifacts" / "orchestrator").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_wait_until_report_time_already_past(self) -> None:
        with mock.patch("scripts.ppe_monday_morning_prep.time.sleep") as sleep:
            waited = wait_until_report_time(hour=0, minute=0)
        self.assertEqual(waited, 0.0)
        sleep.assert_not_called()

    def test_wait_until_report_time_sleeps(self) -> None:
        from datetime import datetime

        fake_now = datetime(2026, 6, 15, 6, 30, 0)
        with (
            mock.patch("scripts.ppe_monday_morning_prep.datetime") as dt_mod,
            mock.patch("scripts.ppe_monday_morning_prep.time.sleep") as sleep,
        ):
            dt_mod.now.return_value = fake_now
            waited = wait_until_report_time(hour=8, minute=0)
        self.assertAlmostEqual(waited, 90 * 60, delta=1)
        sleep.assert_called_once()

    def test_prep_writes_log(self) -> None:
        with (
            mock.patch("scripts.ppe_workflow_radar.auto_cleanup_orphans", return_value=[]),
            mock.patch("scripts.ppe_manifest.load_manifest", side_effect=FileNotFoundError),
        ):
            report = run_monday_prep(self.repo)
        self.assertIn("summary", report)
        log = self.repo / "artifacts/control_plane/MONDAY_MORNING_PREP_LATEST.json"
        self.assertTrue(log.is_file())
        data = json.loads(log.read_text(encoding="utf-8"))
        self.assertIn("steps", data)

    def test_cmd_prep_exit_zero(self) -> None:
        with mock.patch("scripts.ppe_workflow_radar.auto_cleanup_orphans", return_value=[]):
            with mock.patch("scripts.ppe_manifest.load_manifest", side_effect=FileNotFoundError):
                self.assertEqual(cmd_prep(self.repo), 0)


if __name__ == "__main__":
    unittest.main()
