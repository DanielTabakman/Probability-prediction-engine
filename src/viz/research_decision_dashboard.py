"""Pure contract loader for the Research Decision Dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from src.viz.app_env import APP_ROOT

GateState = Literal["PASS", "FAIL", "BLOCKED", "NOT_TESTED", "NOT_AUTHORIZED", "INCONCLUSIVE"]

VALID_GATE_STATES: set[str] = {
    "PASS",
    "FAIL",
    "BLOCKED",
    "NOT_TESTED",
    "NOT_AUTHORIZED",
    "INCONCLUSIVE",
}
FIXTURE_PATH = (
    APP_ROOT
    / "fixtures"
    / "research_decision_dashboard"
    / "hedge_backed_event_liquidity_stage0_1_v1.json"
)


@dataclass(frozen=True)
class FunnelStep:
    label: str
    count: int
    note: str


@dataclass(frozen=True)
class GateRow:
    gate: str
    state: GateState
    evidence: str


@dataclass(frozen=True)
class CandidateRow:
    market_id: str
    question: str
    current_state: str
    parsed_contract_fields: dict[str, Any]
    canonical_classification: str
    rejection_or_watch_reasons: list[str]
    hedge_compilation_ran: bool
    source_pointer: str | None
    evidence_timestamp_utc: str | None


@dataclass(frozen=True)
class ResearchDecisionDashboardV1:
    schema_version: str
    initiative_id: str
    display_name: str
    stage: str
    as_of_utc: str
    theory_statement: str
    mechanism_steps: list[str]
    theory_status: str
    venue_or_branch_status: str
    profitability_status: str
    execution_status: str
    recommendation: str
    funnel: list[FunnelStep]
    gates: list[GateRow]
    candidates: list[CandidateRow]
    interpretation: dict[str, str]
    reopen_conditions: list[str]
    provenance: dict[str, Any]
    warnings: list[str]


class ResearchDecisionDashboardError(ValueError):
    """Raised when a dashboard contract is missing required or valid fields."""


def load_default_research_decision_dashboard() -> ResearchDecisionDashboardV1:
    return load_research_decision_dashboard(FIXTURE_PATH)


def load_research_decision_dashboard(path: Path) -> ResearchDecisionDashboardV1:
    data = json.loads(path.read_text(encoding="utf-8"))
    return parse_research_decision_dashboard(data)


def parse_research_decision_dashboard(data: dict[str, Any]) -> ResearchDecisionDashboardV1:
    required = [
        "schema_version",
        "initiative_id",
        "display_name",
        "stage",
        "as_of_utc",
        "theory_statement",
        "mechanism_steps",
        "theory_status",
        "venue_or_branch_status",
        "profitability_status",
        "execution_status",
        "recommendation",
        "funnel",
        "gates",
        "candidates",
        "interpretation",
        "reopen_conditions",
        "provenance",
        "warnings",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise ResearchDecisionDashboardError(f"Missing dashboard fields: {', '.join(missing)}")
    if data["schema_version"] != "ResearchDecisionDashboardV1":
        raise ResearchDecisionDashboardError(f"Unsupported schema_version: {data['schema_version']}")

    gates = [_parse_gate(row) for row in _list(data, "gates")]
    funnel = [
        FunnelStep(label=str(row["label"]), count=int(row["count"]), note=str(row.get("note") or ""))
        for row in _list(data, "funnel")
    ]
    candidates = [
        CandidateRow(
            market_id=str(row["market_id"]),
            question=str(row["question"]),
            current_state=str(row["current_state"]),
            parsed_contract_fields=dict(row.get("parsed_contract_fields") or {}),
            canonical_classification=str(row["canonical_classification"]),
            rejection_or_watch_reasons=[str(item) for item in row.get("rejection_or_watch_reasons") or []],
            hedge_compilation_ran=bool(row.get("hedge_compilation_ran")),
            source_pointer=row.get("source_pointer"),
            evidence_timestamp_utc=row.get("evidence_timestamp_utc"),
        )
        for row in _list(data, "candidates")
    ]
    _validate_semantics(data, funnel, gates, candidates)
    return ResearchDecisionDashboardV1(
        schema_version=str(data["schema_version"]),
        initiative_id=str(data["initiative_id"]),
        display_name=str(data["display_name"]),
        stage=str(data["stage"]),
        as_of_utc=str(data["as_of_utc"]),
        theory_statement=str(data["theory_statement"]),
        mechanism_steps=[str(item) for item in _list(data, "mechanism_steps")],
        theory_status=str(data["theory_status"]),
        venue_or_branch_status=str(data["venue_or_branch_status"]),
        profitability_status=str(data["profitability_status"]),
        execution_status=str(data["execution_status"]),
        recommendation=str(data["recommendation"]),
        funnel=funnel,
        gates=gates,
        candidates=candidates,
        interpretation={str(k): str(v) for k, v in dict(data["interpretation"]).items()},
        reopen_conditions=[str(item) for item in _list(data, "reopen_conditions")],
        provenance=dict(data["provenance"]),
        warnings=[str(item) for item in _list(data, "warnings")],
    )


def _parse_gate(row: dict[str, Any]) -> GateRow:
    state = str(row["state"])
    if state not in VALID_GATE_STATES:
        raise ResearchDecisionDashboardError(f"Unknown gate state: {state}")
    return GateRow(gate=str(row["gate"]), state=state, evidence=str(row.get("evidence") or ""))  # type: ignore[arg-type]


def _list(data: dict[str, Any], key: str) -> list[Any]:
    value = data[key]
    if not isinstance(value, list):
        raise ResearchDecisionDashboardError(f"{key} must be a list")
    return value


def _validate_semantics(
    data: dict[str, Any],
    funnel: list[FunnelStep],
    gates: list[GateRow],
    candidates: list[CandidateRow],
) -> None:
    if data["theory_status"] != "PLAUSIBLE_NOT_ECONOMICALLY_TESTED":
        raise ResearchDecisionDashboardError("First fixture must preserve plausible-not-economically-tested theory")
    if data["venue_or_branch_status"] != "STOPPED_POLYMARKET":
        raise ResearchDecisionDashboardError("First fixture must preserve stopped Polymarket branch status")
    if data["profitability_status"] != "NOT_TESTED":
        raise ResearchDecisionDashboardError("First fixture must preserve profitability NOT_TESTED")
    if data["execution_status"] != "NOT_AUTHORIZED":
        raise ResearchDecisionDashboardError("First fixture must preserve execution NOT_AUTHORIZED")
    if data["recommendation"] != "STOP_POLYMARKET_BRANCH":
        raise ResearchDecisionDashboardError("First fixture must preserve STOP_POLYMARKET_BRANCH")
    counts_by_label = {row.label: row.count for row in funnel}
    expected_counts = {
        "general market objects discovered": 1100,
        "BTC threshold candidates frozen": 7,
        "semantically eligible": 0,
        "synthetic hedges constructed": 0,
        "executable discrepancies tested": 0,
        "shadow trades": 0,
    }
    if counts_by_label != expected_counts:
        raise ResearchDecisionDashboardError(f"Unexpected funnel counts: {counts_by_label}")
    states_by_gate = {row.gate: row.state for row in gates}
    expected_states = {
        "Terminal BTC contract availability": "FAIL",
        "Hedge compilation": "BLOCKED",
        "Full executable cost stack": "NOT_TESTED",
        "Historical profitability": "NOT_TESTED",
        "Shadow execution": "NOT_TESTED",
        "Live execution": "NOT_AUTHORIZED",
    }
    for gate, state in expected_states.items():
        if states_by_gate.get(gate) != state:
            raise ResearchDecisionDashboardError(f"{gate} must be {state}")
    if len(candidates) != 7:
        raise ResearchDecisionDashboardError("First fixture must include seven frozen candidates")
    if any(row.canonical_classification == "ELIGIBLE" for row in candidates):
        raise ResearchDecisionDashboardError("First fixture must include zero ELIGIBLE candidates")
