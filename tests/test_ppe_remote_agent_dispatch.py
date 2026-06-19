"""Tests for shared CLI → IDE handoff dispatch (build, fix)."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_ide_handoff import FIX_LOG_REL, mark_cli_usage_exhausted
from scripts.ppe_remote_agent_dispatch import respond_remote_agent


def test_respond_fix_ide_build_delegates_to_build(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    monkeypatch.setenv("PPE_PREFER_IDE_OVER_CLI", "1")
    status = {
        "verdict": "IDE_BUILD",
        "blocker": "product slice blocked",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "commands": [],
    }
    target = {
        "ok": True,
        "mode": "ide_build",
        "slice_id": "Slice001",
        "plan_path": "docs/SOP/PHASE_PLANS/foo.json",
    }
    with patch("scripts.ppe_operator_status.collect_operator_status", return_value=status):
        with patch("scripts.ppe_remote_build_agent.resolve_build_target", return_value=target):
            with patch("scripts.ppe_remote_build_agent.read_build_lock", return_value=None):
                with patch("scripts.ppe_ide_handoff.write_starter"):
                    result = respond_remote_agent(tmp_path, mode="fix", source="test")
    assert result["mode"] == "ide_handoff"
    assert result["started"] is True
    assert result.get("slice_id") == "Slice001"
    assert (tmp_path / "artifacts/orchestrator/IDE_BUILD_NOW.md").is_file()


def test_respond_fix_skips_cli_when_prefer_ide(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    monkeypatch.setenv("PPE_PREFER_IDE_OVER_CLI", "1")
    status = {
        "verdict": "ERROR",
        "blocker": "smoke failed",
        "commands": ["run_ppe_local.cmd"],
    }
    with patch("scripts.ppe_operator_status.collect_operator_status", return_value=status):
        with patch("scripts.ppe_remote_fix_agent.build_fix_prompt", return_value="fix prompt"):
            result = respond_remote_agent(tmp_path, mode="fix", source="test")
    assert result["mode"] == "ide_handoff"
    assert result["started"] is True
    assert result.get("cli_attempted") is False
    assert (tmp_path / "artifacts/orchestrator/IDE_FIX_NOW.md").is_file()


def test_cli_usage_exhausted_reads_fix_log(tmp_path):
    log = tmp_path / FIX_LOG_REL
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("agent stderr\nout of usage\n", encoding="utf-8")
    from scripts.ppe_ide_handoff import cli_usage_exhausted

    assert cli_usage_exhausted(tmp_path) is True


def test_respond_fix_cli_failure_handoff_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    mark_cli_usage_exhausted(tmp_path, detail="out of usage")
    status = {
        "verdict": "STALE_STATE",
        "blocker": "plan stuck",
        "commands": [],
    }
    with patch("scripts.ppe_operator_status.collect_operator_status", return_value=status):
        with patch("scripts.ppe_remote_fix_agent.build_fix_prompt", return_value="fix prompt"):
            result = respond_remote_agent(tmp_path, mode="fix", source="test")
    assert result["verdict"] == "STALE_STATE"
    assert result["started"] is True
    assert "IDE_FIX_NOW.md" in str(result.get("now_doc") or "")
