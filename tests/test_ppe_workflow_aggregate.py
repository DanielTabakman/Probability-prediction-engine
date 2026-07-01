"""Tests for ppe_workflow_aggregate.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_workflow_aggregate import record_thread_pulse, summarize_aggregate
from scripts.workflow_metrics_cli import append_slice_close_row


class TestPpeWorkflowAggregate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_pulse_and_aggregate(self) -> None:
        append_slice_close_row(self.repo, slice_id="Slice-A", size="M", roundtrips=2, source="test")
        self.assertEqual(record_thread_pulse(self.repo, cognitive_load=4, non_interactive=True), 0)
        stats = summarize_aggregate(self.repo, days=7)
        self.assertEqual(stats["slices_logged"], 1)
        self.assertEqual(stats["weighted_slices"], 2)
        self.assertEqual(stats["thread_pulses"], 1)
        self.assertEqual(stats["avg_cognitive_load"], 4.0)
        self.assertEqual(stats["mode"], "aggregate")


if __name__ == "__main__":
    unittest.main()
