"""Tests for explicit product-slice runner (token economy)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ppe_manifest import MANIFEST_REL, save_manifest
from scripts.ppe_run_product_slice import (
    apply_product_slice_env,
    main,
    validate_product_slice,
)


def _minimal_product_plan(slice_id: str = "MVP1-Test-Product-Slice002", *, touch: bool = True) -> dict:
    sl: dict = {
        "sliceId": slice_id,
        "declaredPlane": "PRODUCT-PLANE",
        "workerMode": "local-agent",
    }
    if touch:
        sl["touchSet"] = ["src/foo.py"]
    return {
        "name": "test",
        "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
        "slices": [
            sl,
            {
                "sliceId": "MVP1-Test-Closeout-Slice003",
                "closeout": {"chapterId": "test"},
            },
        ],
    }


class TestPpeRunProductSlice(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text("# sprint\n", encoding="utf-8")
        self.plan_rel = "docs/SOP/PHASE_PLANS/test_relay.json"
        (sop / "test_relay.json").write_text(
            json.dumps(_minimal_product_plan()),
            encoding="utf-8",
        )
        save_manifest(
            self.repo,
            {
                "phasePlanPath": self.plan_rel,
                "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                "status": "READY",
            },
        )
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps({"enabled": True, "skipAcp": True}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        for key in (
            "PPE_SKIP_ACP",
            "PPE_WORKER_MODE",
            "PPE_OPERATOR_ENV_APPLIED",
            "PPE_RUN_KIND",
        ):
            os.environ.pop(key, None)
        self._tmp.cleanup()

    def test_validate_ok(self) -> None:
        plan, sl = validate_product_slice(
            self.repo,
            slice_id="MVP1-Test-Product-Slice002",
            plan_path=self.plan_rel,
            require_touch_set=True,
        )
        self.assertIn("slices", plan)
        self.assertEqual(sl["workerMode"], "local-agent")

    def test_validate_missing_slice(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_product_slice(
                self.repo,
                slice_id="MVP1-Missing",
                plan_path=self.plan_rel,
            )
        self.assertIn("not found", str(ctx.exception))

    def test_validate_non_product(self) -> None:
        plan = _minimal_product_plan("MVP1-Test-Control-Slice001")
        plan["slices"] = [
            {"sliceId": "MVP1-Test-Control-Slice001", "declaredPlane": "EVIDENCE-PLANE"},
            {"sliceId": "MVP1-Test-Closeout-Slice003", "closeout": {"chapterId": "x"}},
        ]
        (self.repo / self.plan_rel).write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            validate_product_slice(
                self.repo,
                slice_id="MVP1-Test-Control-Slice001",
                plan_path=self.plan_rel,
            )
        self.assertIn("not a product slice", str(ctx.exception))

    def test_validate_empty_touch_set(self) -> None:
        plan = _minimal_product_plan(touch=False)
        (self.repo / self.plan_rel).write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            validate_product_slice(
                self.repo,
                slice_id="MVP1-Test-Product-Slice002",
                plan_path=self.plan_rel,
                require_touch_set=True,
            )
        self.assertIn("touchSet", str(ctx.exception))

    def test_apply_product_slice_env(self) -> None:
        apply_product_slice_env()
        self.assertEqual(os.environ.get("PPE_SKIP_ACP"), "0")
        self.assertEqual(os.environ.get("PPE_WORKER_MODE"), "local-agent")
        self.assertEqual(os.environ.get("PPE_OPERATOR_ENV_APPLIED"), "1")
        self.assertEqual(os.environ.get("PPE_RUN_KIND"), "product_slice")

    @patch("scripts.ppe_run.main", return_value=0)
    def test_main_sets_env_and_delegates(self, mock_run: MagicMock) -> None:
        rc = main(
            [
                "--repo-root",
                str(self.repo),
                "--slice-id",
                "MVP1-Test-Product-Slice002",
                "--plan",
                self.plan_rel,
            ]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(os.environ.get("PPE_SKIP_ACP"), "0")
        self.assertEqual(os.environ.get("PPE_WORKER_MODE"), "local-agent")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("--slice", args)
        self.assertIn("MVP1-Test-Product-Slice002", args)

    def test_main_validation_exit_2(self) -> None:
        rc = main(["--repo-root", str(self.repo), "--slice-id", "MVP1-Missing"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
