"""Tests for PPE_AUTO_OPERATOR.json wiring."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_config import (
    apply_operator_env,
    operator_enabled,
    steward_charter_enabled,
)
from scripts.ppe_steward_cursor import needs_steward_charter


class TestPpeOperatorConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "enabled": True,
                    "propagateBacklog": True,
                    "stewardCharter": True,
                }
            ),
            encoding="utf-8",
        )
        (sop / "AGENT_CONTINUITY_BRIEF.md").write_text("# brief\n", encoding="utf-8")
        (sop / "MVP1_FRONTIER.md").write_text("# frontier\n", encoding="utf-8")
        (sop / "PPE_INTEGRATED_STATUS.md").write_text("# status\n", encoding="utf-8")
        (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps({"version": 1, "items": [{"planPath": "docs/SOP/PHASE_PLANS/done.json", "status": "done"}]}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        from scripts.ppe_manifest import save_manifest

        save_manifest(self.repo, {"phasePlanPath": "", "status": "COMPLETE", "notes": ""})
        os.environ.pop("PPE_AUTO_STEWARD", None)

    def tearDown(self) -> None:
        os.environ.pop("PPE_AUTO_STEWARD", None)
        os.environ.pop("PPE_AUTO_PROPAGATE_QUEUE", None)
        self._tmp.cleanup()

    def test_operator_enabled(self) -> None:
        self.assertTrue(operator_enabled(self.repo))

    def test_steward_from_config_without_env(self) -> None:
        self.assertTrue(steward_charter_enabled(self.repo))
        need, _ = needs_steward_charter(self.repo)
        self.assertTrue(need)

    def test_apply_operator_env_sets_steward(self) -> None:
        out = apply_operator_env(self.repo)
        self.assertTrue(out.get("applied"))
        self.assertEqual(os.environ.get("PPE_AUTO_STEWARD"), "1")
        self.assertEqual(os.environ.get("PPE_AUTO_PROPAGATE_QUEUE"), "1")
