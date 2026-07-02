"""Tests for factory throughput diagnostics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_factory_throughput import (
    VERDICT_IDLE_OK,
    VERDICT_MOVING,
    VERDICT_STACK_DOWN,
    VERDICT_STUCK,
    assess_factory_throughput,
    assess_supply_health,
    collect_chapter_throughput,
    detect_phase_stuck,
    forecast_supply_days,
    format_throughput_lines,
    maybe_auto_advance_stuck,
    write_factory_throughput,
)


class TestFactoryThroughput(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_stack_down_verdict(self) -> None:
        status = {"verdict": "RUN_LOCAL", "supply": {"backlog": {}, "queue_ready": 5}}
        with patch(
            "scripts.ppe_factory_throughput._stack_snapshot",
            return_value={
                "phase": "STACK_DOWN",
                "loop_running": False,
                "watch_running": False,
                "unknown": False,
            },
        ):
            with patch(
                "scripts.ppe_factory_throughput._throughput_counts",
                return_value={"slices": 0, "closeouts": 0, "weighted_slices": 0, "weighted_slices_per_closeout": 0},
            ):
                with patch("scripts.ppe_factory_throughput._last_slice_completed", return_value=None):
                    with patch(
                        "scripts.ppe_factory_throughput.collect_chapter_throughput",
                        return_value={"pending_count": 0},
                    ):
                        payload = assess_factory_throughput(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_STACK_DOWN)
        self.assertFalse(payload["ok"])

    def test_moving_verdict(self) -> None:
        status = {"verdict": "RUN_LOCAL", "supply": {"backlog": {}, "queue_ready": 5}}
        with patch(
            "scripts.ppe_factory_throughput._stack_snapshot",
            return_value={
                "phase": "RUN_LOCAL_PENDING",
                "loop_running": True,
                "watch_running": True,
                "unknown": False,
            },
        ):
            with patch(
                "scripts.ppe_factory_throughput._throughput_counts",
                return_value={"slices": 2, "closeouts": 1, "weighted_slices": 3, "weighted_slices_per_closeout": 1.5},
            ):
                with patch(
                    "scripts.ppe_factory_throughput._last_slice_completed",
                    return_value={"slice_id": "X", "hours_ago": 1.0},
                ):
                    with patch("scripts.ppe_factory_throughput.detect_phase_stuck", return_value=None):
                        with patch(
                            "scripts.ppe_factory_throughput.collect_chapter_throughput",
                            return_value={"pending_count": 1, "chapter_id": "ch1"},
                        ):
                            payload = assess_factory_throughput(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_MOVING)
        self.assertTrue(payload["ok"])

    def test_forecast_supply_days(self) -> None:
        supply = {"queue_ready": 10, "backlog_queued": 5, "backlog_blocked": 0, "idle_risk": False}
        t7 = {"slices": 14, "closeouts": 2}
        fc = forecast_supply_days(supply, t7)
        self.assertEqual(fc["days_until_supply_low"], 7.5)
        self.assertFalse(fc["at_risk"])

    def test_forecast_at_risk_low_burn(self) -> None:
        supply = {"queue_ready": 2, "backlog_queued": 0, "backlog_blocked": 0, "idle_risk": False}
        fc = forecast_supply_days(supply, {"slices": 0})
        self.assertTrue(fc["at_risk"])

    def test_format_throughput_lines_extended(self) -> None:
        lines = format_throughput_lines(
            {
                "verdict": "stuck",
                "phase": "RUN_LOCAL_PENDING",
                "phase_minutes": 120,
                "phase_age_trusted": False,
                "throughput_24h": {"slices": 0, "closeouts": 0},
                "weighted_sla": {"weighted_slices_per_closeout_7d": 2.5},
                "chapter": {"chapter_id": "msos_foo_v1", "pending_count": 3, "stall_hours": 30.0},
                "supply": {"queue_ready": 5, "backlog_queued": 1, "backlog_blocked": 0},
                "supply_forecast": {"days_until_supply_low": 4.0},
                "top_issue_message": "stuck issue",
            }
        )
        text = "\n".join(lines)
        self.assertIn("CHAPTER", text)
        self.assertIn("wspc7d", text)
        self.assertIn("~mirror", text)
        self.assertIn("4.0d supply", text)

    def test_auto_advance_skips_desktop(self) -> None:
        throughput = {"verdict": VERDICT_STUCK, "phase_minutes": 60}
        with patch(
            "scripts.ppe_loop_host_guard.loop_host_start_allowed",
            return_value=(False, "not_loop_host", ""),
        ):
            result = maybe_auto_advance_stuck(self.repo, throughput)
        self.assertFalse(result.get("attempted"))
        self.assertEqual(result.get("reason"), "not_loop_host")

    def test_auto_advance_on_loop_host(self) -> None:
        throughput = {"verdict": VERDICT_STACK_DOWN, "phase_minutes": 60}
        with patch(
            "scripts.ppe_loop_host_guard.loop_host_start_allowed",
            return_value=(True, "loop_host", ""),
        ):
            with patch(
                "scripts.ppe_autobuilder.action_advance",
                return_value={"action": "ensure", "phase": "HEALTHY_IDLE", "skipped": False},
            ):
                result = maybe_auto_advance_stuck(self.repo, throughput)
        self.assertTrue(result.get("attempted"))

    def test_phase_stuck_detection(self) -> None:
        with patch(
            "scripts.ppe_factory_throughput._phase_age_with_trust",
            return_value=(150.0, True, None),
        ):
            issue = detect_phase_stuck(self.repo, "BUILD_IN_FLIGHT")
        self.assertIsNotNone(issue)
        assert issue is not None
        self.assertEqual(issue["code"], "PHASE_STUCK")

    def test_write_factory_throughput(self) -> None:
        path = write_factory_throughput(
            self.repo,
            {"verdict": VERDICT_STUCK, "ok": False, "as_of": "2026-07-01T00:00:00Z"},
        )
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
