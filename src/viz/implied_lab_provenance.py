"""
Structured verification payload for the BTC implied options lab (Sprint: provenance first slice).

Builds a single dict consumed by app.py; no Streamlit dependency here.
"""

from __future__ import annotations

from typing import Any


def build_verification_payload(
    *,
    market_data: dict[str, Any],
    summary: dict[str, Any],
    strategy: dict[str, Any] | None,
    overlay: dict[str, Any],
    market_pdf_raw: list[float],
    call_marks: list[Any],
    belief_verification: dict[str, Any] | None,
    solve_error: str | None = None,
) -> dict[str, Any]:
    """
    Normalize verification fields for the current derive_lab_outputs run.

    Breeden–Litzenberger gate must match implied_lab_derive: len(call_marks) >= 3
    before calling market_implied_density_breeden_litzenberger.
    """
    dist = market_data.get("dist") or {}
    prices: list[float] = dist.get("prices") or []
    grid_n = len(prices)
    price_min = float(market_data.get("price_min") or (prices[0] if prices else 0.0))
    price_max = float(market_data.get("price_max") or (prices[-1] if prices else 0.0))

    forward = float(market_data.get("forward") or 0.0)
    vol = float(market_data.get("vol") or 0.0)
    T_years = float(market_data.get("T_years") or 0.0)

    data_sources = list(market_data.get("data_sources") or ["Deribit"])
    as_of_utc = str(market_data.get("as_of_utc") or "")
    cache_ttl = market_data.get("quote_cache_ttl_s")
    cache_ttl_s = int(cache_ttl) if cache_ttl is not None else None

    call_n = len(call_marks)
    breeden_gate = call_n >= 3
    breeden_status = "computed" if breeden_gate else "skipped"
    skip_reason: str | None = None
    if not breeden_gate:
        skip_reason = (
            "Fewer than 3 call option marks at this expiry — Breeden–Litzenberger "
            "is not run (same gate as the chart engine)."
        )

    summary_err = summary.get("error")
    err = solve_error or (summary_err if isinstance(summary_err, str) else None)
    has_strategy = strategy is not None and strategy.get("k1") is not None
    payoff_usd = overlay.get("payoff_usd") or []
    applicable = bool(has_strategy and payoff_usd)

    return {
        "data_sources": data_sources,
        "as_of_utc": as_of_utc,
        "snapshot_note": (
            "As-of is the run snapshot / valuation time used for this calculation "
            "(time to expiry, grid, and marks passed into the engine). "
            "It is not the native exchange timestamp on each individual quote packet."
        ),
        "quote_cache_ttl_s": cache_ttl_s,
        "cache_note": (
            f"Streamlit may cache Deribit REST responses for up to {cache_ttl_s} seconds — "
            "quotes can be slightly older than the as-of clock above."
            if cache_ttl_s is not None
            else "Cache TTL for quotes is not set on this run."
        ),
        "density": {
            "reference_risk_neutral": {
                "label": "Risk-neutral distribution (reference)",
                "description": (
                    "Lognormal density on the chart grid from forward and ATM implied volatility — "
                    "the purple reference curve."
                ),
                "method": "Black–Scholes lognormal terminal density on the discrete price grid",
                "forward_usd": forward,
                "atm_iv_annual": vol,
                "T_years": T_years,
                "grid_price_min_usd": price_min,
                "grid_price_max_usd": price_max,
                "grid_points": grid_n,
            },
            "market_implied": {
                "label": "Market-implied pricing distribution",
                "description": (
                    "Risk-neutral density from listed call prices via Breeden–Litzenberger "
                    "(orange curve when available)."
                ),
                "call_marks_count": call_n,
                "breeden_litzenberger": breeden_status,
                "skip_reason": skip_reason,
                "method_when_computed": "Breeden–Litzenberger (second derivative of call price w.r.t. strike)",
            },
        },
        "belief": belief_verification,
        "strategy_summary": {
            "applicable": applicable,
            "error": err,
            "values": {
                "name": summary.get("name"),
                "net_cost_usd": summary.get("cost_usd"),
                "debit_credit": summary.get("debit_credit"),
                "max_gain_usd": summary.get("max_gain"),
                "max_loss_usd": summary.get("max_loss"),
                "breakevens_usd": summary.get("breakevens"),
                "qty": strategy.get("qty") if strategy else None,
            },
            "calculation_notes": {
                "net_cost": (
                    "Net USD = Σ over legs: (long=+1 / short=−1) × put/call mark_btc(strike) × forward. "
                    "Positive = debit (pay), negative = credit (receive)."
                ),
                "max_gain_loss": (
                    "Max gain = max(qty × payoff on each grid point); max loss = min(qty × payoff). "
                    "Payoff at expiry uses the same piecewise definition as the green line."
                ),
                "breakevens": (
                    "Breakevens: points on the price grid where net P&L crosses zero — "
                    "found by linear interpolation between adjacent samples."
                ),
            },
        },
    }

