"""Tests for idle-with-loop-up alerts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from scripts.ppe_operator_idle_alert import load_state, maybe_send_idle_alert, save_state


def test_idle_alert_below_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_IDLE_ALERT", "1")
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    now = datetime.now(timezone.utc)
    save_state(
        tmp_path,
        {"idleSince": (now - timedelta(minutes=5)).replace(microsecond=0).isoformat().replace("+00:00", "Z")},
    )
    with patch("scripts.ppe_operator_idle_alert.notify_enabled", return_value=True):
        with patch("scripts.ppe_operator_idle_alert.ntfy_configured", return_value=True):
            with patch("scripts.ppe_operator_idle_alert.send_ntfy", return_value=True) as send:
                result = maybe_send_idle_alert(
                    tmp_path,
                    loop_running=True,
                    verdict="RUN_LOCAL",
                    status={"blocker": "IDE product marker present"},
                )
    assert result.get("sent") is False
    send.assert_not_called()


def test_idle_alert_fires_after_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_IDLE_ALERT", "1")
    monkeypatch.setenv("PPE_NTFY_IDLE_ALERT_MIN", "10")
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    now = datetime.now(timezone.utc)
    save_state(
        tmp_path,
        {"idleSince": (now - timedelta(minutes=25)).replace(microsecond=0).isoformat().replace("+00:00", "Z")},
    )
    with patch("scripts.ppe_operator_idle_alert.notify_enabled", return_value=True):
        with patch("scripts.ppe_operator_idle_alert.ntfy_configured", return_value=True):
            with patch("scripts.ppe_operator_idle_alert._worker_in_flight", return_value=False):
                with patch("scripts.ppe_operator_idle_alert.send_ntfy", return_value=True) as send:
                    result = maybe_send_idle_alert(
                        tmp_path,
                        loop_running=True,
                        verdict="RUN_LOCAL",
                        status={"blocker": "IDE product marker present"},
                    )
    assert result.get("sent") is True
    assert "idle" in send.call_args[0][0].lower()
    assert load_state(tmp_path).get("lastIdleAlertAt")
