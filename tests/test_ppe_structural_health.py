"""Tests for scripts/ppe_structural_health.py."""

from __future__ import annotations

from pathlib import Path

from scripts.ppe_structural_health import (
    APP_PY_MAX_LINES,
    collect_structural_metrics,
    evaluate_structural_warnings,
    structural_health_block,
)


def test_app_py_stays_under_monolith_threshold() -> None:
    repo = Path(__file__).resolve().parents[1]
    lines = collect_structural_metrics(repo)["app_py_lines"]
    assert lines > 0
    assert lines <= APP_PY_MAX_LINES, f"src/viz/app.py is {lines} lines (max {APP_PY_MAX_LINES})"


def test_evaluate_warnings_for_high_app_py_lines() -> None:
    warnings = evaluate_structural_warnings(
        {
            "app_py_lines": APP_PY_MAX_LINES + 1,
            "scripts_py_count": 1,
            "product_chapters_since_housekeeping": 0,
        }
    )
    assert any(w["id"] == "app-py-monolith" for w in warnings)


def test_housekeeping_overdue_warning() -> None:
    warnings = evaluate_structural_warnings(
        {
            "app_py_lines": 100,
            "scripts_py_count": 10,
            "product_chapters_since_housekeeping": 3,
        }
    )
    assert any(w["id"] == "housekeeping-overdue" for w in warnings)


def test_structural_health_block_on_repo() -> None:
    repo = Path(__file__).resolve().parents[1]
    block = structural_health_block(repo)
    assert "metrics" in block
    assert "warnings" in block
    assert block["metrics"]["app_py_lines"] > 0
