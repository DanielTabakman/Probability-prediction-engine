"""Tests for uptime gap alerts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from scripts.ppe_operator_uptime_gap import maybe_send_gap_alert, save_state, state_path


def test_gap_alert_not_sent_when_loop_up(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_GAP_ALERT", "1")
    result = maybe_send_gap_alert(tmp_path, loop_running=True, verdict="RUN_AUTO", prior={})
    assert result["sent"] is False
    assert result["reason"] == "loop_up"


def test_gap_alert_fires_after_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_GAP_ALERT", "1")
    monkeypatch.setenv("PPE_NTFY_GAP_ALERT_MIN", "30")

    down_since = datetime.now(timezone.utc) - timedelta(minutes=50)
    save_state(
        tmp_path,
        {"loopDownSince": down_since.replace(microsecond=0).isoformat().replace("+00:00", "Z")},
    )

    with patch("scripts.ppe_operator_uptime_gap.notify_enabled", return_value=True):
        with patch("scripts.ppe_operator_uptime_gap.ntfy_configured", return_value=True):
            with patch("scripts.ppe_operator_uptime_gap.send_ntfy", return_value=True) as send:
                result = maybe_send_gap_alert(tmp_path, loop_running=False, verdict="RUN_AUTO", prior={})
    assert result["sent"] is True
    send.assert_called_once()
    title = send.call_args[0][0]
    assert "loop down" in title.lower()


def test_gap_alert_skipped_during_maintenance(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_GAP_ALERT", "1")
    monkeypatch.setenv("PPE_NTFY_GAP_ALERT_MIN", "15")
    from scripts.ppe_operator_maintenance import save_maintenance

    now = datetime.now(timezone.utc)
    save_maintenance(
        tmp_path,
        {
            "active": True,
            "since": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "reason": "desktop work",
            "setBy": "test",
        },
    )
    save_state(
        tmp_path,
        {"loopDownSince": (now - timedelta(minutes=60)).replace(microsecond=0).isoformat().replace("+00:00", "Z")},
    )
    with patch("scripts.ppe_operator_uptime_gap.send_ntfy", return_value=True) as send:
        result = maybe_send_gap_alert(tmp_path, loop_running=False, verdict="RUN_AUTO", prior={})
    assert result["sent"] is False
    assert result["reason"] == "maintenance"
    send.assert_not_called()
    assert state_path(tmp_path).is_file()
