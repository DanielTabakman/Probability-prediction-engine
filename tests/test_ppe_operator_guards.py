"""Tests for continuous operator guards."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_guards import GUARD_EXIT, run_continuous_guards


class TestPpeOperatorGuards(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plans.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps(
                {
                    "enabled": True,
                    "guards": {"enabled": True, "blockProductUnderGlobalDeterministic": True},
                }
            ),
            encoding="utf-8",
        )
        plan = {
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Product-Slice002"},
                {"sliceId": "Ch-Closeout-Slice003", "closeout": True},
            ],
        }
        (plans / "test_relay.json").write_text(json.dumps(plan), encoding="utf-8")
        os.environ["PPE_SKIP_ACP"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_SKIP_ACP", None)
        os.environ.pop("PPE_OPERATOR_GUARDS", None)
        self._tmp.cleanup()

    def test_product_plan_blocked_under_skip_acp(self) -> None:
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/test_relay.json")
        self.assertEqual(rc, GUARD_EXIT)
        report = self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
        self.assertTrue(report.is_file())
        self.assertIn("PRODUCT_BLOCKED", report.read_text(encoding="utf-8"))

    def test_evidence_only_plan_ok(self) -> None:
        plan = {
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Smoke-Slice002"},
            ],
        }
        path = self.repo / "docs/SOP/PHASE_PLANS/evidence.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/evidence.json")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
