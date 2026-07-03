"""Tests for desktop automation graduation (Level A → B)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_desktop_automation_graduation import (
    evaluate_graduation,
    load_desktop_automation_env,
    record_automation_success,
)


def test_load_desktop_automation_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("PPE_AUTO_DISPATCH", raising=False)
    (tmp_path / "ppe_operator_desktop_auto.local.cmd").write_text(
        '@echo off\nset "PPE_DESKTOP_AUTO=1"\nset "PPE_AUTO_DISPATCH=1"\n',
        encoding="utf-8",
    )
    out = load_desktop_automation_env(tmp_path)
    assert out.get("loaded") is True
    assert "PPE_AUTO_DISPATCH" in (out.get("applied") or [])


def test_graduation_not_eligible_before_thresholds(tmp_path: Path) -> None:
    state = {"success_count": 2, "first_success_at": "2026-07-01T00:00:00Z"}
    ev = evaluate_graduation(tmp_path, state)
    assert ev.get("level") == "A"
    assert ev.get("eligible") is False


def test_graduation_eligible_after_thresholds(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_AUTO_GRADUATE_SUCCESSES", "3")
    monkeypatch.setenv("PPE_AUTO_GRADUATE_MIN_HOURS", "1")
    old = (datetime.now(timezone.utc) - timedelta(hours=2)).replace(microsecond=0)
    state = {
        "success_count": 3,
        "first_success_at": old.isoformat().replace("+00:00", "Z"),
    }
    ev = evaluate_graduation(tmp_path, state)
    assert ev.get("eligible") is True


def test_record_success_increments(tmp_path: Path) -> None:
    ev = record_automation_success(
        tmp_path,
        event="auto_dispatch",
        report={"ok": True, "action": "DESKTOP_CONTINUE.cmd --no-pause"},
    )
    assert ev.get("success_count") == 1
