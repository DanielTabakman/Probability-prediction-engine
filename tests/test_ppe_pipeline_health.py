"""Tests for founder pipeline diagnostics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_pipeline_health import (
    DEADLOCK_IDE_BUILD_CLOSEOUT,
    FIX_REPAIR,
    FIX_PROCEED,
    assess_pipeline_health,
    detect_contradictions,
    format_root_cause_block,
    maybe_notify_pipeline_regression,
    write_pipeline_health,
)


class TestPipelineHealth(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        (sop / "AGENT_STEERING_V1.json").write_text(
            json.dumps({"version": 1, "nextBuildCandidateId": "msos_trader_workflow_horizon_nav_v1"}),
            encoding="utf-8",
        )
        (sop / "ACTIVE_PRODUCT_DIRECTION.json").write_text(
            json.dumps({"version": 1, "asOf": "2026-06-30"}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_detect_deadlock_ide_build_closeout(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/x_relay.json",
            "chapter_mode": {"mode": "CLOSEOUT_ONLY", "do_not_rebuild": True},
        }
        coordination = {"chapter_issues": [], "commands": []}
        with patch(
            "scripts.ppe_chapter_mode.product_slices_on_main",
            return_value=["MSOS-X-Product-Slice002"],
        ):
            issues = detect_contradictions(self.repo, status, coordination)
        codes = [i["code"] for i in issues]
        self.assertIn(DEADLOCK_IDE_BUILD_CLOSEOUT, codes)

    def test_assess_pipeline_health_deadlock(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/x_relay.json",
            "chapter_mode": {"mode": "CLOSEOUT_ONLY", "do_not_rebuild": True},
            "branch_preflight": {"blocks_relay": False, "reasons": [], "commands": []},
        }
        with patch(
            "scripts.ppe_chapter_mode.product_slices_on_main",
            return_value=["MSOS-X-Product-Slice002"],
        ):
            with patch(
                "scripts.ppe_coordination_check.assess_coordination_check",
                return_value={
                    "verdict": "repair",
                    "summary": "marker missing",
                    "blocks_burst": False,
                    "blocks_build": False,
                    "chapter_issues": [
                        {
                            "code": "PRODUCT_ON_MAIN_NO_MARKER",
                            "message": "missing marker",
                            "fix": "python scripts/ppe_chapter_coordination.py --repair --plan x",
                        }
                    ],
                    "commands": ["python scripts/ppe_chapter_coordination.py --repair --plan x"],
                },
            ):
                with patch("scripts.ppe_coordination_check.write_coordination_check"):
                    with patch(
                        "scripts.ppe_chapter_coordination.audit_repo",
                        return_value=[],
                    ):
                        health = assess_pipeline_health(self.repo, status)
        self.assertFalse(health["ok"])
        self.assertEqual(health["root_cause_code"], DEADLOCK_IDE_BUILD_CLOSEOUT)
        self.assertEqual(health["fix_class"], FIX_REPAIR)
        self.assertTrue(health["commands"])

    def test_format_root_cause_block_ok(self) -> None:
        block = format_root_cause_block({"ok": True, "milestone": {"next_build_candidate": "horizon_nav"}})
        self.assertIn("pipeline OK", block)
        self.assertIn("horizon_nav", block)

    def test_format_root_cause_block_unhealthy(self) -> None:
        block = format_root_cause_block(
            {
                "ok": False,
                "root_cause_code": DEADLOCK_IDE_BUILD_CLOSEOUT,
                "root_cause_message": "bookkeeping deadlock",
                "fix_class": FIX_REPAIR,
                "milestone": {
                    "next_build_candidate": "horizon_nav",
                    "milestone_blocked_days": 1.2,
                },
                "commands": ["python scripts/ppe_chapter_coordination.py --repair"],
            }
        )
        self.assertIn("ROOT CAUSE", block)
        self.assertIn(DEADLOCK_IDE_BUILD_CLOSEOUT, block)
        self.assertIn("1.2", block)

    def test_write_pipeline_health(self) -> None:
        payload = {"ok": True, "fix_class": FIX_PROCEED, "as_of": "2026-07-01T00:00:00Z"}
        path = write_pipeline_health(self.repo, payload)
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(data["ok"])

    def test_regression_notify_on_ok_to_fail(self) -> None:
        health = {
            "ok": False,
            "fix_class": FIX_REPAIR,
            "root_cause_code": DEADLOCK_IDE_BUILD_CLOSEOUT,
            "root_cause_message": "deadlock",
            "commands": ["fix"],
            "milestone": {},
        }
        with patch(
            "scripts.ppe_pipeline_health._load_health_state",
            return_value={"ok": True, "root_cause_code": None},
        ):
            with patch(
                "scripts.ppe_notify_push.notify_enabled",
                return_value=True,
            ):
                with patch(
                    "scripts.ppe_notify_push.ntfy_configured",
                    return_value=True,
                ):
                    with patch(
                        "scripts.ppe_notify_push.send_ntfy",
                        return_value=True,
                    ) as send_ntfy:
                        sent = maybe_notify_pipeline_regression(self.repo, health)
        self.assertTrue(sent)
        send_ntfy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
