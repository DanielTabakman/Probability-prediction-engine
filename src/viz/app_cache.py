"""
Streamlit cache wrappers for network/data fetches used by `src/viz/app.py`.

This module is intentionally thin: it only defines TTL constants and `@st.cache_data`
wrappers around existing fetch functions.
"""

from __future__ import annotations

import streamlit as st

from src.data import fetch_polymarket_markets, fetch_yahoo_prices
from src.data.assets_registry import asset_venue, default_asset_id, deribit_currency, is_usd_premium_options_venue
from src.data.fetch_btc_options import fetch_btc_options_summary
from src.data.fetch_deribit import (
    DEFAULT_OPTION_EXPIRIES_MAX,
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
    fetch_deribit_index,
    fetch_deribit_option_expiries,
    fetch_deribit_option_marks_by_expiry_full,
    last_deribit_instruments_diagnostic,
)

# Cached fetches (2 min TTL) — avoids re-fetch on every sidebar change
CACHE_TTL = 120
# Shorter TTL for option expiries so a transient empty result is not stuck as long.
CACHE_TTL_OPTION_EXPIRIES = 30


def _norm_asset_id(asset_id: str | None) -> str:
    return (asset_id or default_asset_id()).strip().upper()


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
def cached_lab_spot(asset_id: str | None = None):
    """Spot/index for implied lab (Deribit index, Bybit index, or equity Yahoo spot)."""
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_spot

        return fetch_bybit_spot(asset_id=aid)
    if asset_venue(aid) == "equity":
        from src.data.fetch_equity_options import fetch_equity_spot

        return fetch_equity_spot(asset_id=aid)
    return fetch_deribit_index(deribit_currency(aid))


@st.cache_data(ttl=CACHE_TTL)
def cached_option_instruments(asset_id: str | None = None):
    """Single get_instruments(option) payload; keyed by asset for cache isolation."""
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_options_instruments

        return fetch_bybit_options_instruments(asset_id=aid)
    if asset_venue(aid) == "equity":
        return []
    from src.data.fetch_deribit import fetch_deribit_options_instruments

    return fetch_deribit_options_instruments(deribit_currency(aid), expired=False)


@st.cache_data(ttl=CACHE_TTL)
def cached_option_book_marks(asset_id: str | None = None):
    """Book summary by currency; keyed by asset for cache isolation."""
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_option_book_marks

        return fetch_bybit_option_book_marks(asset_id=aid)
    if asset_venue(aid) == "equity":
        return []
    from src.data.fetch_deribit import fetch_deribit_option_book_marks

    return fetch_deribit_option_book_marks(currency=deribit_currency(aid))


@st.cache_data(ttl=CACHE_TTL)
def cached_bull_spreads(spot_price, spread_width, max_expiries, asset_id: str | None = None):
    aid = _norm_asset_id(asset_id)
    inst = cached_option_instruments(aid)
    marks = cached_option_book_marks(aid)
    if is_usd_premium_options_venue(aid):
        return []
    from src.data.fetch_deribit import fetch_deribit_tight_bull_spreads

    return fetch_deribit_tight_bull_spreads(
        spot_price=spot_price,
        spread_width=spread_width,
        max_expiries=max_expiries,
        instruments=inst,
        option_book_marks=marks,
        currency=deribit_currency(aid),
    )


@st.cache_data(ttl=CACHE_TTL)
def cached_options_for_chart(asset_id: str | None = None):
    aid = _norm_asset_id(asset_id)
    inst = cached_option_instruments(aid)
    if is_usd_premium_options_venue(aid):
        return []
    from src.data.fetch_deribit import fetch_deribit_options_for_chart

    return fetch_deribit_options_for_chart(instruments=inst, currency=deribit_currency(aid))


@st.cache_data(ttl=CACHE_TTL_OPTION_EXPIRIES)
def cached_option_expiries(max_expiries=DEFAULT_OPTION_EXPIRIES_MAX, asset_id: str | None = None):
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_option_expiries

        rows = fetch_bybit_option_expiries(asset_id=aid, max_expiries=max_expiries)
        normalized = [
            {
                "expiry_date_str": str(r["expiry_date_str"]),
                "expiry_ts": int(r["expiry_ts"]),
            }
            for r in rows
        ]
        return normalized, {}
    if asset_venue(aid) == "equity":
        from src.data.fetch_equity_options import fetch_equity_option_expiries

        rows = fetch_equity_option_expiries(asset_id=aid, max_expiries=max_expiries)
        normalized = [
            {
                "expiry_date_str": str(r["expiry_date_str"]),
                "expiry_ts": int(r["expiration_timestamp"]),
            }
            for r in rows
        ]
        return normalized, {}
    return fetch_deribit_option_expiries(
        max_expiries, currency=deribit_currency(aid)
    ), last_deribit_instruments_diagnostic(deribit_currency(aid))


@st.cache_data(ttl=CACHE_TTL)
def cached_forward_iv(expiry_ts, spot, asset_id: str | None = None):
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_forward_and_iv_for_expiry

        return fetch_bybit_forward_and_iv_for_expiry(expiry_ts, spot, asset_id=aid)
    if asset_venue(aid) == "equity":
        from src.data.fetch_equity_options import fetch_equity_forward_and_iv_for_expiry

        return fetch_equity_forward_and_iv_for_expiry(expiry_ts, spot, asset_id=aid)
    return fetch_deribit_forward_and_iv_for_expiry(
        expiry_ts, spot, currency=deribit_currency(aid)
    )


@st.cache_data(ttl=CACHE_TTL)
def cached_marks_full(expiry_ts, asset_id: str | None = None):
    aid = _norm_asset_id(asset_id)
    if asset_venue(aid) == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_option_marks_by_expiry_full

        return fetch_bybit_option_marks_by_expiry_full(expiry_ts, asset_id=aid)
    if asset_venue(aid) == "equity":
        from src.data.fetch_equity_options import fetch_equity_option_marks_by_expiry_full

        return fetch_equity_option_marks_by_expiry_full(expiry_ts, asset_id=aid)
    return fetch_deribit_option_marks_by_expiry_full(
        expiry_ts, currency=deribit_currency(aid)
    )


@st.cache_data(ttl=CACHE_TTL)
def cached_btc_options_summary():
    return fetch_btc_options_summary()


@st.cache_data(ttl=CACHE_TTL)
def cached_deribit_summary(max_tickers):
    return fetch_deribit_btc_options_summary(max_tickers=max_tickers)
