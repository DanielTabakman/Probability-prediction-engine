"""Tests for ppe_go / ppe_director_go handoff."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_director_go import (
    DIRECTOR_PROMPT,
    LITE_STATUS_REL,
    format_user_banner,
    run_director_go,
)
from scripts.ppe_operator_status import VERDICT_RUN_AUTO


def test_run_director_go_run_auto_no_handoff(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {"verdict": VERDICT_RUN_AUTO, "blocker": None, "exit_code": 0}
    with patch("scripts.ppe_director_go.prepare_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            result = run_director_go(tmp_path, open_ide=False)
    assert result["needs_handoff"] is False
    assert result["prompt"] is None
    assert result["burst"] is True
    banner = format_user_banner(result)
    assert "RUN_AUTO" in banner
    assert "Nothing to do" in banner


def test_run_director_go_single_ide_build_handoff(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {
        "verdict": "IDE_BUILD",
        "blocker": "PRODUCT_BLOCKED",
        "exit_code": 7,
    }
    with patch("scripts.ppe_director_go.prepare_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            with patch("scripts.ppe_director_go.copy_text_to_clipboard", return_value={"ok": True}):
                result = run_director_go(tmp_path, open_ide=False, burst=False)
    assert result["needs_handoff"] is True
    assert result["burst"] is False
    assert result["prompt"] == DIRECTOR_PROMPT
    banner = format_user_banner(result)
    assert "what's next" in banner.lower()
    assert "THREAD_ROLE: operator" in banner


def test_run_director_go_burst_default_prompt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake_status = {
        "verdict": "IDE_BUILD",
        "blocker": "PRODUCT_BLOCKED",
        "exit_code": 7,
    }
    fake_plan = {
        "max_cycles": 2,
        "overall_band": "NORMAL",
        "remaining_count": 2,
        "prompt": "@ppe-director Adaptive burst mode. max_workers=2",
        "burst_allowed": True,
    }
    with patch("scripts.ppe_director_go.prepare_operator_status", return_value=fake_status):
        with patch("scripts.ppe_director_go.write_status_report"):
            with patch("scripts.ppe_director_go.refresh_burst_plan", return_value=fake_plan):
                with patch("scripts.ppe_director_go.copy_text_to_clipboard", return_value={"ok": True}):
                    result = run_director_go(tmp_path, open_ide=False)
    assert result["burst"] is True
    assert result["prompt"] == fake_plan["prompt"]
    assert "Adaptive burst" in result["prompt"]
    assert result["burst_plan"]["max_cycles"] == 2


def test_run_director_go_lite_skips_handoff_and_writes_brief(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    status_path = tmp_path / "artifacts/orchestrator/OPERATOR_STATUS.md"
    status_path.parent.mkdir(parents=True)
    status_path.write_text(
        "\n".join(
            [
                "# Operator status",
                "**Verdict:** `RUN_LOCAL`",
                "**Mode:** `CLOSEOUT_ONLY`",
                "Chapter: test_chapter",
                "Plan: docs/SOP/PHASE_TEST.json",
                "Blocker: finish chapter with run_ppe_local",
                "Agent action (auto-execute - not operator):",
                "  1. DESKTOP_CONTINUE.cmd --no-pause",
            ]
        ),
        encoding="utf-8",
    )
    whats_next = tmp_path / "artifacts/control_plane/WHATS_NEXT.md"
    whats_next.parent.mkdir(parents=True, exist_ok=True)
    whats_next.write_text(
        "\n".join(
            [
                "# What's next",
                "",
                "**Next action summary:** compact action",
                "",
                "**Next action detail:** compact action plus " + "long detail " * 80,
            ]
        ),
        encoding="utf-8",
    )
    with patch("scripts.ppe_director_go.prepare_operator_status") as prep:
        with patch("scripts.ppe_director_go.write_status_report") as write_full:
            with patch("scripts.ppe_director_go.refresh_burst_plan") as refresh:
                with patch("scripts.ppe_director_go.copy_text_to_clipboard") as clipboard:
                    result = run_director_go(tmp_path, open_ide=True, lite=True)

    prep.assert_not_called()
    write_full.assert_not_called()
    refresh.assert_not_called()
    clipboard.assert_not_called()
    assert result["needs_handoff"] is False
    assert result["lite"] is True
    assert result["prompt"] is None
    brief = tmp_path / LITE_STATUS_REL
    assert brief.is_file()
    text = brief.read_text(encoding="utf-8")
    assert "Operator Status Brief" in text
    assert "CLOSEOUT_ONLY" in text
    assert "What's next: compact action" in text
    assert "long detail" not in text
    assert "DESKTOP_CONTINUE.cmd --no-pause" in text
    banner = format_user_banner(result)
    assert "PPE GO LITE" in banner
    assert "skipped burst refresh" in banner
