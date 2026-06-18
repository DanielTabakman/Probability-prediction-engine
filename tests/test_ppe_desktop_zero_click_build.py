"""Tests for desktop zero-click IDE BUILD stack."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_desktop_zero_click_build import (
    collect_status,
    ensure_no_loop_guard,
    ensure_opt_in_token,
    zero_click_desired,
)


def test_ensure_opt_in_creates_token(tmp_path):
    (tmp_path / "ppe_operator_desktop_auto.local.cmd.example").write_text(
        'set "PPE_DESKTOP_AUTO=1"\n', encoding="utf-8"
    )
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text('set "PPE_STACK_FORBIDDEN=1"\n', encoding="utf-8")
    out = ensure_opt_in_token(tmp_path)
    assert out["ok"] is True
    assert out["action"] == "created"
    assert (tmp_path / "ppe_operator_desktop_auto.local.cmd").is_file()


def test_zero_click_desired_daily_driver(tmp_path):
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text("x\n", encoding="utf-8")
    (tmp_path / "ppe_operator_desktop_auto.local.cmd").write_text("x\n", encoding="utf-8")
    assert zero_click_desired(tmp_path) is True


def test_zero_click_not_desired_without_opt_in(tmp_path):
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text("x\n", encoding="utf-8")
    assert zero_click_desired(tmp_path) is False


def test_ensure_no_loop_guard_creates_from_example(tmp_path):
    (tmp_path / "ppe_operator_no_loop.local.cmd.example").write_text(
        'set "PPE_STACK_FORBIDDEN=1"\n', encoding="utf-8"
    )
    out = ensure_no_loop_guard(tmp_path)
    assert out["ok"] is True
    assert (tmp_path / "ppe_operator_no_loop.local.cmd").is_file()


def test_collect_status_includes_watcher_fields(tmp_path):
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text("x\n", encoding="utf-8")
    with patch("scripts.ppe_desktop_zero_click_build.is_local_trigger_watcher_running", return_value=False):
        with patch("scripts.ppe_desktop_zero_click_build.local_trigger_watcher_desired", return_value=True):
            with patch("scripts.ppe_desktop_zero_click_build.check_agent_cli", return_value={"ok": True, "code": "OK"}):
                status = collect_status(tmp_path)
    assert "watcher_running" in status
    assert status["role"] == "daily_driver"
