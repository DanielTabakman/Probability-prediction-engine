"""Tests for factory throughput diagnostics."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_factory_throughput import (
    VERDICT_IDLE_OK,
    VERDICT_MOVING,
    VERDICT_STACK_DOWN,
    VERDICT_STUCK,
    assess_factory_throughput,
    assess_supply_health,
    detect_phase_stuck,
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
            },
        ):
            with patch(
                "scripts.ppe_factory_throughput._throughput_counts",
                return_value={"slices": 0, "closeouts": 0, "weighted_slices": 0},
            ):
                with patch("scripts.ppe_factory_throughput._last_slice_completed", return_value=None):
                    payload = assess_factory_throughput(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_STACK_DOWN)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(i.get("code") == "STACK_DOWN" for i in payload["issues"]))

    def test_moving_verdict(self) -> None:
        status = {"verdict": "RUN_LOCAL", "supply": {"backlog": {}, "queue_ready": 5}}
        with patch(
            "scripts.ppe_factory_throughput._stack_snapshot",
            return_value={
                "phase": "RUN_LOCAL_PENDING",
                "loop_running": True,
                "watch_running": True,
            },
        ):
            with patch(
                "scripts.ppe_factory_throughput._throughput_counts",
                return_value={"slices": 2, "closeouts": 1, "weighted_slices": 2},
            ):
                with patch(
                    "scripts.ppe_factory_throughput._last_slice_completed",
                    return_value={"slice_id": "X", "hours_ago": 1.0},
                ):
                    with patch("scripts.ppe_factory_throughput.detect_phase_stuck", return_value=None):
                        payload = assess_factory_throughput(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_MOVING)
        self.assertTrue(payload["ok"])

    def test_idle_ok_on_supply_low(self) -> None:
        status = {
            "verdict": "SUPPLY_LOW",
            "supply": {"backlog": {"queued": 0}, "queue_ready": 0, "idle_risk": True},
        }
        with patch(
            "scripts.ppe_factory_throughput._stack_snapshot",
            return_value={"phase": "HEALTHY_IDLE", "loop_running": True, "watch_running": True},
        ):
            with patch(
                "scripts.ppe_factory_throughput._throughput_counts",
                return_value={"slices": 0, "closeouts": 0, "weighted_slices": 0},
            ):
                with patch("scripts.ppe_factory_throughput._last_slice_completed", return_value=None):
                    with patch("scripts.ppe_factory_throughput.detect_phase_stuck", return_value=None):
                        payload = assess_factory_throughput(self.repo, status)
        self.assertEqual(payload["verdict"], VERDICT_IDLE_OK)

    def test_phase_stuck_detection(self) -> None:
        with patch(
            "scripts.ppe_factory_throughput._phase_age_minutes",
            return_value=150.0,
        ):
            issue = detect_phase_stuck(self.repo, "BUILD_IN_FLIGHT")
        self.assertIsNotNone(issue)
        assert issue is not None
        self.assertEqual(issue["code"], "PHASE_STUCK")

    def test_supply_health(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "supply": {
                "backlog": {"queued": 1, "blocked": 2},
                "queue_ready": 3,
            },
        }
        supply = assess_supply_health(self.repo, status)
        self.assertEqual(supply["queue_ready"], 3)
        self.assertEqual(supply["backlog_blocked"], 2)

    def test_write_factory_throughput(self) -> None:
        path = write_factory_throughput(
            self.repo,
            {"verdict": VERDICT_STUCK, "ok": False, "as_of": "2026-07-01T00:00:00Z"},
        )
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["verdict"], VERDICT_STUCK)


if __name__ == "__main__":
    unittest.main()
