from __future__ import annotations

import copy

import pytest

from src.viz.research_decision_dashboard import (
    ResearchDecisionDashboardError,
    load_default_research_decision_dashboard,
    parse_research_decision_dashboard,
)


def test_fixture_preserves_required_status_distinctions() -> None:
    dashboard = load_default_research_decision_dashboard()

    assert dashboard.theory_status == "PLAUSIBLE_NOT_ECONOMICALLY_TESTED"
    assert dashboard.venue_or_branch_status == "STOPPED_POLYMARKET"
    assert dashboard.profitability_status == "NOT_TESTED"
    assert dashboard.execution_status == "NOT_AUTHORIZED"
    assert dashboard.recommendation == "STOP_POLYMARKET_BRANCH"


def test_fixture_funnel_counts_and_labels() -> None:
    dashboard = load_default_research_decision_dashboard()

    assert {row.label: row.count for row in dashboard.funnel} == {
        "general market objects discovered": 1100,
        "BTC threshold candidates frozen": 7,
        "semantically eligible": 0,
        "synthetic hedges constructed": 0,
        "executable discrepancies tested": 0,
        "shadow trades": 0,
    }
    assert "not 1,100 semantic BTC contract reviews" in dashboard.funnel[0].note


def test_fixture_has_seven_candidates_and_zero_eligible_outcomes() -> None:
    dashboard = load_default_research_decision_dashboard()

    assert len(dashboard.candidates) == 7
    assert {row.canonical_classification for row in dashboard.candidates} == {"REJECT"}
    assert all(not row.hedge_compilation_ran for row in dashboard.candidates)


def test_gate_states_preserve_fail_blocked_not_tested_and_not_authorized() -> None:
    dashboard = load_default_research_decision_dashboard()

    states = {row.gate: row.state for row in dashboard.gates}
    assert states["Terminal BTC contract availability"] == "FAIL"
    assert states["Hedge compilation"] == "BLOCKED"
    assert states["Historical profitability"] == "NOT_TESTED"
    assert states["Live execution"] == "NOT_AUTHORIZED"


def test_unknown_gate_state_is_rejected() -> None:
    dashboard = load_default_research_decision_dashboard()
    data = copy.deepcopy(dashboard.__dict__)
    data["funnel"] = [row.__dict__ for row in dashboard.funnel]
    data["gates"] = [row.__dict__ for row in dashboard.gates]
    data["candidates"] = [row.__dict__ for row in dashboard.candidates]
    data["gates"][0]["state"] = "UNKNOWN"

    with pytest.raises(ResearchDecisionDashboardError, match="Unknown gate state"):
        parse_research_decision_dashboard(data)
