"""Tests for scripts/ppe_operator_status.py."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_guards import GUARD_EXIT
from scripts.ppe_operator_status import (
    VERDICT_IDE_BUILD,
    VERDICT_RUN_AUTO,
    VERDICT_RUN_LOCAL,
    VERDICT_SUPPLY_LOW,
    collect_operator_status,
)


def _operator_json(**guards: object) -> str:
    return json.dumps(
        {
            "enabled": True,
            "guards": {"enabled": True, **guards},
        }
    )


class TestPpeOperatorStatus(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plans.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            _operator_json(blockProductUnderGlobalDeterministic=True),
            encoding="utf-8",
        )
        os.environ["PPE_SKIP_ACP"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_SKIP_ACP", None)
        self._tmp.cleanup()

    def _write_manifest(self, *, plan: str, status: str = "READY") -> None:
        sop = self.repo / "docs" / "SOP"
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": plan, "status": status}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [{"planPath": plan, "status": "READY"}],
                }
            ),
            encoding="utf-8",
        )

    def test_ide_build_verdict_for_product_plan(self) -> None:
        plan = {
            "name": "Test chapter",
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Product-Slice002"},
                {"sliceId": "Ch-Closeout-Slice003", "closeout": {"chapterId": "ch"}},
            ],
        }
        plan_path = "docs/SOP/PHASE_PLANS/test_relay.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "test_relay.json").write_text(
            json.dumps(plan),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text("spec\n", encoding="utf-8")
        self._write_manifest(plan=plan_path)

        status = collect_operator_status(self.repo)
        self.assertEqual(status["verdict"], VERDICT_IDE_BUILD)
        self.assertEqual(status["exit_code"], GUARD_EXIT)
        self.assertTrue(any("generate_ide_build_starter.cmd" in c for c in status["commands"]))

    def test_run_auto_for_evidence_plan(self) -> None:
        plan_path = "docs/SOP/PHASE_PLANS/evidence.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "evidence.json").write_text(
            json.dumps(
                {
                    "name": "Evidence",
                    "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                    "slices": [
                        {"sliceId": "Ch-Control-Slice001"},
                        {"sliceId": "Ch-Closeout-Slice002", "closeout": {"chapterId": "ch"}},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text("ok\n", encoding="utf-8")
        self._write_manifest(plan=plan_path)

        status = collect_operator_status(self.repo)
        self.assertEqual(status["verdict"], VERDICT_RUN_AUTO)
        self.assertEqual(status["exit_code"], 0)

    def test_supply_low_when_idle(self) -> None:
        sop = self.repo / "docs" / "SOP"
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"status": "COMPLETE", "phasePlanPath": ""}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps({"version": 1, "items": [{"chapterId": "done1", "status": "done", "planPath": "x"}]}),
            encoding="utf-8",
        )

        status = collect_operator_status(self.repo)
        self.assertEqual(status["verdict"], VERDICT_SUPPLY_LOW)
        self.assertEqual(status["exit_code"], 0)

    def test_run_local_when_marker_covers_product(self) -> None:
        plan_path = "docs/SOP/PHASE_PLANS/test_relay.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "test_relay.json").write_text(
            json.dumps(
                {
                    "name": "Test",
                    "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                    "slices": [
                        {"sliceId": "Ch-Product-Slice002", "buildBranch": "build/test-branch"},
                        {"sliceId": "Ch-Closeout-Slice003", "closeout": {"chapterId": "ch"}},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text("ok\n", encoding="utf-8")
        self._write_manifest(plan=plan_path)
        (self.repo / "artifacts" / "orchestrator").mkdir(parents=True)
        (self.repo / "artifacts" / "orchestrator" / "IDE_PRODUCT_READY.json").write_text(
            json.dumps(
                {
                    "phasePlanPath": plan_path,
                    "sliceId": "Ch-Product-Slice002",
                    "buildBranch": "build/test-branch",
                }
            ),
            encoding="utf-8",
        )

        from unittest.mock import patch

        with patch(
            "scripts.ppe_ide_product_ready._branch_has_commits",
            return_value=True,
        ):
            status = collect_operator_status(self.repo)
        self.assertEqual(status["verdict"], VERDICT_RUN_LOCAL)
        self.assertEqual(status["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
