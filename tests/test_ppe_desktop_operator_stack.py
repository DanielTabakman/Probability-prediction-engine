"""Tests for desktop operator stack helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from scripts.ppe_desktop_operator_stack import (
    NTFY_LISTEN_PATTERN,
    LOOP_CMD_PATTERN,
    _powershell_process_match,
    ensure_stack,
    stack_status,
)


def test_powershell_process_match_excludes_probe_command():
    captured: list[str] = []

    def _run(cmd, **kwargs):
        captured.append(cmd[-1])
        return MagicMock(stdout="no", returncode=0)

    with patch("scripts.ppe_desktop_operator_stack.subprocess.run", side_effect=_run):
        assert _powershell_process_match(LOOP_CMD_PATTERN) is False

    assert captured
    script = captured[-1]
    assert "Get-CimInstance Win32_Process" in script
    assert LOOP_CMD_PATTERN.split("|")[0] in script
    assert "powershell.exe" in script


def test_ntfy_listen_pattern_requires_python_process():
    assert "watch_ntfy_commands" not in NTFY_LISTEN_PATTERN
    assert "ppe_ntfy_listen" in NTFY_LISTEN_PATTERN


def test_stack_status_all_running():
    with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=True):
        with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=True):
            with patch("scripts.ppe_desktop_operator_stack.is_ntfy_listen_running", return_value=False):
                status = stack_status()
    assert status["stack_running"] is True


def test_ensure_stack_starts_full_when_idle(tmp_path):
    with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=False):
        with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=False):
            with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=False):
                with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
                    with patch(
                        "scripts.ppe_desktop_operator_stack.stack_status",
                        side_effect=[
                            {"loop_running": False, "watch_running": False, "stack_running": False},
                            {"loop_running": True, "watch_running": True, "stack_running": True},
                        ],
                    ):
                        result = ensure_stack(tmp_path, start=True)
    start.assert_called_once_with(tmp_path)
    assert result["action"] == "stack"


def test_ensure_stack_noop_when_running(tmp_path):
    with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=False):
        with patch("scripts.ppe_desktop_operator_stack.stack_status") as status:
            status.return_value = {
                "loop_running": True,
                "watch_running": True,
                "ntfy_listen_running": False,
                "stack_running": True,
            }
            with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
                result = ensure_stack(tmp_path, start=True)
    start.assert_not_called()
    assert result["action"] == "none"


def test_ensure_stack_starts_ntfy_when_loop_watch_up(tmp_path):
    with patch("scripts.ppe_ntfy_commands.commands_enabled", return_value=True):
        with patch("scripts.ppe_desktop_operator_stack.start_ntfy_listen_only") as ntfy:
            with patch(
                "scripts.ppe_desktop_operator_stack.stack_status",
                side_effect=[
                    {
                        "loop_running": True,
                        "watch_running": True,
                        "ntfy_listen_running": False,
                        "stack_running": True,
                    },
                    {
                        "loop_running": True,
                        "watch_running": True,
                        "ntfy_listen_running": True,
                        "stack_running": True,
                    },
                ],
            ):
                result = ensure_stack(tmp_path, start=True)
    ntfy.assert_called_once_with(tmp_path)
    assert result["action"] == "ntfy_listen"
