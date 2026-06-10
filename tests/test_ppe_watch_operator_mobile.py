"""Tests for mobile operator watch."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_watch_operator_mobile import ATTENTION_VERDICTS, watch_once


def test_watch_once_alerts_on_verdict_change(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")

    status_sequence = [
        {"verdict": "RUN_AUTO", "blocker": None, "commands": []},
        {"verdict": "IDE_BUILD", "blocker": "PRODUCT_BLOCKED", "commands": ["generate_ide_build_starter.cmd"]},
    ]

    with patch("scripts.ppe_watch_operator_mobile.collect_operator_status", side_effect=status_sequence):
        with patch("scripts.ppe_watch_operator_mobile.is_loop_running", return_value=True):
            with patch("scripts.ppe_watch_operator_mobile._heartbeat_due", return_value=False):
                with patch("scripts.ppe_watch_operator_mobile.send_ntfy", return_value=True) as send:
                    first = watch_once(tmp_path, write_report=False)
                    second = watch_once(tmp_path, write_report=False)

    assert first["alerts"] == []
    assert second["alerts_sent"] == 1
    send.assert_called_once()
    assert "IDE_BUILD" in send.call_args[0][0]


def test_attention_verdicts_include_run_local():
    assert "RUN_LOCAL" in ATTENTION_VERDICTS
