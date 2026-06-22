"""Tests for remote ntfy operator commands."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_ntfy_commands import (
    OUTBOUND_TAG,
    is_outbound_message,
    parse_command_text,
    should_ignore_message,
)


def test_parse_restart_command():
    assert parse_command_text("restart").name == "restart"
    assert parse_command_text("PPE restart").name == "restart"
    assert parse_command_text("/restart").name == "restart"


def test_parse_build_command():
    assert parse_command_text("build").name == "build"
    assert parse_command_text("build extra context").args == "extra context"


def test_parse_fix_with_note():
    cmd = parse_command_text("fix loop died after smoke")
    assert cmd is not None
    assert cmd.name == "fix"
    assert cmd.args == "loop died after smoke"


def test_parse_requires_secret_when_configured(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    assert parse_command_text("restart") is None
    assert parse_command_text("s3cret restart").name == "restart"
    assert parse_command_text("s3cret build").name == "build"


def test_ignore_outbound_messages():
    assert should_ignore_message({"event": "message", "message": "restart", "tags": [OUTBOUND_TAG]})
    assert not should_ignore_message({"event": "message", "message": "restart", "tags": ["phone"]})


def test_ignore_desktop_ok_title():
    assert should_ignore_message(
        {"event": "message", "title": "PPE OK - RUN_AUTO", "message": "Loop running."}
    )


def test_is_outbound_message_string_tags():
    assert is_outbound_message({"tags": "ppe,from-desktop,ok"})


def test_parse_maintenance_command():
    assert parse_command_text("maintenance on").name == "maintenance"
    assert parse_command_text("maintenance off").args == "off"
    assert parse_command_text("maintenance fixing viz").args == "fixing viz"


def test_execute_restart_calls_stack(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    with patch("scripts.ppe_ntfy_commands.stop_stack_processes", return_value=2):
        with patch("scripts.ppe_desktop_operator_stack.ensure_stack") as ensure:
            ensure.return_value = {"loop_running": True, "watch_running": True}
            from scripts.ppe_ntfy_commands import execute_restart

            result = execute_restart(tmp_path)
    assert result["killed"] == 2
    ensure.assert_called_once()
