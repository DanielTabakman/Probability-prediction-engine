"""Ensure extracted implied-lab view module imports cleanly."""

from __future__ import annotations


def test_app_implied_lab_view_imports() -> None:
    from src.viz.app_implied_lab_view import render_implied_lab_bitcoin_section

    assert callable(render_implied_lab_bitcoin_section)
