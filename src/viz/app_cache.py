"""
Streamlit cache wrappers for network/data fetches used by `src/viz/app.py`.

This module is intentionally thin: it only defines TTL constants and `@st.cache_data`
wrappers around existing fetch functions.
"""

from __future__ import annotations

import streamlit as st

from src.data import fetch_polymarket_markets, fetch_yahoo_prices
from src.data.fetch_btc_options import fetch_btc_options_summary
from src.data.fetch_deribit import (
    fetch_deribit_btc_futures_forward_curve,
    fetch_deribit_btc_index,
    fetch_deribit_btc_option_book_marks,
    fetch_deribit_btc_option_expiries,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_btc_options_instruments,
    fetch_deribit_btc_options_for_chart,
    fetch_deribit_btc_options_summary,
    fetch_deribit_btc_tight_bull_spreads,
    fetch_deribit_forward_and_iv_for_expiry,
    last_deribit_instruments_diagnostic,
)

# Cached fetches (2 min TTL) — avoids re-fetch on every sidebar change
CACHE_TTL = 120
# Shorter TTL for option expiries so a transient empty result is not stuck as long.
CACHE_TTL_OPTION_EXPIRIES = 30


@st.cache_data(ttl=CACHE_TTL)
def cached_yahoo(symbols, period):
    return fetch_yahoo_prices(symbols=symbols, period=period)


@st.cache_data(ttl=CACHE_TTL)
def cached_polymarket(active, closed, limit):
    return fetch_polymarket_markets(active=active, closed=closed, limit=limit)


@st.cache_data(ttl=CACHE_TTL)
def cached_forward_curve(max_contracts):
    return fetch_deribit_btc_futures_forward_curve(max_contracts=max_contracts)


@st.cache_data(ttl=CACHE_TTL)
def cached_deribit_index():
    return fetch_deribit_btc_index()


@st.cache_data(ttl=CACHE_TTL)
def cached_option_instruments():
    """Single get_instruments(option) payload; reused for spreads + options chart."""
    return fetch_deribit_btc_options_instruments(expired=False)


@st.cache_data(ttl=CACHE_TTL)
def cached_option_book_marks():
    """Single get_book_summary_by_currency(BTC, option); reused for spread marks (no per-ticker storm)."""
    return fetch_deribit_btc_option_book_marks()


@st.cache_data(ttl=CACHE_TTL)
def cached_bull_spreads(spot_price, spread_width, max_expiries):
    inst = cached_option_instruments()
    marks = cached_option_book_marks()
    return fetch_deribit_btc_tight_bull_spreads(
        spot_price=spot_price,
        spread_width=spread_width,
        max_expiries=max_expiries,
        instruments=inst,
        option_book_marks=marks,
    )


@st.cache_data(ttl=CACHE_TTL)
def cached_options_for_chart():
    inst = cached_option_instruments()
    return fetch_deribit_btc_options_for_chart(instruments=inst)


@st.cache_data(ttl=CACHE_TTL_OPTION_EXPIRIES)
def cached_option_expiries(max_expiries):
    rows = fetch_deribit_btc_option_expiries(max_expiries=max_expiries)
    return rows, last_deribit_instruments_diagnostic()


@st.cache_data(ttl=CACHE_TTL)
def cached_forward_iv(expiry_ts, spot):
    return fetch_deribit_forward_and_iv_for_expiry(expiry_ts, spot)


@st.cache_data(ttl=CACHE_TTL)
def cached_marks_full(expiry_ts):
    return fetch_deribit_btc_option_marks_by_expiry_full(expiry_ts)


@st.cache_data(ttl=CACHE_TTL)
def cached_btc_options_summary():
    return fetch_btc_options_summary()


@st.cache_data(ttl=CACHE_TTL)
def cached_deribit_summary(max_tickers):
    return fetch_deribit_btc_options_summary(max_tickers=max_tickers)

