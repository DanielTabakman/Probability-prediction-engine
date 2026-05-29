"""Tests for PPE continuous operator guardrails."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_guards import (
    assess_phase_plan,
    sprint_context_band,
)
from scripts.ppe_slice_worker_mode import resolve_worker_mode


class TestPpeOperatorGuards(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        self.plan_path = "docs/SOP/PHASE_PLANS/test_relay.json"
        sprint = self.repo / "docs" / "SOP" / "SPRINT_TEST.md"
        sprint.write_text("# sprint\n", encoding="utf-8")
        (sop / "test_relay.json").write_text(
            json.dumps(
                {
                    "name": "test",
                    "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                    "slices": [
                        {
                            "sliceId": "MVP1-Test-Product-Slice002",
                            "declaredPlane": "PRODUCT-PLANE",
                            "touchSet": ["src/foo.py"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        os.environ.pop("PPE_WORKER_MODE", None)
        os.environ.pop("PPE_SKIP_ACP", None)
        self._tmp.cleanup()

    def test_context_escalate(self) -> None:
        sprint = self.repo / "docs" / "SOP" / "SPRINT_TEST.md"
        sprint.write_text("\n".join(f"line {i}" for i in range(450)), encoding="utf-8")
        self.assertEqual(sprint_context_band(self.repo, "docs/SOP/SPRINT_TEST.md"), "ESCALATE")
        v = assess_phase_plan(self.repo, self.plan_path)
        self.assertFalse(v.ok)
        self.assertEqual(v.code, "CONTEXT_ESCALATE")

    def test_product_blocked_under_deterministic(self) -> None:
        os.environ["PPE_WORKER_MODE"] = "deterministic"
        v = assess_phase_plan(self.repo, self.plan_path)
        self.assertFalse(v.ok)
        self.assertEqual(v.code, "PRODUCT_BLOCKED")

    def test_product_allowed_with_local_agent_override(self) -> None:
        os.environ["PPE_WORKER_MODE"] = "deterministic"
        plan = json.loads((self.repo / self.plan_path).read_text(encoding="utf-8"))
        plan["slices"][0]["workerMode"] = "local-agent"
        (self.repo / self.plan_path).write_text(json.dumps(plan), encoding="utf-8")
        v = assess_phase_plan(self.repo, self.plan_path)
        self.assertTrue(v.ok)
        self.assertEqual(
            resolve_worker_mode(
                slice_id="MVP1-Test-Product-Slice002",
                slice_obj={"workerMode": "local-agent"},
            ),
            "local-agent",
        )

    def test_product_requires_touch_set(self) -> None:
        plan = json.loads((self.repo / self.plan_path).read_text(encoding="utf-8"))
        plan["slices"][0]["workerMode"] = "local-agent"
        plan["slices"][0].pop("touchSet", None)
        (self.repo / self.plan_path).write_text(json.dumps(plan), encoding="utf-8")
        v = assess_phase_plan(self.repo, self.plan_path)
        self.assertFalse(v.ok)
        self.assertEqual(v.code, "PRODUCT_NO_TOUCH_SET")


if __name__ == "__main__":
    unittest.main()
