"""Tests for headless desktop operator stack supervisor."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ppe_headless_stack_supervisor import (
    clear_state,
    ensure_headless_supervisor,
    is_supervisor_running,
    load_state,
    save_state,
    worker_specs,
)
from scripts.ppe_operator_config import headless_stack_mode


def test_headless_stack_mode_from_config(tmp_path):
    cfg = tmp_path / "docs/SOP/PPE_AUTO_OPERATOR.local.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(
        json.dumps({"desktopStack": {"mode": "headless"}}),
        encoding="utf-8",
    )
    with patch.dict("os.environ", {"PPE_OPERATOR_PROFILE": "local"}, clear=False):
        assert headless_stack_mode(tmp_path) is True


def test_headless_stack_mode_env_override(tmp_path):
    with patch.dict("os.environ", {"PPE_STACK_HEADLESS": "0"}, clear=False):
        assert headless_stack_mode(tmp_path) is False


def test_supervisor_running_uses_state_pid(tmp_path):
    save_state(tmp_path, {"supervisor_pid": 4242})
    with patch("scripts.ppe_headless_stack_supervisor.process_alive", return_value=True):
        assert is_supervisor_running(tmp_path) is True


def test_worker_specs_respects_ntfy_and_local_watcher(tmp_path):
    with patch("scripts.ppe_headless_stack_supervisor.commands_enabled", return_value=False):
        with patch(
            "scripts.ppe_headless_stack_supervisor.local_trigger_watcher_desired",
            return_value=False,
        ):
            names = [spec.name for spec in worker_specs(tmp_path)]
    assert names == ["loop", "watch"]


def test_ensure_headless_supervisor_noop_when_running(tmp_path):
    with patch("scripts.ppe_headless_stack_supervisor.is_supervisor_running", return_value=True):
        with patch(
            "scripts.ppe_headless_stack_supervisor.stack_status",
            return_value={"stack_running": True, "loop_running": True, "watch_running": True},
        ):
            result = ensure_headless_supervisor(tmp_path, detach=True, start=True)
    assert result["action"] == "none"
    assert result["supervisor_running"] is True


def test_ensure_headless_supervisor_starts_detached(tmp_path):
    clear_state(tmp_path)
    fake_proc = MagicMock()
    fake_proc.pid = 9999
    with patch("scripts.ppe_headless_stack_supervisor.is_supervisor_running", side_effect=[False, True]):
        with patch(
            "scripts.ppe_headless_stack_supervisor.spawn_detached_logged",
            return_value=fake_proc,
        ) as spawn:
            with patch(
                "scripts.ppe_headless_stack_supervisor.stack_status",
                return_value={"stack_running": False, "loop_running": False, "watch_running": False},
            ):
                result = ensure_headless_supervisor(tmp_path, detach=True, start=True)
    spawn.assert_called_once()
    assert result["action"] == "headless_supervisor"
    assert result["supervisor_running"] is True


def test_start_full_stack_uses_headless(tmp_path):
    from scripts.ppe_desktop_operator_stack import start_full_stack

    with patch("scripts.ppe_desktop_operator_stack.headless_stack_mode", return_value=True):
        with patch("scripts.ppe_desktop_operator_stack._ensure_headless") as ensure:
            start_full_stack(tmp_path)
    ensure.assert_called_once_with(tmp_path)


def test_load_state_missing_returns_empty(tmp_path):
    assert load_state(tmp_path) == {}
