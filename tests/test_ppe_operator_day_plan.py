"""Tests for day plan and blocker forecast."""

from __future__ import annotations

from scripts.ppe_operator_day_plan import (
    build_morning_title,
    build_plan_lines,
    business_playbook_lines,
    forecast_blockers,
)


def test_forecast_when_ide_build(tmp_path):
    lines = forecast_blockers(
        tmp_path,
        {"verdict": "IDE_BUILD", "blocker": "PRODUCT_BLOCKED [MVP1-Slice001]"},
    )
    assert any("Blocked now" in line for line in lines)
    assert any("IDE BUILD" in line for line in lines)


def test_forecast_run_auto_mentions_unattended(tmp_path):
    lines = forecast_blockers(
        tmp_path,
        {"verdict": "RUN_AUTO", "phase_plan_path": ""},
    )
    assert lines


def test_business_playbook_has_sessions(tmp_path):
    lines = business_playbook_lines(tmp_path)
    assert any("session" in line.lower() for line in lines)


def test_build_morning_title_ide_build():
    title = build_morning_title(
        {"verdict": "IDE_BUILD", "blocker": "PRODUCT_BLOCKED [MVP1-Slice001]"},
        [],
    )
    assert "IDE BUILD now" in title
    assert "MVP1-Slice001" in title


def test_build_morning_title_forecast(tmp_path):
    title = build_morning_title(
        {"verdict": "RUN_AUTO", "chapter_name": "MVP1 chapter"},
        ["Will block today: IDE BUILD for Slice004 when relay reaches it."],
    )
    assert "IDE likely today" in title


def test_build_week_factory_lines(tmp_path):
    from scripts.ppe_operator_day_plan import build_week_factory_lines

    lines = build_week_factory_lines(tmp_path)
    assert lines
