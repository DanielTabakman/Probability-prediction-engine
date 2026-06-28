"""Streamlit debug surface for forward consistency (research-only)."""

from __future__ import annotations

import streamlit as st

from src.data.forward_consistency_quotes import build_forward_consistency_live
from src.viz.lab_asset_selection import render_lab_asset_selector


def render_forward_consistency_spike() -> None:
    st.subheader("No-Arbitrage Check — forward consistency (debug)")
    st.caption(
        "Research only. Compares option-implied synthetic forward (put-call parity, bid/ask) "
        "to dated future/perp quotes. Not order execution."
    )
    asset_id = render_lab_asset_selector(key="forward_consistency_asset")
    expiry = st.text_input("Expiry (YYYY-MM-DD or Strategy Lab string)", value="")
    if st.button("Run check", type="primary"):
        if not expiry.strip():
            st.warning("Enter an expiry date.")
            return
        with st.spinner("Fetching live bid/ask…"):
            payload = build_forward_consistency_live(asset_id=asset_id, expiry_date=expiry.strip())
        status = payload.get("status", "—")
        st.metric("Status", status)
        if payload.get("net_edge_usd") is not None:
            st.metric("Net edge (USD)", f"{float(payload['net_edge_usd']):,.2f}")
        if payload.get("legs"):
            st.write("Suggested legs (simulation only if POSSIBLE_ARB):")
            for leg in payload["legs"]:
                st.write(f"- {leg.get('side', '').upper()} {leg.get('label', '')}")
        st.json(payload)
