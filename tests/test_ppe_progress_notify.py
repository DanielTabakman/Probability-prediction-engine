"""Tests for slice/chapter progress ntfy."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_progress_notify import (
    notify_chapter_complete,
    notify_fix_resolved,
    notify_fix_working,
    notify_slice_complete,
)


def test_notify_slice_complete(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_PROGRESS", "all")
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        ok = notify_slice_complete("RepoHousekeeping-Control-Slice001", plan_path="docs/plan.json")
    assert ok is True
    assert "slice done" in send.call_args[0][0].lower()


def test_slice_skipped_in_chapter_mode(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.delenv("PPE_NTFY_PROGRESS", raising=False)
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        assert notify_slice_complete("Slice001") is False
    send.assert_not_called()


def test_notify_chapter_complete(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        ok = notify_chapter_complete(
            "repo_housekeeping_v1",
            slice_id="RepoHousekeeping-Closeout-Slice004",
            next_chapter="mvp1_probability_method_legibility",
        )
    assert ok is True
    assert "chapter done" in send.call_args[0][0].lower()
    assert "mvp1_probability" in send.call_args[0][1]


def test_progress_disabled(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_PROGRESS", "0")
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        assert notify_slice_complete("X") is False
        assert notify_fix_working("ERROR") is False
    send.assert_not_called()


def test_notify_fix_working(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_PROGRESS", "all")
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        ok = notify_fix_working("IDE_BUILD: PRODUCT_BLOCKED", detail="Slice007")
    assert ok is True
    assert "fixing" in send.call_args[0][0].lower()


def test_notify_fix_resolved(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_PROGRESS", "all")
    with patch("scripts.ppe_progress_notify.send_ntfy", return_value=True) as send:
        ok = notify_fix_resolved(
            "gate failure",
            summary="Ruff fixed; pytest green.",
            verdict="RUN_LOCAL",
        )
    assert ok is True
    assert "fixed" in send.call_args[0][0].lower()
    assert "RUN_LOCAL" in send.call_args[0][1]
