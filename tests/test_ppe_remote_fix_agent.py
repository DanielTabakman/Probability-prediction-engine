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
        "avoid": ["run_ppe_auto_local_loop.cmd  (will hit PRODUCT_BLOCKED)"],
    }
    target = {
        "ok": True,
        "mode": "ide_build",
        "slice_id": "Slice001",
        "plan_path": "docs/SOP/PHASE_PLANS/foo.json",
    }
    with patch("scripts.ppe_remote_fix_agent.collect_operator_status", return_value=status):
        with patch("scripts.ppe_remote_build_agent.resolve_build_target", return_value=target):
            with patch("scripts.ppe_ide_build_starter.write_starter"):
                prompt = build_fix_prompt(tmp_path, user_note="please fix the smoke failure")
    assert "IDE_BUILD" in prompt
    assert "product slice blocked" in prompt
    assert "please fix the smoke failure" in prompt
    assert "phone" in prompt
    assert "Slice001" in prompt
    assert "IDE_BUILD_STARTER_Slice001.md" in prompt
    assert "AGENT_CONTINUITY_BRIEF" in prompt
    assert "run_ppe_auto_local_loop" in prompt
