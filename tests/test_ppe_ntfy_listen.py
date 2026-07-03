"""Tests for ntfy command listener."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_ntfy_listen import handle_message, listen_once, load_state, process_messages, save_state


def test_handle_message_restart(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    with patch("scripts.ppe_ntfy_commands.execute_restart") as restart:
        restart.return_value = {"action": "restart", "killed": 1, "stack": {}}
        with patch("scripts.ppe_ntfy_commands.notify_command_result", return_value=True):
            out = handle_message(
                tmp_path,
                {"event": "message", "id": "abc", "message": "s3cret restart"},
                notify=True,
            )
    assert out is not None
    assert out["command"] == "restart"
    restart.assert_called_once()


def test_listen_once_updates_state(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NTFY_TOPIC", "topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    save_state(tmp_path, {"last_message_id": "m0", "cmd_listener_initialized": True})
    messages = [{"event": "message", "id": "m1", "message": "s3cret status"}]
    with patch("scripts.ppe_ntfy_listen.poll_messages", return_value=messages):
        with patch("scripts.ppe_ntfy_commands.execute_status") as status:
            status.return_value = {"action": "status", "body": "ok", "notified": True}
            with patch("scripts.ppe_ntfy_commands.notify_command_result", return_value=True):
                result = listen_once(tmp_path, notify=False)
    assert result["handled"]
    state = load_state(tmp_path)
    assert state["last_message_id"] == "m1"


def test_listen_once_seeds_watermark_without_replaying_history(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    history = [
        {"event": "message", "id": "old-build", "message": "s3cret build"},
        {"event": "message", "id": "old-status", "message": "s3cret status"},
    ]
    with patch("scripts.ppe_ntfy_listen.poll_messages", return_value=history) as poll:
        with patch("scripts.ppe_ntfy_listen.handle_message") as handle:
            result = listen_once(tmp_path, notify=False)
    poll.assert_called_once_with(since="all")
    handle.assert_not_called()
    assert result.get("initialized") is True
    assert result["handled"] == []
    state = load_state(tmp_path)
    assert state["last_message_id"] == "old-status"
    assert state["cmd_listener_initialized"] is True


def test_state_roundtrip(tmp_path: Path):
    save_state(tmp_path, {"last_message_id": "x"})
    assert load_state(tmp_path)["last_message_id"] == "x"


def test_process_messages_acks_restart_before_handle(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    messages = [{"event": "message", "id": "restart-1", "message": "s3cret restart"}]
    with patch("scripts.ppe_ntfy_listen.handle_message") as handle:
        handle.return_value = {"command": "restart"}
        handled, state = process_messages(tmp_path, messages, state={}, notify=False)
    assert handled
    assert load_state(tmp_path)["last_message_id"] == "restart-1"
