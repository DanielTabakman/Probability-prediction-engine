"""Streamlit renderer for Market Proposal + Hedge Capacity Preview v0."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.engine.market_proposal_hedge_capacity import (
    MarketProposalHedgeCapacityPreviewV0,
    build_preview_from_fixture,
    export_json,
    export_markdown,
    render_markdown,
    to_dict,
)
from src.viz.app_env import APP_ROOT

FIXTURE_PATH = APP_ROOT / "fixtures" / "market_proposal_hedge_capacity" / "btc_terminal_v0.json"
EXPORT_DIR = APP_ROOT / "artifacts" / "market_proposal_hedge_capacity" / "exports"


def load_default_market_proposal_preview() -> MarketProposalHedgeCapacityPreviewV0:
    return build_preview_from_fixture(FIXTURE_PATH)


def render_market_proposal_hedge_capacity_preview(
    preview: MarketProposalHedgeCapacityPreviewV0 | None = None,
) -> None:
    if preview is None:
        preview = load_default_market_proposal_preview()
    st.title("Market Proposal Preview")
    st.warning(preview.preview_warning)
    st.caption(f"{preview.schema_version} | {preview.as_of_utc} | {preview.readiness_state}")

    with st.form("market_proposal_inputs"):
        st.subheader("Proposed Event Inputs")
        cols = st.columns(4)
        cols[0].selectbox("Underlying", ["BTC"], index=0, disabled=True)
        cols[1].selectbox("Comparator", ["above", "below"], index=0, disabled=True)
        cols[2].number_input(
            "Requested threshold",
            min_value=1.0,
            value=float(preview.requested_event.requested_threshold_usd),
            disabled=True,
        )
        cols[3].number_input(
            "Requested payout",
            min_value=1.0,
            value=float(preview.requested_event.requested_payout_usd),
            disabled=True,
        )
        st.caption("Fixture mode is deterministic and offline. Live refresh is available through the witness script.")
        st.form_submit_button("Generate Fixture Proposal", disabled=True)

    st.header("Generated Contract")
    st.write(preview.proposed_contract.question)
    st.info(preview.proposed_contract.resolution_language)

    st.header("Requested Versus Proposed Threshold")
    threshold_cols = st.columns(3)
    threshold_cols[0].metric("Requested threshold", f"${preview.threshold_adjustment['requested_threshold_usd']:,.0f}")
    threshold_cols[1].metric(
        "Proposed listed-strike threshold",
        f"${preview.threshold_adjustment['proposed_threshold_usd']:,.0f}",
    )
    threshold_cols[2].metric("Delta", f"${preview.threshold_adjustment['threshold_delta_usd']:,.0f}")

    st.header("Hedge Candidates")
    col_yes, col_no = st.columns(2)
    with col_yes:
        _render_side(preview.yes_hedge)
    with col_no:
        _render_side(preview.no_hedge)

    st.header("Capacity Summary")
    st.table(pd.DataFrame([preview.capacity_summary]))

    st.header("Payoff Mismatch")
    rows = []
    for side in (preview.yes_hedge, preview.no_hedge):
        ramp = side.payoff_ramp
        if ramp:
            rows.append(
                {
                    "side": side.exposure,
                    "zero": ramp.zero_payoff_region,
                    "ramp": ramp.linear_ramp_region,
                    "full": ramp.full_payoff_region,
                    "max_mismatch_usd": ramp.maximum_binary_replication_error_usd,
                    "width_pct_threshold": ramp.ramp_width_pct_of_threshold,
                }
            )
    st.table(pd.DataFrame(rows))

    st.header("Cost Stack")
    st.json(preview.cost_stack)

    st.header("Constraints And Unknowns")
    for item in preview.constraints:
        st.write(f"- {item}")
    for item in preview.unknowns:
        st.write(f"- {item}")

    st.header("Provenance And Timestamps")
    st.json(preview.provenance)

    markdown = render_markdown(preview)
    json_text = __import__("json").dumps(to_dict(preview), indent=2, sort_keys=True)
    export_base = EXPORT_DIR / "fixture_market_proposal_hedge_capacity_v0"
    md_path = export_markdown(preview, Path(str(export_base) + ".md"))
    json_path = export_json(preview, Path(str(export_base) + ".json"))
    st.header("Download Proposal")
    st.download_button("Download Markdown", markdown, file_name=md_path.name, mime="text/markdown")
    st.download_button("Download JSON", json_text, file_name=json_path.name, mime="application/json")
    st.caption(f"Fixture export path: {md_path}")


def _render_side(side) -> None:
    st.subheader(f"{side.exposure} Hedge")
    st.metric("Status", side.status)
    st.metric("Policy capacity", f"${side.policy_capacity_usd:,.2f}")
    st.metric("Supported payout", f"${side.supported_payout_usd:,.2f}")
    st.metric("Unsupported remainder", f"${side.unsupported_payout_usd:,.2f}")
    st.metric("Synthetic cost per $1 max payout", side.synthetic_cost_per_1_usd or "n/a")
    if side.legs:
        st.table(
            pd.DataFrame(
                [
                    {
                        "action": leg.action,
                        "instrument": leg.instrument_name,
                        "book side": "asks" if leg.action == "buy" else "bids",
                        "strike": leg.strike,
                        "amount": leg.executable_amount,
                        "vwap_btc": leg.vwap_btc,
                        "timestamp": leg.book_timestamp,
                    }
                    for leg in side.legs
                ]
            )
        )
    if side.capacity_levels:
        st.table(pd.DataFrame([row.__dict__ for row in side.capacity_levels]))
    if side.flags:
        for flag in side.flags:
            st.warning(flag)
