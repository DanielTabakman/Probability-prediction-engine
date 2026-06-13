"""Tests for 8am morning digest."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts.ppe_morning_report import (
    build_morning_report,
    is_morning_report_window,
    maybe_send_morning_report,
)


def test_morning_report_window(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_MORNING_REPORT_AT", "08:00")
    tz = ZoneInfo("America/New_York")
    assert is_morning_report_window(datetime(2026, 6, 12, 8, 15, tzinfo=tz)) is True
    assert is_morning_report_window(datetime(2026, 6, 12, 9, 0, tzinfo=tz)) is False


def test_build_morning_report_includes_activity(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    from scripts.ppe_notify_push import record_ntfy_send

    record_ntfy_send("PPE IDE handoff: Slice001", tags=["ppe", "ide"], priority="high", repo=tmp_path)
    title, body = build_morning_report(
        tmp_path,
        {"verdict": "RUN_AUTO", "chapter_name": "MVP1 chapter"},
    )
    assert title == "PPE morning report"
    assert "IDE BUILD" in body or "ide build" in body.lower()
    assert "MVP1 chapter" in body


def test_maybe_send_once_per_day(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_MORNING_REPORT", "1")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    tz = ZoneInfo("America/New_York")
    status = {"verdict": "RUN_AUTO", "chapter_name": "ch"}

    with patch("scripts.ppe_morning_report.is_morning_report_window", return_value=True):
        with patch("scripts.ppe_morning_report.send_ntfy", return_value=True) as send:
            first = maybe_send_morning_report(tmp_path, status)
            second = maybe_send_morning_report(tmp_path, status)
    assert first["sent"] is True
    assert second["sent"] is False
    assert second["reason"] == "already_sent_today"
    send.assert_called_once()
