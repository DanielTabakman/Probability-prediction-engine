"""Tests for remote ntfy build command."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_ntfy_commands import parse_command_text
from scripts.ppe_remote_build_agent import resolve_build_target


def test_parse_build_command(monkeypatch):
    monkeypatch.delenv("PPE_NTFY_CMD_SECRET", raising=False)
    assert parse_command_text("build") is None
    monkeypatch.setenv("PPE_NTFY_CMD_SECRET", "s3cret")
    assert parse_command_text("s3cret build").name == "build"
    assert parse_command_text("s3cret build extra context").args == "extra context"


def test_resolve_build_ide_build(monkeypatch, tmp_path):
    status = {
        "verdict": "IDE_BUILD",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "guard": {"detail": "product [MVP1-Slice002, MVP1-Slice003] blocked"},
        "blocker": "product blocked",
    }
    with patch("scripts.ppe_remote_build_agent.collect_operator_status", return_value=status):
        with patch("scripts.ppe_ide_product_ready.next_pending_product_slice", return_value=None):
            target = resolve_build_target(tmp_path)
    assert target["ok"] is True
    assert target["mode"] == "ide_build"
    assert target["slice_id"] == "MVP1-Slice002"


def test_execute_build_launches_agent(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_CMD_ENABLED", "1")
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    monkeypatch.setenv("PPE_PREFER_IDE_OVER_CLI", "1")
    with patch(
        "scripts.ppe_remote_build_agent.resolve_build_target",
        return_value={
            "ok": True,
            "mode": "ide_build",
            "slice_id": "MVP1-Slice002",
            "plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        },
    ):
        with patch("scripts.ppe_remote_build_agent.read_build_lock", return_value=None):
            with patch("scripts.ppe_ide_build_starter.build_starter_md", return_value="# starter\n"):
                from scripts.ppe_ntfy_commands import execute_build

                result = execute_build(tmp_path)
    assert result["started"] is True
    assert result["slice_id"] == "MVP1-Slice002"
    assert result["mode"] == "ide_handoff"
