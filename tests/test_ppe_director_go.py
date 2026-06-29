"""Tests for ppe_go / ppe_director_go handoff."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_director_go import DIRECTOR_BURST_PROMPT, DIRECTOR_PROMPT, format_user_banner, run_director_go
from scripts.ppe_operator_status import VERDICT_RUN_AUTO


def test_run_director_go_run_auto_no_handoff(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {"verdict": VERDICT_RUN_AUTO, "blocker": None, "exit_code": 0}
    with patch("scripts.ppe_director_go.collect_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            result = run_director_go(tmp_path, open_ide=False)
    assert result["needs_handoff"] is False
    assert result["prompt"] is None
    banner = format_user_banner(result)
    assert "RUN_AUTO" in banner
    assert "Nothing to do" in banner


def test_run_director_go_ide_build_handoff(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {
        "verdict": "IDE_BUILD",
        "blocker": "PRODUCT_BLOCKED",
        "exit_code": 7,
    }
    with patch("scripts.ppe_director_go.collect_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            with patch("scripts.ppe_director_go.copy_text_to_clipboard", return_value={"ok": True}):
                result = run_director_go(tmp_path, open_ide=False)
    assert result["needs_handoff"] is True
    assert result["prompt"] == DIRECTOR_PROMPT
    banner = format_user_banner(result)
    assert "Ctrl+V" in banner


def test_run_director_go_burst_prompt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {
        "verdict": "IDE_BUILD",
        "blocker": "PRODUCT_BLOCKED",
        "exit_code": 7,
    }
    with patch("scripts.ppe_director_go.collect_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            with patch("scripts.ppe_director_go.copy_text_to_clipboard", return_value={"ok": True}):
                result = run_director_go(tmp_path, open_ide=False, burst=True)
    assert result["burst"] is True
    assert result["prompt"] == DIRECTOR_BURST_PROMPT
    assert "Burst mode" in result["prompt"]
