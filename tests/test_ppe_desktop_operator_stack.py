"""Tests for desktop operator stack helpers."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_desktop_operator_stack import ensure_stack, stack_status


def test_stack_status_all_running():
    with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=True):
        with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=True):
            with patch("scripts.ppe_desktop_operator_stack.is_ntfy_listen_running", return_value=False):
                with patch(
                    "scripts.ppe_desktop_operator_stack.is_local_trigger_watcher_running",
                    return_value=True,
                ):
                    with patch(
                        "scripts.ppe_desktop_operator_stack.local_trigger_watcher_desired",
                        return_value=True,
                    ):
                        status = stack_status()
    assert status["stack_running"] is True


def test_ensure_stack_starts_full_when_idle(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.headless_stack_mode", return_value=False):
        with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=False):
            with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=False):
                with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=False):
                    with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
                        with patch(
                            "scripts.ppe_desktop_operator_stack.stack_status",
                            side_effect=[
                                {
                                    "loop_running": False,
                                    "watch_running": False,
                                    "local_trigger_watcher_running": False,
                                    "local_trigger_watcher_desired": False,
                                    "stack_running": False,
                                },
                                {
                                    "loop_running": True,
                                    "watch_running": True,
                                    "local_trigger_watcher_running": False,
                                    "local_trigger_watcher_desired": False,
                                    "stack_running": True,
                                },
                            ],
                        ):
                            result = ensure_stack(tmp_path, start=True)
    start.assert_called_once_with(tmp_path)
    assert result["action"] == "stack"


def test_ensure_stack_noop_when_running(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.headless_stack_mode", return_value=False):
        with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=False):
            with patch("scripts.ppe_desktop_operator_stack.stack_status") as status:
                status.return_value = {
                    "loop_running": True,
                    "watch_running": True,
                    "ntfy_listen_running": False,
                    "local_trigger_watcher_running": True,
                    "local_trigger_watcher_desired": True,
                    "stack_running": True,
                }
                with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
                    result = ensure_stack(tmp_path, start=True)
    start.assert_not_called()
    assert result["action"] == "none"


def test_ensure_stack_starts_ntfy_when_loop_watch_up(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.headless_stack_mode", return_value=False):
        with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=True):
            with patch("scripts.ppe_loop_host_guard.loop_host_blocked", return_value=None):
                with patch("scripts.ppe_desktop_operator_stack.start_ntfy_listen_only") as ntfy:
                    with patch(
                        "scripts.ppe_desktop_operator_stack.stack_status",
                        side_effect=[
                            {
                                "loop_running": True,
                                "watch_running": True,
                                "ntfy_listen_running": False,
                                "local_trigger_watcher_running": True,
                                "local_trigger_watcher_desired": True,
                                "stack_running": True,
                            },
                            {
                                "loop_running": True,
                                "watch_running": True,
                                "ntfy_listen_running": True,
                                "local_trigger_watcher_running": True,
                                "local_trigger_watcher_desired": True,
                                "stack_running": True,
                            },
                        ],
                    ):
                        result = ensure_stack(tmp_path, start=True)
    ntfy.assert_called_once_with(tmp_path)
    assert result["action"] == "ntfy_listen"


def test_ensure_stack_skips_ntfy_on_daily_driver(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.headless_stack_mode", return_value=False):
        with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=True):
            with patch(
                "scripts.ppe_loop_host_guard.loop_host_blocked",
                return_value={"guard_code": "stack_forbidden", "guard_detail": "daily PC"},
            ):
                with patch("scripts.ppe_desktop_operator_stack.start_ntfy_listen_only") as ntfy:
                    with patch(
                        "scripts.ppe_desktop_operator_stack.stack_status",
                        return_value={
                            "loop_running": True,
                            "watch_running": True,
                            "ntfy_listen_running": False,
                            "local_trigger_watcher_running": True,
                            "local_trigger_watcher_desired": True,
                            "stack_running": True,
                        },
                    ):
                        result = ensure_stack(tmp_path, start=True)
    ntfy.assert_not_called()
    assert result["action"] == "none"
