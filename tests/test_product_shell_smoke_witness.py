"""MVP1 product shell clarity — dual-smoke witness field (EVIDENCE-PLANE)."""

from __future__ import annotations

from dataclasses import fields

from scripts.implied_lab_ui_smoke_harness import ScenarioResult


def test_scenario_result_has_product_shell_context_field() -> None:
    names = {f.name for f in fields(ScenarioResult)}
    assert "product_shell_context_found" in names


def test_product_shell_context_defaults_false() -> None:
    row = ScenarioResult(scenario="MVP1_compact_verification")
    assert row.product_shell_context_found is False
