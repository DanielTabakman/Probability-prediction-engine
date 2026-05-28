"""Phase 3 commercial wrapper — dual-smoke witness field (EVIDENCE-PLANE)."""

from __future__ import annotations

from dataclasses import fields

from scripts.implied_lab_ui_smoke_harness import ScenarioResult


def test_scenario_result_has_commercial_wrapper_field() -> None:
    names = {f.name for f in fields(ScenarioResult)}
    assert "commercial_wrapper_found" in names


def test_commercial_wrapper_defaults_false() -> None:
    row = ScenarioResult(scenario="MVP1_compact_verification")
    assert row.commercial_wrapper_found is False
