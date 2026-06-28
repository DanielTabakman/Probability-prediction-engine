"""Tests for ppe_workflow_cost."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_workflow_cost import (
    default_size_for_slice,
    infer_relay_worker_lane,
    maybe_record_slice_close,
    record_relay_closeout,
    slice_already_recorded,
    summarize_by_lane,
    worker_mode_to_lane,
)
from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _read_jsonl


class TestPpeWorkflowCost(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_worker_mode_to_lane(self) -> None:
        self.assertEqual(worker_mode_to_lane("deterministic"), "deterministic-local")

    def test_auto_record_dedupes(self) -> None:
        self.assertTrue(
            maybe_record_slice_close(
                self.repo,
                slice_id="Slice-A",
                source="relay_closeout",
                worker_lane="deterministic-local",
                size="S",
                roundtrips=0,
            )
        )
        self.assertFalse(
            maybe_record_slice_close(
                self.repo,
                slice_id="Slice-A",
                source="relay_closeout",
                worker_lane="deterministic-local",
            )
        )
        rows = _read_jsonl(_metrics_dir(self.repo) / SLICES_FILE)
        self.assertEqual(len(rows), 1)

    def test_summarize_by_lane(self) -> None:
        maybe_record_slice_close(
            self.repo, slice_id="L1", source="relay_closeout", worker_lane="deterministic-local", size="S", roundtrips=0
        )
        maybe_record_slice_close(
            self.repo, slice_id="I1", source="ide_product_ready", worker_lane="manual", size="M", roundtrips=2
        )
        summary = summarize_by_lane(self.repo, days=7)
        self.assertEqual(summary["slices_logged"], 2)
        self.assertEqual(summary["by_lane"]["deterministic-local"], 1)

    def test_record_relay_closeout(self) -> None:
        plan_path = self.repo / "plan.json"
        plan_path.write_text(
            '{"slices":[{"sliceId":"Test-Witness-Slice001","workerMode":"deterministic"}]}',
            encoding="utf-8",
        )
        self.assertTrue(record_relay_closeout(self.repo, slice_id="Test-Witness-Slice001", plan_path=plan_path))
        self.assertTrue(slice_already_recorded(self.repo, "Test-Witness-Slice001"))

    def test_default_size(self) -> None:
        self.assertEqual(default_size_for_slice("Foo-Product-Slice002", None), "M")
        self.assertEqual(default_size_for_slice("Foo-Control-Slice001", None), "S")

    def test_infer_relay_lane(self) -> None:
        lane = infer_relay_worker_lane(
            self.repo, slice_id="PPE-Test-Control-Slice001", slice_obj={"workerMode": "deterministic"}
        )
        self.assertEqual(lane, "deterministic-local")


if __name__ == "__main__":
    unittest.main()
