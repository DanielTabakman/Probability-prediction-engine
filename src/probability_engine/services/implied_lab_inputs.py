from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from src.engine.implied_distribution import build_distribution_chart_data


def build_implied_lab_market_data(
    *,
    expiry_ts_ms: float,
    spot_usd: float,
    cached_forward_iv: Callable[[float, float], dict[str, Any] | None],
    cached_marks_full: Callable[[float], dict[str, Any] | None],
    quote_cache_ttl_s: int,
) -> dict[str, Any]:
    """
    Assemble the implied-lab market inputs used by the UI.

    Notes:
    - Caching is intentionally external (callers pass cached_* wrappers).
    - Output shape matches the UI's existing `market_data` contract.
    """
    fwd_iv = cached_forward_iv(expiry_ts_ms, spot_usd)
    forward = (fwd_iv.get("forward") or spot_usd) if fwd_iv else spot_usd
    vol = (fwd_iv.get("atm_iv") or 0.6) if fwd_iv else 0.6
    if vol <= 0:
        vol = 0.6

    run_ts_utc = pd.Timestamp.now(tz="UTC")
    now_ts_ms = run_ts_utc.timestamp() * 1000
    as_of_utc = run_ts_utc.isoformat()

    T_years = max(0.0, (float(expiry_ts_ms) - float(now_ts_ms)) / 1000 / (365.25 * 24 * 3600))
    # Avoid degenerate near-zero T: use at least ~1 week so the bell is visible
    T_years = max(float(T_years), 0.02)

    price_min = max(1000, float(forward) * 0.4)
    price_max = float(forward) * 2.2

    dist = build_distribution_chart_data(
        forward=float(forward),
        vol_annual=float(vol),
        T_years=float(T_years),
        price_min=float(price_min),
        price_max=float(price_max),
        num_points=100,
    )

    marks_full = cached_marks_full(expiry_ts_ms) or {}
    call_marks = marks_full.get("calls") or []
    put_marks = marks_full.get("puts") or []

    avail_strikes = sorted(set(m["strike"] for m in call_marks + put_marks))
    call_by_k = {m["strike"]: float(m.get("mark_btc") or 0) for m in call_marks}
    put_by_k = {m["strike"]: float(m.get("mark_btc") or 0) for m in put_marks}

    return {
        "forward": float(forward),
        "vol": float(vol),
        "T_years": float(T_years),
        "price_min": float(price_min),
        "price_max": float(price_max),
        "dist": dist,
        "marks_full": marks_full,
        "call_marks": call_marks,
        "put_marks": put_marks,
        "avail_strikes": avail_strikes,
        "call_by_k": call_by_k,
        "put_by_k": put_by_k,
        "data_sources": [
            "Deribit (BTC index, forward, ATM IV, option marks)",
        ],
        "as_of_utc": as_of_utc,
        "quote_cache_ttl_s": int(quote_cache_ttl_s),
    }

