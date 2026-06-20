"""Tests for PPE_AUTO_OPERATOR.json wiring."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_config import (
    OPERATOR_PROFILE_REL,
    apply_operator_env,
    operator_config_path,
    operator_enabled,
    steward_charter_enabled,
    skip_acp_from_config,
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
                    "skipAcp": True,
                }
            ),
            encoding="utf-8",
        )
        (sop / "PPE_AUTO_OPERATOR.local.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "enabled": True,
                    "stewardCharter": False,
                    "skipAcp": True,
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
        os.environ.pop("PPE_OPERATOR_PROFILE", None)
        os.environ.pop("PPE_SKIP_ACP", None)

    def tearDown(self) -> None:
        os.environ.pop("PPE_AUTO_STEWARD", None)
        os.environ.pop("PPE_AUTO_PROPAGATE_QUEUE", None)
        os.environ.pop("PPE_OPERATOR_PROFILE", None)
        os.environ.pop("PPE_SKIP_ACP", None)
        self._tmp.cleanup()

    def test_operator_enabled(self) -> None:
        self.assertTrue(operator_enabled(self.repo))

    def test_steward_disabled_when_skip_acp_in_config(self) -> None:
        self.assertFalse(steward_charter_enabled(self.repo))
        need, _ = needs_steward_charter(self.repo)
        self.assertFalse(need)

    def test_steward_enabled_when_skip_acp_false(self) -> None:
        cfg_path = self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["skipAcp"] = False
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        self.assertTrue(steward_charter_enabled(self.repo))
        need, _ = needs_steward_charter(self.repo)
        self.assertTrue(need)

    def test_apply_operator_env_skips_steward_when_skip_acp(self) -> None:
        out = apply_operator_env(self.repo)
        self.assertTrue(out.get("applied"))
        self.assertEqual(os.environ.get("PPE_SKIP_ACP"), "1")
        self.assertIsNone(os.environ.get("PPE_AUTO_STEWARD"))

    def test_local_profile_path(self) -> None:
        os.environ["PPE_OPERATOR_PROFILE"] = "local"
        expected = (self.repo / OPERATOR_PROFILE_REL["local"]).resolve()
        self.assertEqual(operator_config_path(self.repo), expected)
        self.assertFalse(steward_charter_enabled(self.repo))

    def test_local_profile_from_base_config_when_env_unset(self) -> None:
        base = self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json"
        cfg = json.loads(base.read_text(encoding="utf-8"))
        cfg["profile"] = "local"
        base.write_text(json.dumps(cfg), encoding="utf-8")
        expected = (self.repo / OPERATOR_PROFILE_REL["local"]).resolve()
        self.assertEqual(operator_config_path(self.repo), expected)

    def test_skip_acp_from_config_default(self) -> None:
        self.assertTrue(skip_acp_from_config({"skipAcp": True}))
        self.assertFalse(skip_acp_from_config({"skipAcp": False}))


if __name__ == "__main__":
    unittest.main()
