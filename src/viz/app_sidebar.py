"""
Sidebar widget composition for `src/viz/app.py`.

This module is intentionally UI-only. It preserves widget keys and session-state
semantics so refactors remain behavior-neutral.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def build_sidebar_state(*, show_bitcoin_default: bool = True) -> dict[str, Any]:
    st.sidebar.header("Data")
    show_bitcoin_view = st.sidebar.checkbox(
        "Bitcoin view (chart + questions + implied)", value=show_bitcoin_default
    )
    show_markets = st.sidebar.checkbox("Market prices (Yahoo)", value=True)
    show_polymarket = st.sidebar.checkbox("Prediction markets (Polymarket)", value=True)
    chart_days = st.sidebar.slider("Chart history (days)", 5, 90, 30)

    # Chart toggles (always available; optional Deribit overlays gated until Refresh priced inputs)
    st.sidebar.caption("Chart detail")
    show_forward_curve = st.sidebar.checkbox(
        "Show futures forward curve",
        value=True,
        help="Deribit futures at expiry dates.",
    )
    show_bull_spreads = st.sidebar.checkbox(
        "Show tight bull spreads on chart",
        value=True,
        help="Overlay bull call spreads with R:R.",
    )
    show_prediction_spreads = st.sidebar.checkbox(
        "Show prediction-aligned spreads on chart",
        value=True,
        help="Spreads tied to Polymarket questions (blue).",
    )
    show_options_on_chart = st.sidebar.checkbox(
        "Show options on main chart",
        value=False,
        help="Overlay option expiries/strikes.",
    )
    options_in_separate_chart = st.sidebar.checkbox(
        "Options in separate chart below",
        value=True,
        help="Dedicated options chart.",
    )
    option_types_on_chart = st.sidebar.multiselect(
        "Option types",
        ["call", "put"],
        default=["call", "put"],
        key="option_types",
    )
    min_prob_label_pct = st.sidebar.slider(
        "Show probability labels above (%)",
        0,
        50,
        5,
        help="Hide small labels.",
    )

    if show_bitcoin_view:
        st.sidebar.markdown("---")
        st.sidebar.caption("Implied lab — priced inputs")
        if st.sidebar.button("Refresh priced inputs (Deribit)", key="btn_refresh_priced"):
            st.cache_data.clear()
            st.session_state["load_deribit"] = True
            st.rerun()
        st.sidebar.caption(
            "Reloads exchange quotes and chart overlays. Does not reset your belief sliders."
        )
        if not st.session_state.get("load_deribit", False):
            st.sidebar.caption(
                "Deribit forward curve and spread overlays on the main chart load after the first refresh above."
            )

    return {
        "show_bitcoin_view": show_bitcoin_view,
        "show_markets": show_markets,
        "show_polymarket": show_polymarket,
        "chart_days": chart_days,
        "show_forward_curve": show_forward_curve,
        "show_bull_spreads": show_bull_spreads,
        "show_prediction_spreads": show_prediction_spreads,
        "show_options_on_chart": show_options_on_chart,
        "options_in_separate_chart": options_in_separate_chart,
        "option_types_on_chart": option_types_on_chart,
        "min_prob_label_pct": min_prob_label_pct,
    }

