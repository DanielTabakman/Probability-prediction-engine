"""Tests for enrich_operator_status_with_monitor."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_status import enrich_operator_status_with_monitor


def test_monitor_action_ready_sets_commands(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL", "vm_trust": {"wait_for_vm": True}}
    snapshot = {
        "phase": "HEALTHY_IDLE",
        "status": "action_ready",
        "done": True,
        "wait_for_vm": False,
        "completion_action": "DESKTOP_CONTINUE.cmd --no-pause",
        "message": "Phase cleared (`HEALTHY_IDLE`) — run DESKTOP_CONTINUE.cmd --no-pause.",
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(False, "desktop")):
        with patch("scripts.ppe_in_flight_monitor.collect_monitor_snapshot", return_value=snapshot):
            out = enrich_operator_status_with_monitor(tmp_path, status)

    assert out.get("action_ready") is True
    assert out.get("completion_action") == "DESKTOP_CONTINUE.cmd --no-pause"
    assert any("DESKTOP_CONTINUE" in cmd for cmd in out.get("commands") or [])
    assert out.get("vm_trust", {}).get("wait_for_vm") is False


def test_monitor_action_ready_respects_branch_block(tmp_path: Path) -> None:
    status = {
        "verdict": "RUN_LOCAL",
        "branch_preflight": {"blocks_relay": True},
    }
    snapshot = {
        "phase": "HEALTHY_IDLE",
        "status": "action_ready",
        "done": True,
        "completion_action": "DESKTOP_CONTINUE.cmd --no-pause",
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(False, "desktop")):
        with patch("scripts.ppe_in_flight_monitor.collect_monitor_snapshot", return_value=snapshot):
            out = enrich_operator_status_with_monitor(tmp_path, status)

    assert out.get("action_ready") is True
    assert not any("DESKTOP_CONTINUE" in str(c) for c in out.get("commands") or [])
    warnings = out.get("preflight_warnings") or []
    assert any("action_ready" in w for w in warnings)


def test_monitor_stale_recover_surfaces_productive_evidence(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL"}
    snapshot = {
        "phase": "BUILD_IN_FLIGHT",
        "status": "stale_recover",
        "done": False,
        "wait_for_vm": True,
        "stuck": True,
        "stale_recover": True,
        "productive_evidence": {
            "status": "waiting_for_evidence",
            "recent": False,
            "latest_path": None,
        },
        "message": "No recent productive evidence.",
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(False, "desktop")):
        with patch("scripts.ppe_in_flight_monitor.collect_monitor_snapshot", return_value=snapshot):
            out = enrich_operator_status_with_monitor(tmp_path, status)

    monitor = out.get("in_flight_monitor") or {}
    assert monitor.get("status") == "stale_recover"
    assert monitor.get("stale_recover") is True
    assert monitor.get("productive_evidence", {}).get("recent") is False


def test_monitor_skipped_on_loop_host(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL"}
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "loop")):
        out = enrich_operator_status_with_monitor(tmp_path, status)
    assert "in_flight_monitor" not in out
