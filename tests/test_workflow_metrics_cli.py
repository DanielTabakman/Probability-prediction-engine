"""Tests for workflow_metrics_cli."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.workflow_metrics_cli import (
    cmd_export_csv,
    cmd_session_start,
    cmd_session_stop,
    cmd_slice_close,
    cmd_summary,
)


class TestWorkflowMetricsCli(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_session_and_slice_flow(self) -> None:
        self.assertEqual(cmd_session_start(self.repo), 0)
        self.assertEqual(
            cmd_slice_close(
                self.repo,
                slice_id="Slice-A",
                size="M",
                roundtrips=2,
            ),
            0,
        )
        self.assertEqual(
            cmd_session_stop(self.repo, cognitive_load=3, roundtrips=2),
            0,
        )
        self.assertEqual(cmd_summary(self.repo, days=7), 0)
        self.assertEqual(cmd_export_csv(self.repo), 0)
        csv_path = self.repo / "artifacts" / "workflow_metrics" / "weekly_summary.csv"
        self.assertTrue(csv_path.is_file())
        self.assertIn("Slice-A", csv_path.read_text(encoding="utf-8"))

    def test_session_stop_without_start_fails(self) -> None:
        self.assertEqual(cmd_session_stop(self.repo, cognitive_load=2), 1)


if __name__ == "__main__":
    unittest.main()
