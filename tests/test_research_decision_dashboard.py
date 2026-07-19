from __future__ import annotations

import copy
import inspect

import pytest

from src.viz.research_decision_dashboard import (
    CandidateRow,
    ResearchDecisionDashboardError,
    count_eligible_contracts,
    load_default_research_decision_dashboard,
    parse_research_decision_dashboard,
)
from src.viz.research_decision_view import render_research_decision_dashboard


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
    assert dashboard.eligible_contract_count == 0
    assert {row.canonical_classification for row in dashboard.candidates} == {"REJECT"}
    assert all(not row.hedge_compilation_ran for row in dashboard.candidates)


def test_eligible_contract_count_is_derived_from_candidate_rows() -> None:
    rejected = CandidateRow(
        market_id="reject",
        question="Rejected contract?",
        current_state="closed",
        parsed_contract_fields={},
        canonical_classification="REJECT",
        rejection_or_watch_reasons=[],
        hedge_compilation_ran=False,
        source_pointer=None,
        evidence_timestamp_utc=None,
    )
    eligible = CandidateRow(
        market_id="eligible",
        question="Eligible contract?",
        current_state="open",
        parsed_contract_fields={},
        canonical_classification="ELIGIBLE",
        rejection_or_watch_reasons=[],
        hedge_compilation_ran=True,
        source_pointer=None,
        evidence_timestamp_utc=None,
    )

    assert count_eligible_contracts([rejected, eligible]) == 1


def test_renderer_does_not_hard_code_dashboard_interpretation_or_counts() -> None:
    renderer_source = inspect.getsource(render_research_decision_dashboard)

    assert "eligible contracts: `0`" not in renderer_source
    assert "Seven frozen candidates; zero eligible contracts." not in renderer_source
    assert "touch/path-dependent Polymarket BTC contracts" not in renderer_source
    assert "eligible_contract_count" in renderer_source
    assert 'dashboard.interpretation["what_we_learned"]' in renderer_source


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
