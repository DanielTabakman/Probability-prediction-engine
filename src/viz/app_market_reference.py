"""
Reference-only expanders rendered at the bottom of `src/viz/app.py`.

These sections are intentionally low-coupling and should stay behavior-neutral:
- "Market prices (reference)" (Yahoo)
- "Prediction markets (reference)" (Polymarket)
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd
import streamlit as st

from src.probability_engine.services.market_context import polymarket_events_to_probabilities


def render_market_reference_sections(
    *,
    config: dict[str, Any],
    show_markets: bool,
    show_polymarket: bool,
    cached_yahoo: Callable[[Any, str], pd.DataFrame],
    cached_polymarket: Callable[[bool, bool, int], list[dict[str, Any]]],
) -> None:
    # ---------- Original market prices (all assets) ----------
    if show_markets:
        with st.expander("Market prices (reference)", expanded=False):
            st.subheader("Market prices (Gold, Silver, Bitcoin)")
            symbols = (config.get("markets") or {}).get("yahoo", {}).get("symbols")
            df = cached_yahoo(symbols, "5d")
            if df is not None and not df.empty:
                latest = df.sort_values("timestamp").groupby("symbol").last().reset_index()
                st.dataframe(
                    latest[["symbol", "asset", "close", "timestamp"]].style.format({"close": "{:.2f}"}),
                    use_container_width=True,
                )
                st.line_chart(
                    df.set_index("timestamp").pivot(columns="symbol", values="close").dropna(how="all")
                )
            else:
                st.info("No market data returned. Check symbols and network.")

    if show_polymarket:
        with st.expander("Prediction markets (reference)", expanded=False):
            st.subheader("Prediction markets (Polymarket)")
            keywords = (
                (config.get("prediction_markets") or {})
                .get("polymarket", {})
                .get("topic_keywords")
                or ["bitcoin", "gold", "silver"]
            )
            events: list[dict[str, Any]] = []
            polymarket_failed = False
            try:
                events = cached_polymarket(True, False, 100)
            except Exception as e:
                polymarket_failed = True
                st.warning(
                    f"Polymarket API unavailable ({type(e).__name__}). "
                    "The rest of the app works; only prediction market data is missing. Try again later or check your network."
                )
            probs = polymarket_events_to_probabilities(events, topic_keywords=keywords)
            if probs:
                pm_df = pd.DataFrame(probs)
                st.dataframe(
                    pm_df[["event_title", "market_question", "outcome", "probability", "end_date_iso"]].head(50),
                    use_container_width=True,
                )
            elif polymarket_failed:
                st.caption("Prediction market data will appear here once Polymarket is reachable.")
            else:
                st.info("No matching Polymarket events. Try adjusting topic_keywords in config/sources.yaml.")

