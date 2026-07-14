"""Tests for the founder portfolio registry."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_founder_pipeline_registry_validates() -> None:
    from scripts.founder_portfolio_registry import pipeline_by_id, validate_registry

    assert validate_registry(REPO) == []
    assert pipeline_by_id("ppe", REPO) is not None
    assert pipeline_by_id("autobuilder", REPO) is not None


def test_txline_is_not_registered_execution_ready_without_charter() -> None:
    from scripts.founder_portfolio_registry import pipeline_by_id

    assert pipeline_by_id("txline", REPO) is None
