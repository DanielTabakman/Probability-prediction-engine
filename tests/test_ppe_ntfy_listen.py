"""Tests for ntfy command listener."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_ntfy_listen import handle_message, listen_once, load_state, process_messages, save_state


def test_handle_message_restart(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    with patch("scripts.ppe_ntfy_commands.execute_restart") as restart:
        restart.return_value = {"action": "restart", "killed": 1, "stack": {}}
        with patch("scripts.ppe_ntfy_commands.notify_command_result", return_value=True):
            out = handle_message(
                tmp_path,
                {"event": "message", "id": "abc", "message": "restart"},
                notify=True,
            )
    assert out is not None
    assert out["command"] == "restart"
    restart.assert_called_once()


def test_listen_once_updates_state(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NTFY_TOPIC", "topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.delenv("PPE_NTFY_CMD_SECRET", raising=False)
    messages = [{"event": "message", "id": "m1", "message": "status"}]
    with patch("scripts.ppe_ntfy_listen.poll_messages", return_value=messages):
        with patch("scripts.ppe_ntfy_commands.execute_status") as status:
            status.return_value = {"action": "status", "body": "ok", "notified": True}
            with patch("scripts.ppe_ntfy_commands.notify_command_result", return_value=True):
                result = listen_once(tmp_path, notify=False)
    assert result["handled"]
    state = load_state(tmp_path)
    assert state["last_message_id"] == "m1"


def test_state_roundtrip(tmp_path: Path):
    save_state(tmp_path, {"last_message_id": "x"})
    assert load_state(tmp_path)["last_message_id"] == "x"


def test_process_messages_acks_restart_before_handle(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    messages = [{"event": "message", "id": "restart-1", "message": "restart"}]
    with patch("scripts.ppe_ntfy_listen.handle_message") as handle:
        handle.return_value = {"command": "restart"}
        handled, state = process_messages(tmp_path, messages, state={}, notify=False)
    assert handled
    assert load_state(tmp_path)["last_message_id"] == "restart-1"
