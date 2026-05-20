"""MVP1 belief-input UX module surface."""

from __future__ import annotations

from src.viz import app_panels


def test_compute_mvp1_belief_overlay_state_exported():
    assert callable(app_panels.compute_mvp1_belief_overlay_state)
