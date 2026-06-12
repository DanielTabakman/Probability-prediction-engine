"""Tests for IDE BUILD automation health checks."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_ide_build_automation_health import (
    EXIT_BROKEN,
    EXIT_OK,
    EXIT_QUOTA_ONLY,
    classify_webhook_failure,
    run_health_checks,
)


def test_classify_quota_exhausted():
    assert (
        classify_webhook_failure(
            {"ok": False, "error": "HTTP 400", "detail": 'resource_exhausted'}
        )
        == "WEBHOOK_QUOTA_EXHAUSTED"
    )


def test_classify_ok():
    assert classify_webhook_failure({"ok": True, "status": 200}) == "OK"


def test_health_missing_url(tmp_path, monkeypatch):
    monkeypatch.delenv("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", raising=False)
    report = run_health_checks(tmp_path, ping_webhook=False)
    assert report["verdict"] == "BROKEN"
    assert report["exit_code"] == EXIT_BROKEN
    codes = [c["code"] for c in report["checks"]]
    assert "MISSING_WEBHOOK_URL" in codes


def test_health_quota_only(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", "https://example.test/hook")
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", "secret")
    (tmp_path / "ppe_operator_cursor.local.cmd").write_text("@echo off\n", encoding="utf-8")
    with patch(
        "scripts.ppe_ide_build_automation_health.post_automation_webhook",
        return_value={
            "ok": False,
            "error": "HTTP 400",
            "detail": '{"success":false,"error":"resource_exhausted"}',
        },
    ):
        report = run_health_checks(tmp_path, ping_webhook=True)
    assert report["verdict"] == "QUOTA_BLOCKED"
    assert report["exit_code"] == EXIT_QUOTA_ONLY
    assert report["will_work_when_quota_returns"] is True


def test_health_ok(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", "https://example.test/hook")
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", "secret")
    (tmp_path / "ppe_operator_cursor.local.cmd").write_text("@echo off\n", encoding="utf-8")
    with patch(
        "scripts.ppe_ide_build_automation_health.post_automation_webhook",
        return_value={"ok": True, "status": 200},
    ):
        report = run_health_checks(tmp_path, ping_webhook=True)
    assert report["verdict"] == "OK"
    assert report["exit_code"] == EXIT_OK
