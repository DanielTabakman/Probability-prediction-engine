"""Phone commands must always get an ntfy reply, including debounced handoff."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_ntfy_commands import RemoteCommand, notify_command_result


def test_notify_debounced_build_still_replies(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    cmd = RemoteCommand(name="build", args="")
    result = {
        "action": "ide_handoff",
        "started": False,
        "debounced": True,
        "reason": "handoff already done recently for MVP1-Slice002",
        "slice_id": "MVP1-Slice002",
    }
    with patch("scripts.ppe_ntfy_commands.notify_enabled", return_value=True):
        with patch("scripts.ppe_ntfy_commands.ntfy_configured", return_value=True):
            with patch("scripts.ppe_ntfy_commands.send_ntfy", return_value=True) as send:
                ok = notify_command_result(cmd, result, tmp_path)
    assert ok is True
    assert "already sent" in send.call_args[0][0].lower()
    assert "build force" in send.call_args[0][1].lower()
