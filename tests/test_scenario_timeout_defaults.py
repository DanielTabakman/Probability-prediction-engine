"""Per-scenario smoke timeout defaults (MVP1 Reliability Slice002)."""

from scripts.implied_lab_ui_smoke_harness import (
    DEFAULT_SCENARIO_TIMEOUT_S,
    default_scenario_timeout_s,
)


def test_mvp1_compact_timeout_budget() -> None:
    assert default_scenario_timeout_s("MVP1_compact_verification") == 15.0 * 60.0


def test_a_width_timeout_budget() -> None:
    assert default_scenario_timeout_s("A_width_target_payoff") == 25.0 * 60.0


def test_unknown_scenario_uses_default() -> None:
    assert default_scenario_timeout_s("B_peak_aligned") == DEFAULT_SCENARIO_TIMEOUT_S
