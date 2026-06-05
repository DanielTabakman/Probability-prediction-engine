"""Pointwise P(> strike) enrichments for Polymarket-aligned spread rows."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from src.engine.implied_distribution import (
    build_distribution_chart_data,
    market_implied_density_breeden_litzenberger,
    probability_above_strike_from_density,
    probability_above_strike_lognormal,
)


def enrich_prediction_spreads_pointwise(
    spreads: list[dict[str, Any]],
    *,
    current_spot: float,
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None],
    marks_full_fn: Callable[[int], dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Add lognormal_p_above_pct and options_chain_p_above_pct per spread row when data allows.
    """
    if not spreads:
        return spreads
    now_ms = datetime.now(tz=timezone.utc).timestamp() * 1000
    out: list[dict[str, Any]] = []
    for s in spreads:
        row = dict(s)
        target = float(row.get("target") or 0)
        exp_ts = row.get("expiry_ts")
        if target <= 0 or exp_ts is None:
            out.append(row)
            continue
        try:
            exp_ts_i = int(exp_ts)
        except (TypeError, ValueError):
            out.append(row)
            continue

        fwd_iv = forward_iv_fn(exp_ts_i, float(current_spot))
        forward = float((fwd_iv or {}).get("forward") or current_spot)
        vol = float((fwd_iv or {}).get("atm_iv") or 0.6)
        if vol <= 0:
            vol = 0.6
        T_years = max(0.02, (exp_ts_i - now_ms) / 1000 / (365.25 * 24 * 3600))

        row["lognormal_p_above_pct"] = (
            probability_above_strike_lognormal(forward, vol, T_years, target) * 100.0
        )

        marks = marks_full_fn(exp_ts_i) or {}
        call_marks = marks.get("calls") or []
        if len(call_marks) >= 3:
            price_min = max(1000, forward * 0.4)
            price_max = forward * 2.2
            dist = build_distribution_chart_data(
                forward=forward,
                vol_annual=vol,
                T_years=T_years,
                price_min=price_min,
                price_max=price_max,
                num_points=80,
            )
            prices = dist["prices"]
            strikes = [m["strike"] for m in call_marks]
            call_usd = [float(m.get("mark_btc") or 0.0) * forward for m in call_marks]
            market_pdf = market_implied_density_breeden_litzenberger(strikes, call_usd, prices)
            if market_pdf and max(market_pdf) > 1e-20:
                row["options_chain_p_above_pct"] = (
                    probability_above_strike_from_density(prices, market_pdf, target) * 100.0
                )
        out.append(row)
    return out
