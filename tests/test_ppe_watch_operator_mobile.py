"""Tests for mobile operator watch."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_watch_operator_mobile import ATTENTION_VERDICTS, _auto_build_retry_due, watch_once


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


def test_watch_module_imports_verdict_run_auto():
    from scripts.ppe_watch_operator_mobile import HEALTHY_VERDICTS

    assert "RUN_AUTO" in HEALTHY_VERDICTS


def test_watch_once_auto_build_on_ide_build(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_AUTO_REMOTE_BUILD", "1")

    status = {
        "verdict": "IDE_BUILD",
        "blocker": "PRODUCT_BLOCKED [MVP1-Slice002]",
        "guard": {"detail": "product [MVP1-Slice002, MVP1-Slice003]"},
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "commands": [],
    }

    with patch("scripts.ppe_watch_operator_mobile.collect_operator_status", return_value=status):
        with patch("scripts.ppe_watch_operator_mobile.is_loop_running", return_value=True):
            with patch("scripts.ppe_watch_operator_mobile._heartbeat_due", return_value=False):
                with patch("scripts.ppe_watch_operator_mobile._maybe_auto_remote_build") as auto_build:
                    auto_build.return_value = {
                        "started": True,
                        "slice_id": "MVP1-Slice002",
                        "action": "build",
                    }
                    with patch("scripts.ppe_watch_operator_mobile.send_ntfy", return_value=True) as send:
                        result = watch_once(tmp_path, write_report=False)

    assert result["auto_build"]["started"] is True
    auto_build.assert_called_once()
    assert "auto-build started" in send.call_args[0][0].lower()


def test_auto_build_retry_when_never_started():
    prior = {
        "last_verdict": "IDE_BUILD",
        "last_verdict_slice": "MVP1-Slice002",
        "last_stuck_alert_at": None,
    }
    assert _auto_build_retry_due(prior, "IDE_BUILD") is True


def test_watch_once_alerts_when_stuck_clears(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")

    status_sequence = [
        {
            "verdict": "IDE_BUILD",
            "blocker": "PRODUCT_BLOCKED [Slice007]",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
            "commands": [],
        },
        {
            "verdict": "RUN_AUTO",
            "blocker": None,
            "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
            "commands": [],
        },
    ]

    with patch("scripts.ppe_watch_operator_mobile.collect_operator_status", side_effect=status_sequence):
        with patch("scripts.ppe_watch_operator_mobile.is_loop_running", return_value=True):
            with patch("scripts.ppe_watch_operator_mobile._heartbeat_due", return_value=False):
                with patch("scripts.ppe_watch_operator_mobile.send_ntfy", return_value=True) as send:
                    watch_once(tmp_path, write_report=False)
                    second = watch_once(tmp_path, write_report=False)

    assert second["alerts_sent"] == 1
    title, body = send.call_args[0][0], send.call_args[0][1]
    assert title.startswith("PPE fixed:")
    assert "IDE_BUILD" in body
    assert "PRODUCT_BLOCKED" in body
    assert "RUN_AUTO" in body
