"""Tests for PPE_AUTO_OPERATOR.json wiring."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_config import (
    apply_operator_env,
    load_operator_config,
    operator_enabled,
    operator_env_cmd_lines,
    planned_operator_env,
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
                    "skipAcp": False,
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

    def test_skip_acp_disables_steward_charter_from_config(self) -> None:
        cfg_path = self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["skipAcp"] = True
        cfg["stewardCharter"] = True
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        os.environ.pop("PPE_AUTO_STEWARD", None)
        self.assertFalse(steward_charter_enabled(self.repo))
        planned = planned_operator_env(self.repo)
        self.assertNotIn("PPE_AUTO_STEWARD", planned)
        self.assertEqual(planned.get("PPE_SKIP_ACP"), "1")
        lines = operator_env_cmd_lines(self.repo)
        self.assertTrue(any("PPE_SKIP_ACP" in ln for ln in lines))
        self.assertFalse(any("PPE_AUTO_STEWARD" in ln for ln in lines))

    def test_operator_profile_local(self) -> None:
        from scripts.ppe_operator_config import active_operator_profile, operator_config_path

        local = self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.local.json"
        local.write_text(
            json.dumps({"version": 1, "profile": "local", "enabled": True, "skipAcp": True, "workerMode": "deterministic"}),
            encoding="utf-8",
        )
        os.environ["PPE_OPERATOR_PROFILE"] = "local"
        self.assertEqual(
            operator_config_path(self.repo).name,
            "PPE_AUTO_OPERATOR.local.json",
        )
        local_cfg = load_operator_config(self.repo)
        self.assertTrue(local_cfg.get("skipAcp"))
        self.assertEqual(active_operator_profile(self.repo), "local")
        os.environ.pop("PPE_OPERATOR_PROFILE", None)

    def test_operator_profile_acp(self) -> None:
        from scripts.ppe_operator_config import operator_config_path, planned_operator_env

        acp = self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.acp.json"
        acp.write_text(
            json.dumps(
                {
                    "version": 1,
                    "profile": "acp",
                    "enabled": True,
                    "skipAcp": False,
                    "workerMode": "acp",
                    "stewardCharter": True,
                    "propagateBacklog": True,
                }
            ),
            encoding="utf-8",
        )
        os.environ["PPE_OPERATOR_PROFILE"] = "acp"
        self.assertEqual(
            operator_config_path(self.repo).name,
            "PPE_AUTO_OPERATOR.acp.json",
        )
        planned = planned_operator_env(self.repo)
        self.assertNotIn("PPE_SKIP_ACP", planned)
        self.assertEqual(planned.get("PPE_WORKER_MODE"), "acp")
        self.assertEqual(planned.get("PPE_AUTO_STEWARD"), "1")
        os.environ.pop("PPE_OPERATOR_PROFILE", None)
