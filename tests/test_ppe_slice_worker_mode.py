"""Tests for PPE worker mode resolution."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.ppe_slice_worker_mode import infer_slice_kind, resolve_worker_mode


class TestPpeSliceWorkerMode(unittest.TestCase):
    def test_infer_closeout(self) -> None:
        self.assertEqual(
            infer_slice_kind("MVP1-Foo-Closeout-Slice003", {"closeout": {"chapterId": "x"}}),
            "closeout",
        )

    def test_infer_smoke(self) -> None:
        self.assertEqual(infer_slice_kind("MVP1-Foo-Smoke-Slice002", None), "smoke")

    def test_plan_worker_mode(self) -> None:
        self.assertEqual(
            resolve_worker_mode(
                slice_id="MVP1-Foo-Product-Slice002",
                slice_obj={"workerMode": "deterministic"},
            ),
            "deterministic",
        )

    def test_skip_acp_env(self) -> None:
        with patch.dict(os.environ, {"PPE_SKIP_ACP": "1"}, clear=False):
            self.assertEqual(
                resolve_worker_mode(slice_id="MVP1-Foo-Product-Slice002", slice_obj=None),
                "deterministic",
            )

    def test_global_deterministic_overrides_plan_local_agent(self) -> None:
        with patch.dict(os.environ, {"PPE_WORKER_MODE": "deterministic"}, clear=False):
            self.assertEqual(
                resolve_worker_mode(
                    slice_id="MVP1-Foo-Product-Slice002",
                    slice_obj={"workerMode": "local-agent"},
                ),
                "deterministic",
            )

    def test_auto_deterministic_control(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PPE_WORKER_MODE", None)
            os.environ.pop("PPE_SKIP_ACP", None)
            self.assertEqual(
                resolve_worker_mode(
                    slice_id="MVP1-Foo-Control-Slice001",
                    slice_obj=None,
                ),
                "deterministic",
            )


if __name__ == "__main__":
    unittest.main()
