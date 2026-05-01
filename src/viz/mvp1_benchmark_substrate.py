"""
MVP1 Phase 1 — market + benchmark substrate (explicit benchmark ID/version + width at horizon).

Numerics stay free of Streamlit. Breeden–Litzenberger gate matches implied_lab_derive /
build_verification_payload (len(call_marks) >= 3).
"""

from __future__ import annotations

import math
from typing import Any

# Frozen contract identifiers for Phase 1 substrate (bump version when semantics change).
MVP1_BENCHMARK_ID = "ppe_mvp1_lognormal_atm_iv"
MVP1_BENCHMARK_VERSION = "1.0.0"


def _sigma_ln_atm_horizon(vol_annual: float, T_years: float) -> float:
    v = max(0.0, float(vol_annual))
    T = max(0.0, float(T_years))
    return float(v * math.sqrt(max(T, 1e-12)))


def _empirical_sigma_ln_under_pdf(prices: list[float], f_raw: list[float]) -> float | None:
    """
    Trapezoid-normalized density on the price grid; return stdev of ln(price) using segment midpoints.
    """
    if len(prices) < 2 or len(f_raw) != len(prices):
        return None
    if max(abs(float(x)) for x in f_raw) <= 1e-20:
        return None

    area = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        area += 0.5 * (float(f_raw[i]) + float(f_raw[i + 1])) * dx
    if area <= 0 or math.isnan(area) or math.isinf(area):
        return None

    eln = 0.0
    eln2 = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        w = 0.5 * (float(f_raw[i]) / area + float(f_raw[i + 1]) / area) * dx
        mid = 0.5 * (float(prices[i]) + float(prices[i + 1]))
        lm = math.log(max(mid, 1e-12))
        eln += w * lm
        eln2 += w * lm * lm
    var = max(0.0, eln2 - eln * eln)
    out = math.sqrt(var)
    if math.isnan(out) or math.isinf(out):
        return None
    return float(out)


def build_mvp1_benchmark_substrate(
    *,
    market_data: dict[str, Any],
    market_pdf_raw: list[float],
    call_marks: list[Any],
) -> dict[str, Any]:
    """
    Single structured block for UI + trust: benchmark identity, widths on shared horizon T,
    and honest degraded handling when Breeden is skipped or empirical width is unusable.
    """
    dist = market_data.get("dist") or {}
    prices: list[float] = dist.get("prices") or []

    vol = float(market_data.get("vol") or 0.0)
    T_years = float(market_data.get("T_years") or 0.0)
    sigma_atm = _sigma_ln_atm_horizon(vol, T_years)

    call_n = len(call_marks)
    breeden_gate = call_n >= 3

    empirical: float | None = None
    empirical_status = "skipped"
    empirical_skip_reason: str | None = None
    if not breeden_gate:
        empirical_skip_reason = (
            "Fewer than 3 call marks at this expiry — no Breeden–Litzenberger density; "
            "empirical market-implied width is not computed."
        )
    elif not market_pdf_raw or len(market_pdf_raw) != len(prices):
        empirical_skip_reason = "Market-implied raw density missing or length mismatch vs grid."
    else:
        empirical = _empirical_sigma_ln_under_pdf(prices, market_pdf_raw)
        if empirical is None:
            empirical_skip_reason = "Empirical σ_ln under market-implied PDF was not usable on this grid."
        else:
            empirical_status = "computed"

    degraded = (not breeden_gate) or (empirical_status != "computed")
    if empirical_status != "computed" and breeden_gate:
        degraded = True

    if not degraded:
        trust_state = "ok"
        trust_note = (
            "Benchmark reference and ATM width are on the same horizon; Breeden–Litzenberger σ estimate "
            "on the pricing grid is available for comparison."
        )
    elif not breeden_gate:
        trust_state = "degraded"
        trust_note = (
            "Degraded: market-implied curve (orange) skipped — only ATM-quoted σ and the lognormal benchmark "
            "on the purple reference are fully anchored."
        )
    else:
        trust_state = "degraded"
        trust_note = (
            "Degraded: Breeden density ran but empirical width on the grid is missing — compare ATM and benchmark σ "
            "only; see Verification for details."
        )

    return {
        "benchmark_id": MVP1_BENCHMARK_ID,
        "benchmark_version": MVP1_BENCHMARK_VERSION,
        "horizon_years": float(T_years),
        "benchmark_definition": (
            "Black–Scholes lognormal terminal density on the chart grid using forward and ATM implied volatility "
            "(purple reference); MVP1 Phase 1 names this the explicit benchmark."
        ),
        "sigma_market_atm_ln": float(sigma_atm),
        "sigma_benchmark_ln": float(sigma_atm),
        "benchmark_sigma_note": (
            "Phase 1: benchmark width equals ATM σ·√T by contract — same inputs as the purple reference curve."
        ),
        "empirical_market_implied_sigma_ln": empirical,
        "empirical_status": empirical_status,
        "empirical_skip_reason": empirical_skip_reason,
        "call_marks_count": int(call_n),
        "trust_state": trust_state,
        "trust_state_note": trust_note,
    }
