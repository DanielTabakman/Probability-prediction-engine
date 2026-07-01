"""Tests for stuck RUN_LOCAL auto-recovery."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_stuck_run_local import (
    assess_stuck_run_local,
    ensure_stuck_watch_daemon,
    maybe_auto_recover_run_local,
    stuck_automation_enabled,
    stuck_watch_enabled,
)


def test_assess_not_stuck_when_run_local_lock_active(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL", "operator_session": {"elapsed_seconds": 900}}
    with patch(
        "scripts.ppe_remote_build_agent._run_local_lock_active",
        return_value=True,
    ):
        with patch(
            "scripts.ppe_remote_build_agent._read_run_local_lock",
            return_value={"worker_pid": 123},
        ):
            out = assess_stuck_run_local(tmp_path, status)
    assert out["stuck"] is False


def test_assess_stuck_when_no_worker_and_elapsed(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL", "operator_session": {"elapsed_seconds": 300}}
    with patch(
        "scripts.ppe_remote_build_agent._run_local_lock_active",
        return_value=False,
    ):
        with patch(
            "scripts.ppe_remote_build_agent._read_run_local_lock",
            return_value=None,
        ):
            out = assess_stuck_run_local(tmp_path, status, stuck_seconds=180)
    assert out["stuck"] is True


def test_auto_recover_skips_when_not_stuck(tmp_path: Path) -> None:
    status = {"verdict": "IDE_BUILD", "operator_session": {"elapsed_seconds": 9999}}
    out = maybe_auto_recover_run_local(tmp_path, status=status, source="test")
    assert out is None


def test_auto_recover_loop_host_calls_run_local(tmp_path: Path) -> None:
    status = {"verdict": "RUN_LOCAL", "operator_session": {"elapsed_seconds": 400}}
    with patch("scripts.ppe_operator_stuck_run_local._is_loop_host", return_value=True):
        with patch(
            "scripts.ppe_remote_build_agent._run_local_lock_active",
            return_value=False,
        ):
            with patch(
                "scripts.ppe_remote_build_agent._read_run_local_lock",
                return_value=None,
            ):
                with patch(
                    "scripts.ppe_autobuilder.action_run_local",
                    return_value={"started": True, "worker_pid": 42},
                ):
                    out = maybe_auto_recover_run_local(tmp_path, status=status, source="test")
    assert out is not None
    assert out.get("recovered") is True


def test_auto_recover_desktop_disabled_by_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("PPE_ENABLE_STUCK_RUN_LOCAL_RECOVERY", raising=False)
    monkeypatch.delenv("PPE_STUCK_RUN_LOCAL_WATCH", raising=False)
    monkeypatch.delenv("PPE_DISABLE_STUCK_RUN_LOCAL_RECOVERY", raising=False)
    status = {"verdict": "RUN_LOCAL", "operator_session": {"elapsed_seconds": 400}}
    with patch("scripts.ppe_operator_stuck_run_local._is_loop_host", return_value=False):
        out = maybe_auto_recover_run_local(tmp_path, status=status, source="test")
        assert out is None
        assert stuck_automation_enabled(tmp_path) is False


def test_auto_recover_desktop_opt_in(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_ENABLE_STUCK_RUN_LOCAL_RECOVERY", "1")
    status = {"verdict": "RUN_LOCAL", "operator_session": {"elapsed_seconds": 400}}
    with patch("scripts.ppe_operator_stuck_run_local._is_loop_host", return_value=False):
        with patch(
            "scripts.ppe_remote_build_agent._run_local_lock_active",
            return_value=False,
        ):
            with patch(
                "scripts.ppe_remote_build_agent._read_run_local_lock",
                return_value=None,
            ):
                with patch(
                    "scripts.ppe_operator_stuck_run_local._recover_on_desktop",
                    return_value={"action": "desktop_ssh_recover", "recovered": True, "step": "handoff"},
                ):
                    out = maybe_auto_recover_run_local(tmp_path, status=status, source="test")
    assert out is not None
    assert out.get("recovered") is True


def test_ensure_watch_skipped_without_opt_in(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("PPE_STUCK_RUN_LOCAL_WATCH", raising=False)
    with patch("scripts.ppe_operator_stuck_run_local._is_loop_host", return_value=False):
        out = ensure_stuck_watch_daemon(tmp_path)
    assert out.get("skipped") is True
    assert out.get("reason") == "not_enabled"
    assert stuck_watch_enabled() is False


def test_ensure_watch_explicit_opt_in(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("PPE_STUCK_RUN_LOCAL_WATCH", raising=False)
    monkeypatch.setenv("PPE_DISABLE_STUCK_RUN_LOCAL_RECOVERY", "1")
    with patch("scripts.ppe_operator_stuck_run_local._is_loop_host", return_value=False):
        with patch("scripts.ppe_remote_agent_spawn.spawn_python_worker") as spawn:
            spawn.return_value = type("P", (), {"pid": 9999})()
            out = ensure_stuck_watch_daemon(tmp_path, explicit=True)
    assert out.get("started") is True
    spawn.assert_called_once()


def test_vm_handoff_preflight_legacy_ok(tmp_path: Path) -> None:
    from scripts.ppe_vm_handoff_preflight import _legacy_prepare

    def fake_git(_repo: Path, *args: str):
        if args[:2] == ("fetch", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("rev-parse", "--abbrev-ref"):
            return type("P", (), {"returncode": 0, "stdout": "main\n", "stderr": ""})()
        if args[:2] == ("pull", "--ff-only"):
            return type("P", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()
        if args[:3] == ("checkout", "origin/main", "--"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_vm_handoff_preflight._git", side_effect=fake_git):
        out = _legacy_prepare(tmp_path)
    assert out.get("ok") is True
