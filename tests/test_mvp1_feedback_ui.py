"""Tests for MVP1 feedback panel gating (demo vs full app)."""

from __future__ import annotations

from src.viz.mvp1_feedback_ui import feedback_panel_enabled


def test_feedback_disabled_on_demo_defaults(monkeypatch):
    monkeypatch.delenv("PPE_ENABLE_FEEDBACK", raising=False)
    monkeypatch.setenv("PPE_ENABLE_SNAPSHOTS", "0")
    assert feedback_panel_enabled() is False


def test_feedback_enabled_on_full_app_defaults(monkeypatch):
    monkeypatch.delenv("PPE_ENABLE_FEEDBACK", raising=False)
    monkeypatch.setenv("PPE_ENABLE_SNAPSHOTS", "1")
    assert feedback_panel_enabled() is True


def test_feedback_explicit_override(monkeypatch):
    monkeypatch.setenv("PPE_ENABLE_SNAPSHOTS", "0")
    monkeypatch.setenv("PPE_ENABLE_FEEDBACK", "1")
    assert feedback_panel_enabled() is True
