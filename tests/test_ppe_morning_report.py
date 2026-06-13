"""Tests for operator daily metrics and 8am morning digest."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts.ppe_morning_report import (
    build_morning_report,
    is_morning_report_window,
    maybe_send_morning_report,
)
from scripts.ppe_operator_daily_metrics import (
    format_duration,
    format_pct,
    get_day_metrics,
    record_chapter_completed,
    record_slice_completed,
    record_watch_sample,
    slice_kind,
    yesterday_local_date,
)


def test_morning_report_window(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_MORNING_REPORT_AT", "08:00")
    tz = ZoneInfo("America/New_York")
    assert is_morning_report_window(datetime(2026, 6, 12, 8, 15, tzinfo=tz)) is True
    assert is_morning_report_window(datetime(2026, 6, 12, 9, 0, tzinfo=tz)) is False


def test_slice_kind_inference():
    assert slice_kind("MVP1-DistQuantV2-Product-Slice004") == "product"
    assert slice_kind("MVP1-DistQuantV2-Control-Slice001") == "control"


def test_record_watch_sample_accumulates_uptime(tmp_path):
    tz = ZoneInfo("America/New_York")
    t0 = datetime(2026, 6, 12, 10, 0, tzinfo=tz).astimezone(timezone.utc)
    t1 = t0 + timedelta(minutes=30)

    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=t0)
    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=t1)

    day = get_day_metrics(tmp_path, "2026-06-12")
    assert day["runningSec"] >= 30 * 60


def test_maintenance_downtime_not_counted_as_gap(tmp_path):
    tz = ZoneInfo("America/New_York")
    t0 = datetime(2026, 6, 12, 10, 0, tzinfo=tz).astimezone(timezone.utc)
    t2 = t0 + timedelta(minutes=20)

    from scripts.ppe_operator_maintenance import save_maintenance

    save_maintenance(
        tmp_path,
        {
            "active": True,
            "since": t0.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "reason": "desktop IDE work",
            "setBy": "test",
        },
    )
    record_watch_sample(tmp_path, loop_running=False, verdict="IDE_BUILD", now=t0)
    record_watch_sample(tmp_path, loop_running=False, verdict="IDE_BUILD", now=t2)

    day = get_day_metrics(tmp_path, "2026-06-12")
    assert day["downIntentionalSec"] >= 18 * 60
    assert day["downUnexpectedSec"] == 0


def test_unmarked_downtime_counts_as_gap(tmp_path):
    tz = ZoneInfo("America/New_York")
    t0 = datetime(2026, 6, 12, 10, 0, tzinfo=tz).astimezone(timezone.utc)
    t1 = t0 + timedelta(minutes=2)
    t2 = t0 + timedelta(minutes=17)

    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=t0)
    record_watch_sample(tmp_path, loop_running=False, verdict="RUN_AUTO", now=t1)
    record_watch_sample(tmp_path, loop_running=False, verdict="RUN_AUTO", now=t2)

    day = get_day_metrics(tmp_path, "2026-06-12")
    assert day["downUnexpectedSec"] >= 13 * 60
    assert day["downIntentionalSec"] == 0


def test_record_completions(tmp_path):
    tz = ZoneInfo("America/New_York")
    at = datetime(2026, 6, 12, 15, 0, tzinfo=tz).astimezone(timezone.utc)
    record_slice_completed(
        tmp_path,
        slice_id="MVP1-DistQuantV2-Product-Slice003",
        plan_path="docs/plan.json",
        at=at,
    )
    record_chapter_completed(tmp_path, chapter_id="mvp1_chapter", at=at)

    day = get_day_metrics(tmp_path, "2026-06-12")
    assert len(day["slicesCompleted"]) == 1
    assert day["slicesCompleted"][0]["kind"] == "product"
    assert len(day["chaptersCompleted"]) == 1


def test_build_morning_report_metrics_focus(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    tz = ZoneInfo("America/New_York")
    yday = yesterday_local_date()
    year, month, day = (int(x) for x in yday.split("-"))
    at = datetime(year, month, day, 15, 0, tzinfo=tz).astimezone(timezone.utc)
    record_slice_completed(tmp_path, slice_id="MVP1-DistQuantV2-Product-Slice003", at=at)

    title, body = build_morning_report(
        tmp_path,
        {"verdict": "RUN_AUTO", "chapter_name": "MVP1 chapter", "manifest_status": "READY"},
    )
    assert title.startswith("PPE:")
    assert "MVP1 chapter" in title or "MVP1 chapter" in body
    assert "Slices closed:" in body
    assert "Alerts sent" not in body
    assert "06-12 12:" not in body
    assert "Yesterday's output:" in body
    assert "Business playbook:" in body


def test_progress_backfill_when_metrics_empty(tmp_path):
    from scripts.ppe_phase_plan_window import save_progress

    tz = ZoneInfo("America/New_York")
    at = datetime(2026, 6, 12, 16, 0, tzinfo=tz).astimezone(timezone.utc)
    save_progress(
        tmp_path,
        {
            "planPath": "docs/plans/test.json",
            "completedSliceIds": ["MVP1-DistQuantV2-Product-Slice003"],
            "updatedAt": at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
    )
    day = get_day_metrics(tmp_path, "2026-06-12")
    assert len(day["slicesCompleted"]) == 1
    assert day["slicesCompleted"][0]["id"] == "MVP1-DistQuantV2-Product-Slice003"


def test_uptime_trend_line(tmp_path):
    from scripts.ppe_operator_daily_metrics import record_watch_sample, uptime_trend_line

    tz = ZoneInfo("America/New_York")
    d1 = datetime(2026, 6, 11, 12, 0, tzinfo=tz).astimezone(timezone.utc)
    d2 = d1 + timedelta(hours=20)
    d3 = datetime(2026, 6, 12, 12, 0, tzinfo=tz).astimezone(timezone.utc)
    d4 = d3 + timedelta(hours=10)

    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=d1)
    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=d2)
    record_watch_sample(tmp_path, loop_running=True, verdict="RUN_AUTO", now=d3)
    record_watch_sample(tmp_path, loop_running=False, verdict="RUN_AUTO", now=d4)

    trend = uptime_trend_line(tmp_path, "2026-06-12")
    assert trend is not None
    assert "vs prior day" in trend


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


def test_format_duration_and_pct():
    assert format_duration(3661) == "1h 1m"
    assert format_pct(1, 4) == "25%"
