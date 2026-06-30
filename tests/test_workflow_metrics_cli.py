"""Tests for workflow_metrics_cli."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_tracking_hub import record_event
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
        self.assertEqual(cmd_slice_close(self.repo, slice_id="Slice-A", size="M", roundtrips=2), 0)
        self.assertEqual(cmd_session_stop(self.repo, cognitive_load=3, roundtrips=2), 0)
        self.assertEqual(cmd_summary(self.repo, days=7), 0)
        self.assertEqual(cmd_export_csv(self.repo), 0)
        csv_path = self.repo / "artifacts" / "workflow_metrics" / "weekly_summary.csv"
        self.assertIn("Slice-A", csv_path.read_text(encoding="utf-8"))

    def test_session_stop_without_start_fails(self) -> None:
        self.assertEqual(cmd_session_stop(self.repo, cognitive_load=2), 1)

    def test_slice_close_with_worker_lane(self) -> None:
        self.assertEqual(
            cmd_slice_close(
                self.repo,
                slice_id="Slice-B",
                size="S",
                roundtrips=1,
                worker_lane="manual",
                source="manual",
            ),
            0,
        )
        cmd_export_csv(self.repo)
        text = (self.repo / "artifacts" / "workflow_metrics" / "weekly_summary.csv").read_text(encoding="utf-8")
        self.assertIn("worker_lane", text)

    def test_export_csv_includes_events(self) -> None:
        record_event(self.repo, event_type="usage_note", note="csv-test")
        self.assertEqual(cmd_export_csv(self.repo), 0)
        events_csv = self.repo / "artifacts" / "workflow_metrics" / "events_export.csv"
        self.assertTrue(events_csv.is_file())
        self.assertIn("usage_note", events_csv.read_text(encoding="utf-8"))

    def test_export_csv_includes_product_usage(self) -> None:
        usage_path = self.repo / "data" / "ppe_product_usage.jsonl"
        usage_path.parent.mkdir(parents=True)
        usage_path.write_text(
            '{"event_name":"lab_view","created_at_utc":"2026-06-30T12:00:00Z"}\n',
            encoding="utf-8",
        )
        self.assertEqual(cmd_export_csv(self.repo), 0)
        usage_csv = self.repo / "artifacts" / "workflow_metrics" / "product_usage_export.csv"
        self.assertTrue(usage_csv.is_file())
        text = usage_csv.read_text(encoding="utf-8")
        self.assertIn("lab_view", text)
        self.assertIn("total_events", text)

    def test_summary_by_lane(self) -> None:
        cmd_slice_close(
            self.repo,
            slice_id="Slice-C",
            size="M",
            roundtrips=0,
            worker_lane="deterministic-local",
            source="relay_closeout",
        )
        self.assertEqual(cmd_summary(self.repo, days=7, by_lane=True), 0)


if __name__ == "__main__":
    unittest.main()
