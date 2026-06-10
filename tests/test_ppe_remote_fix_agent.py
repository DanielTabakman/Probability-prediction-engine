"""Tests for remote fix agent prompt builder."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_remote_fix_agent import build_fix_prompt


def test_build_fix_prompt_includes_verdict(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    status = {
        "verdict": "IDE_BUILD",
        "blocker": "product slice blocked",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "commands": ["generate_ide_build_starter.cmd Slice001 docs/SOP/PHASE_PLANS/foo.json"],
    }
    with patch("scripts.ppe_remote_fix_agent.collect_operator_status", return_value=status):
        prompt = build_fix_prompt(tmp_path, user_note="please fix the smoke failure")
    assert "IDE_BUILD" in prompt
    assert "product slice blocked" in prompt
    assert "please fix the smoke failure" in prompt
    assert "phone" in prompt
