"""Tests for founder pipeline diagnostics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_pipeline_health import (
    ACTIVE_CHAPTER_GATE,
    DEADLOCK_IDE_BUILD_CLOSEOUT,
    FIX_REPAIR,
    FIX_PROCEED,
    STEERING_CANDIDATE_STALE,
    assess_pipeline_health,
    compute_milestone_clock,
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
                        with patch(
                            "scripts.ppe_factory_throughput.assess_factory_throughput",
                            return_value={
                                "ok": True,
                                "verdict": "moving",
                                "issues": [],
                                "commands": [],
                            },
                        ):
                            with patch("scripts.ppe_factory_throughput.write_factory_throughput"):
                                health = assess_pipeline_health(self.repo, status)
        self.assertFalse(health["ok"])
        self.assertEqual(health["root_cause_code"], DEADLOCK_IDE_BUILD_CLOSEOUT)
        self.assertEqual(health["fix_class"], FIX_REPAIR)
        self.assertTrue(health["commands"])

    def test_format_root_cause_block_ok(self) -> None:
        block = format_root_cause_block({"ok": True, "milestone": {"next_build_candidate": "horizon_nav"}})
        self.assertIn("factory OK", block)
        self.assertIn("horizon_nav", block)

    def test_format_root_cause_block_unhealthy(self) -> None:
        block = format_root_cause_block(
            {
                "ok": False,
                "root_cause_code": ACTIVE_CHAPTER_GATE,
                "root_cause_message": "active chapter pending",
                "fix_class": FIX_REPAIR,
                "milestone": {
                    "next_build_candidate": "msos_cross_venue_strategy_lab_v1",
                    "next_build_resolved": "msos_cross_venue_strategy_lab_v1",
                    "next_build_steering": "msos_trader_workflow_horizon_nav_v1",
                    "steering_stale": True,
                    "active_chapter_id": "msos_storyboard_visual_parity_v1",
                    "active_pending_count": 2,
                    "registry_total": 19,
                    "registry_stale": 17,
                    "registry_actionable": 1,
                },
                "commands": ["DESKTOP_CONTINUE.cmd --no-pause"],
            }
        )
        self.assertIn("ROOT CAUSE", block)
        self.assertIn(ACTIVE_CHAPTER_GATE, block)
        self.assertIn("storyboard_visual_parity", block)
        self.assertIn("Steering drift", block)

    def test_compute_milestone_clock_no_blocked_days_when_only_stale_registry(self) -> None:
        with patch(
            "scripts.ppe_pipeline_health.assess_closeout_debt",
            return_value={
                "has_active_gate": False,
                "active_pending_count": 0,
                "next_build_steering": "horizon_nav",
                "next_build_resolved": "cross_venue",
                "steering_stale": True,
                "registry_stale": 10,
            },
        ):
            clock = compute_milestone_clock(self.repo)
        self.assertIsNone(clock.get("milestone_blocked_days"))
        self.assertEqual(clock.get("next_build_resolved"), "cross_venue")

    def test_detect_steering_stale_issue(self) -> None:
        with patch(
            "scripts.ppe_pipeline_health.assess_closeout_debt",
            return_value={
                "active_chapter_id": None,
                "active_pending_count": 0,
                "active_pending_slices": [],
                "has_active_gate": False,
                "registry_total": 5,
                "registry_stale": 3,
                "registry_actionable": 0,
                "next_build_steering": "horizon_nav",
                "next_build_resolved": "cross_venue",
                "steering_stale": True,
            },
        ):
            issues = detect_contradictions(self.repo, {"verdict": "RUN_LOCAL"}, {"chapter_issues": []})
        codes = [i["code"] for i in issues]
        self.assertIn(STEERING_CANDIDATE_STALE, codes)

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
