"""Tests for operator dispatch and parked work."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_dispatch import dispatch_allowed, dispatch_direct_action
from scripts.ppe_parked_work import clear_parked_work, load_parked_work, write_parked_work


def test_dispatch_skipped_without_env(tmp_path: Path) -> None:
    assert not dispatch_allowed()
    report = dispatch_direct_action(tmp_path, "branch_recovery", force=False)
    assert report.get("skipped") is True


def test_dispatch_force_unknown_action(tmp_path: Path) -> None:
    report = dispatch_direct_action(tmp_path, "unknown_action", force=True)
    assert report.get("ok") is False


def test_maybe_auto_operate_starts_monitor(monkeypatch, tmp_path: Path) -> None:
    from scripts.ppe_operator_dispatch import maybe_auto_operate

    monkeypatch.setenv("PPE_AUTO_DISPATCH", "1")
    status = {"vm_trust": {"wait_for_vm": True, "vm_phase": "BUILD_IN_FLIGHT"}}
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(False, "desktop")):
        with patch(
            "scripts.ppe_in_flight_monitor.maybe_start_monitor_daemon",
            return_value={"started": True, "pid": 4242, "auto_act": True},
        ) as start:
            out = maybe_auto_operate(tmp_path, status)
    start.assert_called_once_with(tmp_path, auto_act=True)
    assert out.get("monitor_daemon", {}).get("pid") == 4242


def test_maybe_auto_operate_action_ready(monkeypatch, tmp_path: Path) -> None:
    from scripts.ppe_operator_dispatch import maybe_auto_operate

    monkeypatch.setenv("PPE_AUTO_DISPATCH", "1")
    status = {
        "action_ready": True,
        "completion_action": "DESKTOP_CONTINUE.cmd --no-pause",
        "branch_preflight": {"blocks_relay": False},
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(False, "desktop")):
        with patch(
            "scripts.ppe_operator_dispatch.dispatch_direct_action",
            return_value={"ok": True, "action": "DESKTOP_CONTINUE.cmd --no-pause"},
        ) as dispatch:
            out = maybe_auto_operate(tmp_path, status)
    dispatch.assert_called_once()
    assert out.get("auto_dispatch", {}).get("ok") is True


def test_parked_work_roundtrip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    path = write_parked_work(tmp_path, reason="mixed_plane", thread_role="charter")
    assert path.is_file()
    data = load_parked_work(tmp_path)
    assert data and data.get("reason") == "mixed_plane"
    assert clear_parked_work(tmp_path)
    assert load_parked_work(tmp_path) is None
