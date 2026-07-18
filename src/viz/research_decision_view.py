"""Streamlit renderer for the Research Decision Dashboard contract."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from src.viz.research_decision_dashboard import ResearchDecisionDashboardV1


def render_research_decision_dashboard(dashboard: ResearchDecisionDashboardV1) -> None:
    st.title("Research Review")
    st.caption(f"{dashboard.display_name} | {dashboard.stage} | {dashboard.as_of_utc}")

    status_cols = st.columns(4)
    status_cols[0].metric("Theory", dashboard.theory_status)
    status_cols[1].metric("Venue / branch", dashboard.venue_or_branch_status)
    status_cols[2].metric("Profitability", dashboard.profitability_status)
    status_cols[3].metric("Execution", dashboard.execution_status)
    st.subheader(dashboard.recommendation)
    st.markdown(
        "\n".join(
            [
                f"- Theory: `{dashboard.theory_status}`",
                f"- Polymarket branch: `{dashboard.venue_or_branch_status}`",
                f"- Profitability: `{dashboard.profitability_status}`",
                f"- Execution: `{dashboard.execution_status}`",
                f"- Frozen candidates: `{len(dashboard.candidates)}`; eligible contracts: `0`",
            ]
        )
    )
    st.write(dashboard.theory_statement)

    st.header("Theory and Mechanism")
    st.write(" -> ".join(dashboard.mechanism_steps))
    st.info(
        "The accepted evidence found touch/path-dependent Polymarket BTC contracts, "
        "not terminal option-payoff-compatible contracts. The general theory is not disproven."
    )

    st.header("Test Funnel")
    st.table(
        pd.DataFrame([asdict(row) for row in dashboard.funnel]),
    )

    st.header("Gate Matrix")
    st.table(
        pd.DataFrame([asdict(row) for row in dashboard.gates]),
    )

    st.header("Candidate Inspector")
    st.caption("Seven frozen candidates; zero eligible contracts.")
    for candidate in dashboard.candidates:
        with st.expander(f"{candidate.market_id} - {candidate.question}", expanded=False):
            cols = st.columns(3)
            cols[0].metric("State", candidate.current_state)
            cols[1].metric("Classification", candidate.canonical_classification)
            cols[2].metric("Hedge compilation ran", "yes" if candidate.hedge_compilation_ran else "no")
            st.write("Rejection / watch reasons")
            st.write(", ".join(candidate.rejection_or_watch_reasons))
            st.json(candidate.parsed_contract_fields)
            if candidate.source_pointer:
                st.markdown(f"Source: [{candidate.source_pointer}]({candidate.source_pointer})")
            if candidate.evidence_timestamp_utc:
                st.caption(f"Evidence timestamp: {candidate.evidence_timestamp_utc}")

    st.header("Interpretation")
    for label in (
        "what_we_learned",
        "what_we_did_not_learn",
        "why_the_branch_stopped_or_continued",
        "reopen_conditions",
    ):
        st.subheader(label.replace("_", " ").title())
        st.write(dashboard.interpretation[label])

    st.header("Reopen Conditions")
    for item in dashboard.reopen_conditions:
        st.write(f"- {item}")

    st.header("Provenance")
    st.json(dashboard.provenance)

    if dashboard.warnings:
        st.header("Warnings")
        for warning in dashboard.warnings:
            st.warning(warning)
