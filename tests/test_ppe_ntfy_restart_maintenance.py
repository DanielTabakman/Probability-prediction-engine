"""Restart notify includes maintenance reminder."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_ntfy_commands import RemoteCommand, notify_command_result


def test_restart_notify_maintenance_nudge(tmp_path):
    from scripts.ppe_operator_maintenance import save_maintenance

    now = datetime.now(timezone.utc)
    save_maintenance(
        tmp_path,
        {
            "active": True,
            "since": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "reason": "desktop IDE",
            "setBy": "test",
        },
    )
    cmd = RemoteCommand(name="restart", args="")
    result = {
        "action": "restart",
        "killed": 1,
        "stack": {"loop_running": True, "watch_running": True},
    }
    with patch("scripts.ppe_ntfy_commands.notify_enabled", return_value=True):
        with patch("scripts.ppe_ntfy_commands.ntfy_configured", return_value=True):
            with patch("scripts.ppe_ntfy_commands.send_ntfy", return_value=True) as send:
                notify_command_result(cmd, result, tmp_path)
    body = send.call_args[0][1]
    assert "Maintenance still ON" in body
