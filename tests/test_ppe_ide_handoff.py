"""Tests for IDE handoff when headless agent CLI is unavailable."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_ide_build_automation_trigger import TRIGGER_REL
from scripts.ppe_ide_handoff import (
    BUILD_LOG_REL,
    cli_usage_exhausted,
    clipboard_on_handoff_enabled,
    copy_text_to_clipboard,
    handoff_recently_done,
    launch_ide_fix_handoff,
    launch_ide_handoff,
    mark_cli_usage_exhausted,
    maybe_handoff_after_cli_failure,
    prefer_ide_over_cli,
    respond_to_ide_build,
    should_attempt_cli_build,
    should_attempt_headless_cli,
    text_indicates_usage_exhausted,
)
from scripts.ppe_ide_product_ready import next_pending_product_slice, write_marker


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
    with patch("scripts.ppe_build_worker.codex_available", return_value=False):
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
    trigger = json.loads((tmp_path / TRIGGER_REL).read_text(encoding="utf-8"))
    assert trigger["status"] == "pending"
    assert trigger["sliceId"] == "MVP1-Slice002"


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


def test_prefer_ide_over_cli_skips_cli(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_PREFER_IDE_OVER_CLI", "1")
    assert prefer_ide_over_cli(tmp_path) is True
    assert should_attempt_cli_build(tmp_path) is False


def test_next_pending_product_slice_skips_marked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plan_path = "docs/SOP/PHASE_PLANS/foo.json"
    plan_dir = tmp_path / "docs/SOP/PHASE_PLANS"
    plan_dir.mkdir(parents=True)
    (plan_dir / "foo.json").write_text(
        json.dumps(
            {
                "slices": [
                    {"sliceId": "MVP1-Product-Slice002", "declaredPlane": "PRODUCT-PLANE"},
                    {"sliceId": "MVP1-Product-Slice003", "declaredPlane": "PRODUCT-PLANE"},
                ]
            }
        ),
        encoding="utf-8",
    )
    write_marker(
        tmp_path,
        phase_plan_path=plan_path,
        slice_id="MVP1-Product-Slice002",
        build_branch="build/auto/MVP1-Product-Slice002",
        commit_sha="abc",
    )
    assert next_pending_product_slice(tmp_path, plan_path=plan_path) == "MVP1-Product-Slice003"


def test_respond_skips_cli_when_usage_exhausted(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    monkeypatch.setenv("PPE_PREFER_IDE_OVER_CLI", "1")
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


def test_should_attempt_headless_cli_fix_ignores_auto_remote_build(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_AUTO_REMOTE_BUILD", "0")
    monkeypatch.delenv("PPE_PREFER_IDE_OVER_CLI", raising=False)
    monkeypatch.delenv("PPE_FORCE_IDE_HANDOFF", raising=False)
    assert should_attempt_headless_cli(tmp_path, mode="fix") is True
    assert should_attempt_cli_build(tmp_path) is False


def test_launch_ide_fix_handoff_writes_now_doc(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    result = launch_ide_fix_handoff(
        tmp_path,
        verdict="ERROR",
        blocker="gate failed",
        prompt="Investigate and fix.",
        source="test",
        reason="usage exhausted",
        force=True,
    )
    assert result["started"] is True
    assert (tmp_path / "artifacts/orchestrator/IDE_FIX_NOW.md").is_file()
    assert "ERROR" in (tmp_path / "artifacts/orchestrator/IDE_FIX_NOW.md").read_text(encoding="utf-8")


def test_worker_fix_failure_triggers_handoff(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NOTIFY", "0")
    monkeypatch.setenv("PPE_IDE_HANDOFF_OPEN", "0")
    job = {
        "log_name": "REMOTE_FIX_AGENT.log",
        "handoff": {
            "mode": "fix",
            "verdict": "ERROR",
            "blocker": "smoke",
            "source": "phone",
            "user_note": "",
        },
    }
    with patch("scripts.ppe_remote_fix_agent.collect_operator_status", return_value={"verdict": "ERROR", "blocker": "smoke", "commands": []}):
        result = maybe_handoff_after_cli_failure(tmp_path, job, {"ok": False, "stderr_head": "failed"})
    assert result is not None
    assert result.get("verdict") == "ERROR"
    assert (tmp_path / "artifacts/orchestrator/IDE_FIX_NOW.md").is_file()


def test_clipboard_on_handoff_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PPE_IDE_HANDOFF_CLIPBOARD", raising=False)
    assert clipboard_on_handoff_enabled() is False


def test_clipboard_on_handoff_opt_in(monkeypatch):
    monkeypatch.setenv("PPE_IDE_HANDOFF_CLIPBOARD", "1")
    assert clipboard_on_handoff_enabled() is True


def test_copy_text_to_clipboard_skipped_when_disabled(monkeypatch):
    monkeypatch.setenv("PPE_IDE_HANDOFF_CLIPBOARD", "0")
    result = copy_text_to_clipboard("hello")
    assert result.get("skipped") is True
    assert result.get("ok") is False
