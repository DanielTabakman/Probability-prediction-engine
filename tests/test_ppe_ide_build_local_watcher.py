"""Tests for local IDE BUILD trigger watcher."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_ide_build_automation_trigger import TRIGGER_REL, write_trigger_pending
from scripts.ppe_ide_build_local_watcher import (
    build_trigger_watcher_prompt,
    local_trigger_watcher_enabled,
    try_dispatch_from_trigger,
    trigger_dispatch_key,
    watch_once,
)


def test_local_trigger_watcher_enabled_default(tmp_path):
    assert local_trigger_watcher_enabled(tmp_path) is True


def test_local_trigger_watcher_disabled_by_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_IDE_LOCAL_TRIGGER_WATCHER", "0")
    assert local_trigger_watcher_enabled(tmp_path) is False


def test_trigger_dispatch_key():
    key = trigger_dispatch_key({"sliceId": "Slice002", "handoffAt": "2026-06-14T00:00:00Z"})
    assert key == "Slice002:2026-06-14T00:00:00Z"


def test_try_dispatch_skips_idle(tmp_path):
    result = try_dispatch_from_trigger(tmp_path, {"status": "idle"})
    assert result["skipped"] is True


def test_try_dispatch_starts_agent(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_IDE_LOCAL_TRIGGER_WATCHER", "1")
    write_trigger_pending(
        tmp_path,
        slice_id="MSOS-Slice002",
        plan_path="docs/SOP/PHASE_PLANS/foo.json",
        starter_rel="artifacts/orchestrator/IDE_BUILD_STARTER_MSOS-Slice002.md",
        reason="test",
        source="unit",
    )
    trigger = json.loads((tmp_path / TRIGGER_REL).read_text(encoding="utf-8"))
    with patch("scripts.ppe_ide_build_local_watcher.agent_available", return_value=True):
        with patch("scripts.ppe_ide_build_local_watcher.launch_agent_background") as launch:
            launch.return_value = {"started": True, "worker_pid": 4242, "log": "artifacts/x.log"}
            result = try_dispatch_from_trigger(tmp_path, trigger)
    assert result["started"] is True
    assert result["slice_id"] == "MSOS-Slice002"
    launch.assert_called_once()
    prompt = launch.call_args.kwargs["prompt"]
    assert "MSOS-Slice002" in prompt
    assert "ppe_ide_build_closeout.cmd" in prompt
    data = json.loads((tmp_path / TRIGGER_REL).read_text(encoding="utf-8"))
    assert data["status"] == "dispatched"
    assert data["workerPid"] == 4242


def test_try_dispatch_dedupes_same_handoff(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_IDE_LOCAL_TRIGGER_WATCHER", "1")
    trigger = {
        "status": "pending",
        "sliceId": "MSOS-Slice002",
        "planPath": "docs/SOP/PHASE_PLANS/foo.json",
        "starter": "artifacts/orchestrator/IDE_BUILD_STARTER_MSOS-Slice002.md",
        "handoffAt": "2026-06-14T00:00:00Z",
    }
    with patch("scripts.ppe_ide_build_local_watcher.agent_available", return_value=True):
        with patch("scripts.ppe_ide_build_local_watcher.launch_agent_background") as launch:
            launch.return_value = {"started": True, "worker_pid": 1}
            first = try_dispatch_from_trigger(tmp_path, trigger)
            second = try_dispatch_from_trigger(tmp_path, trigger)
    assert first["started"] is True
    assert second["skipped"] is True
    assert launch.call_count == 1


def test_build_trigger_watcher_prompt_includes_starter():
    prompt = build_trigger_watcher_prompt(
        slice_id="Slice002",
        plan_path="docs/SOP/PHASE_PLANS/foo.json",
        starter_rel="artifacts/orchestrator/IDE_BUILD_STARTER_Slice002.md",
    )
    assert "Slice002" in prompt
    assert "IDE_BUILD_STARTER_Slice002.md" in prompt


def test_watch_once_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_IDE_LOCAL_TRIGGER_WATCHER", "0")
    result = watch_once(tmp_path)
    assert result["skipped"] is True
    assert result["reason"] == "disabled"
