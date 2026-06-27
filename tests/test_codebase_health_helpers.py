"""Smoke tests for extracted implied-lab submodules."""

from __future__ import annotations


def test_app_implied_lab_frozen_imports() -> None:
    from src.viz.app_implied_lab_frozen import render_implied_lab_frozen_and_strategy_sections

    assert callable(render_implied_lab_frozen_and_strategy_sections)


def test_generate_module_test_coverage_map() -> None:
    from scripts.generate_module_test_coverage_map import generate
    from pathlib import Path

    text = generate(Path(__file__).resolve().parents[1])
    assert "Engine (`src/engine/`)" in text
    assert "strategy_scanner" in text
