"""Tests for IDE handoff when headless agent CLI is unavailable."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_ide_handoff import (
    BUILD_LOG_REL,
    cli_usage_exhausted,
    handoff_recently_done,
    launch_ide_handoff,
    mark_cli_usage_exhausted,
    respond_to_ide_build,
    should_attempt_cli_build,
    text_indicates_usage_exhausted,
)


def test_text_indicates_usage_exhausted():
    assert text_indicates_usage_exhausted("You're out of usage. Switch to Auto")
    assert not text_indicates_usage_exhausted("build succeeded")


def test_cli_usage_exhausted_from_log(tmp_path):
    log = tmp_path / BUILD_LOG_REL
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("stderr\nout of usage\n", encoding="utf-8")
    assert cli_usage_exhausted(tmp_path) is True


def test_cli_usage_exhausted_from_state(tmp_path):
    mark_cli_usage_exhausted(tmp_path, detail="quota")
    assert cli_usage_exhausted(tmp_path) is True
    assert should_attempt_cli_build(tmp_path) is False


def test_launch_ide_handoff_writes_starter(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    with patch("scripts.ppe_ide_build_starter.build_starter_md", return_value="# starter\n"):
        result = launch_ide_handoff(
            tmp_path,
            slice_id="MVP1-Slice002",
            plan_path="docs/SOP/PHASE_PLANS/foo.json",
            source="test",
            reason="usage exhausted",
            force=True,
        )
    assert result["started"] is True
    assert (tmp_path / "artifacts/orchestrator/IDE_BUILD_STARTER_MVP1-Slice002.md").is_file()
    assert (tmp_path / "artifacts/orchestrator/IDE_BUILD_NOW.md").is_file()


def test_handoff_debounce(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_IDE_HANDOFF_DEBOUNCE_SEC", "3600")
    state_path = tmp_path / "artifacts/orchestrator/IDE_HANDOFF_STATE.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "last_handoff_slice": "MVP1-Slice002",
                "last_handoff_at": "2099-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    assert handoff_recently_done(tmp_path, "MVP1-Slice002") is True


def test_respond_skips_cli_when_usage_exhausted(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    mark_cli_usage_exhausted(tmp_path, detail="out of usage")
    status = {
        "verdict": "IDE_BUILD",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "guard": {"detail": "product [MVP1-Slice002] blocked"},
    }
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
                result = respond_to_ide_build(tmp_path, source="test")
    assert result["mode"] == "ide_handoff"
    assert result["started"] is True
    assert result.get("cli_attempted") is False
