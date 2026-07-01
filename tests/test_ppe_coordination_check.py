"""Tests for coordination check synthesizer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_coordination_check import (
    VERDICT_PARK,
    VERDICT_PROCEED,
    VERDICT_RECOVERY,
    VERDICT_REPAIR,
    assess_coordination_check,
    write_coordination_check,
)


class TestCoordinationCheck(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        (sop / "AGENT_STEERING_V1.json").write_text(json.dumps({"version": 1}), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_proceed_when_clean(self) -> None:
        status = {
            "verdict": "RUN_LOCAL",
            "phase_plan_path": "",
            "branch_preflight": {"blocks_relay": False, "reasons": [], "commands": []},
            "preflight_warnings": [],
            "delegation_hint": None,
        }
        with patch("scripts.ppe_chapter_coordination.audit_repo", return_value=[]):
            with patch(
                "scripts.ppe_operator_blind_spots.assess_operator_blind_spots",
                return_value={"issues": []},
            ):
                payload = assess_coordination_check(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_PROCEED)
        self.assertFalse(payload["blocks_burst"])

    def test_recovery_when_branch_blocks_relay(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/x_relay.json",
            "branch_preflight": {
                "blocks_relay": True,
                "reasons": ["checkout is 'product/foo'"],
                "commands": ["git checkout main"],
                "branch": "product/foo",
            },
            "preflight_warnings": [],
            "delegation_hint": None,
        }
        with patch("scripts.ppe_chapter_coordination.audit_repo", return_value=[]):
            with patch(
                "scripts.ppe_operator_blind_spots.assess_operator_blind_spots",
                return_value={"issues": []},
            ):
                payload = assess_coordination_check(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_RECOVERY)
        self.assertTrue(payload["blocks_burst"])
        self.assertTrue(any("ppe_branch_recovery" in c for c in payload["commands"]))

    def test_repair_when_marker_missing(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/x_relay.json",
            "branch_preflight": {"blocks_relay": False, "reasons": [], "commands": []},
            "preflight_warnings": [],
            "delegation_hint": None,
        }
        issues = [
            {
                "code": "PRODUCT_ON_MAIN_NO_MARKER",
                "severity": "high",
                "message": "marker missing",
                "fix": "python scripts/ppe_chapter_coordination.py --repair --plan x",
            }
        ]
        with patch("scripts.ppe_chapter_coordination.audit_repo", return_value=issues):
            with patch(
                "scripts.ppe_operator_blind_spots.assess_operator_blind_spots",
                return_value={"issues": []},
            ):
                payload = assess_coordination_check(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_REPAIR)
        self.assertFalse(payload["blocks_burst"])

    def test_park_on_frontier_ahead_of_evidence(self) -> None:
        status = {
            "verdict": "RUN_LOCAL",
            "branch_preflight": {"blocks_relay": False, "reasons": [], "commands": []},
            "preflight_warnings": [],
            "delegation_hint": None,
        }
        issues = [
            {
                "code": "FRONTIER_AHEAD_OF_EVIDENCE",
                "severity": "high",
                "message": "frontier claims complete",
                "fix": "align evidence doc honestly",
            }
        ]
        with patch("scripts.ppe_chapter_coordination.audit_repo", return_value=issues):
            with patch(
                "scripts.ppe_operator_blind_spots.assess_operator_blind_spots",
                return_value={"issues": []},
            ):
                payload = assess_coordination_check(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_PARK)
        self.assertTrue(payload["blocks_burst"])

    def test_write_artifact(self) -> None:
        status = {
            "verdict": "RUN_LOCAL",
            "branch_preflight": {"blocks_relay": False, "reasons": [], "commands": []},
            "preflight_warnings": [],
        }
        with patch("scripts.ppe_chapter_coordination.audit_repo", return_value=[]):
            with patch(
                "scripts.ppe_operator_blind_spots.assess_operator_blind_spots",
                return_value={"issues": []},
            ):
                payload = assess_coordination_check(self.repo, status)
        path = write_coordination_check(self.repo, payload)
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("verdict", data)


if __name__ == "__main__":
    unittest.main()
