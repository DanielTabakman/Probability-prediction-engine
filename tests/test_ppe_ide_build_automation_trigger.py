"""Tests for IDE BUILD automation trigger JSON."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_ide_build_automation_trigger import (
    TRIGGER_REL,
    load_trigger,
    notify_automation,
    write_trigger_idle,
    write_trigger_pending,
)


def test_write_trigger_pending(tmp_path):
    path = write_trigger_pending(
        tmp_path,
        slice_id="MVP1-Slice002",
        plan_path="docs/SOP/PHASE_PLANS/foo.json",
        starter_rel="artifacts/orchestrator/IDE_BUILD_STARTER_MVP1-Slice002.md",
        reason="test",
        source="unit",
    )
    assert path == tmp_path / TRIGGER_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "pending"
    assert data["sliceId"] == "MVP1-Slice002"
    assert data["starter"].endswith("IDE_BUILD_STARTER_MVP1-Slice002.md")


def test_write_trigger_idle(tmp_path):
    write_trigger_idle(tmp_path, completed_slice="MVP1-Slice002")
    data = load_trigger(tmp_path)
    assert data["status"] == "idle"
    assert data["lastCompletedSlice"] == "MVP1-Slice002"


def test_notify_automation_skips_webhook_without_url(tmp_path):
    result = notify_automation(
        tmp_path,
        handoff={
            "slice_id": "MVP1-Slice002",
            "plan_path": "docs/SOP/PHASE_PLANS/foo.json",
            "starter": "artifacts/orchestrator/IDE_BUILD_STARTER_MVP1-Slice002.md",
            "reason": "test",
            "source": "unit",
        },
    )
    assert result["ok"] is True
    assert (tmp_path / TRIGGER_REL).is_file()
    assert result["webhook"]["skipped"] is True


def test_notify_automation_posts_webhook(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", "https://example.test/hook")
    monkeypatch.setenv("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", "secret")
    with patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.status = 200
        result = notify_automation(
            tmp_path,
            handoff={
                "slice_id": "MVP1-Slice002",
                "plan_path": "docs/SOP/PHASE_PLANS/foo.json",
                "starter": "artifacts/orchestrator/IDE_BUILD_STARTER_MVP1-Slice002.md",
                "reason": "test",
                "source": "unit",
            },
        )
    assert result["ok"] is True
    assert result["webhook"]["ok"] is True
