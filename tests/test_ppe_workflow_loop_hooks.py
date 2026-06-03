"""Tests for ppe_workflow_loop_hooks."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_workflow_loop_hooks import on_guard_stop, on_loop_start
from scripts.workflow_metrics_cli import _read_jsonl, _metrics_dir, EVENTS_FILE, SESSIONS_FILE


def _operator_json(**workflow: object) -> str:
    return json.dumps(
        {
            "enabled": True,
            "workflowEfficiency": {
                "enabled": True,
                "trackMetrics": True,
                "autoGenerateIdeStarter": True,
                **workflow,
            },
        }
    )


class TestPpeWorkflowLoopHooks(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plans.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(_operator_json(), encoding="utf-8")
        (sop / "REPO_LAYER_PATH_PREFIXES.json").write_text(
            json.dumps(
                {
                    "presets": {
                        "MSOS_UI": {
                            "layer": "msos-shell",
                            "allowed_paths": ["apps/msos-web/"],
                            "forbidden_paths": ["src/"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        (sop / "AGENT_CONTINUITY_BRIEF.md").write_text("# brief\n\n## Chapter status\n\nOK\n", encoding="utf-8")
        (sop / "SPRINT_TEST.md").write_text(
            "## Sprint intent\n\nBuild thing.\n\n## Slice map\n\n| **Test-Product-Slice001** | PRODUCT | MSOS_UI | x |\n",
            encoding="utf-8",
        )
        plan = {
            "baselineBranch": "main",
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {
                    "sliceId": "Test-Product-Slice001",
                    "declaredPlane": "PRODUCT-PLANE",
                    "layerPreset": "MSOS_UI",
                    "buildBranch": "build/auto/Test-Product-Slice001",
                }
            ],
        }
        self.plan_path = "docs/SOP/PHASE_PLANS/test.json"
        (plans / "test.json").write_text(json.dumps(plan), encoding="utf-8")
        os.environ["PPE_SKIP_ACP"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_SKIP_ACP", None)
        self._tmp.cleanup()

    def test_loop_start_creates_session(self) -> None:
        on_loop_start(self.repo)
        sessions = _read_jsonl(_metrics_dir(self.repo) / SESSIONS_FILE)
        self.assertTrue(any(r.get("event") == "session_start" for r in sessions))

    def test_guard_stop_generates_starter_and_event(self) -> None:
        extra = on_guard_stop(
            self.repo,
            reason="PRODUCT_BLOCKED",
            plan_path=self.plan_path,
            detail="test",
            slice_id="Test-Product-Slice001",
        )
        self.assertIn("IDE_BUILD_STARTER", extra)
        starter = self.repo / "artifacts/orchestrator/IDE_BUILD_STARTER_Test-Product-Slice001.md"
        self.assertTrue(starter.is_file())
        events = _read_jsonl(_metrics_dir(self.repo) / EVENTS_FILE)
        self.assertTrue(any(e.get("event_type") == "guard_stop" for e in events))


if __name__ == "__main__":
    unittest.main()
