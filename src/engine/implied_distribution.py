"""
Implied probability distribution from options (lognormal model + market-implied via Breeden-Litzenberger).
Phase 1: lognormal. Phase 2: market-implied density + anomaly detection.
"""
from __future__ import annotations

import math
from typing import Any


def lognormal_pdf(
    forward: float,
    vol_annual: float,
    T_years: float,
    prices: list[float],
) -> list[float]:
    """
    Risk-neutral lognormal PDF at given price points.
    S_T = F * exp(-0.5*sigma^2*T + sigma*sqrt(T)*Z), Z~N(0,1).
    Returns density per 1 USD (so integral over range ≈ probability in that range).
    """
    if T_years <= 0 or vol_annual <= 0 or forward <= 0:
        return [0.0] * len(prices)
    sigma = vol_annual * math.sqrt(T_years)
    mu = math.log(forward) - 0.5 * sigma * sigma
    out = []
    for s in prices:
        if s <= 0:
            out.append(0.0)
            continue
        log_s = math.log(s)
        z = (log_s - mu) / sigma
        # pdf(s) = (1 / (s * sigma * sqrt(2*pi))) * exp(-0.5*z^2)
        density = (1.0 / (s * sigma * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * z * z)
        out.append(density)
    return out


def lognormal_cdf(
    forward: float,
    vol_annual: float,
    T_years: float,
    strike: float,
) -> float:
    """CDF at strike: P(S_T <= strike)."""
    if strike <= 0:
        return 0.0
    if T_years <= 0 or vol_annual <= 0 or forward <= 0:
        return 0.5
    sigma = vol_annual * math.sqrt(T_years)
    mu = math.log(forward) - 0.5 * sigma * sigma
    z = (math.log(strike) - mu) / sigma
    # Standard normal CDF via error function
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def probability_above_strike_lognormal(
    forward: float,
    vol_annual: float,
    T_years: float,
    strike: float,
) -> float:
    """Risk-neutral P(S_T > strike) under lognormal(forward, vol, T)."""
    return max(0.0, min(1.0, 1.0 - lognormal_cdf(forward, vol_annual, T_years, strike)))


def probability_above_strike_from_density(
    prices: list[float],
    pdf_raw: list[float],
    strike: float,
) -> float:
    """P(S > strike) via trapezoid integral of density on the price grid."""
    if len(prices) < 2 or len(pdf_raw) != len(prices):
        return 0.0
    area = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        area += 0.5 * (float(pdf_raw[i]) + float(pdf_raw[i + 1])) * dx
    if area <= 0:
        return 0.0
    above = 0.0
    for i in range(len(prices) - 1):
        p0 = float(prices[i])
        p1 = float(prices[i + 1])
        if p1 <= strike:
            continue
        f0 = float(pdf_raw[i]) / area
        f1 = float(pdf_raw[i + 1]) / area
        seg_lo = max(p0, strike)
        seg_hi = p1
        if seg_hi <= seg_lo:
            continue
        if seg_lo > p0 and p1 > p0:
            t = (seg_lo - p0) / (p1 - p0)
            f_lo = f0 + t * (f1 - f0)
        else:
            f_lo = f0
        above += 0.5 * (f_lo + f1) * (seg_hi - seg_lo)
    return max(0.0, min(1.0, above))


def build_distribution_chart_data(
    forward: float,
    vol_annual: float,
    T_years: float,
    price_min: float,
    price_max: float,
    num_points: int = 80,
) -> dict[str, Any]:
    """
    Build x (prices) and y (PDF as percentage) and optional cumulative at a few strikes.
    Returns dict: prices, pdf_pct, cumulative_at (list of (price, cdf_pct)).
    """
    step = (price_max - price_min) / max(num_points - 1, 1)
    prices = [price_min + i * step for i in range(num_points)]
    pdf = lognormal_pdf(forward, vol_annual, T_years, prices)
    # Normalize so peak is ~25% for IB-style 0-30% y-axis
    max_pdf = max(pdf) if pdf else 1.0
    pdf_pct = [(d / max_pdf * 25.0) if max_pdf > 0 else 0.0 for d in pdf]
    # Cumulative at a few points (for labels under axis)
    cumulative_at = []
    for p in [price_min, price_min + (price_max - price_min) * 0.25,
              price_min + (price_max - price_min) * 0.5,
              price_min + (price_max - price_min) * 0.75, price_max]:
        cdf = lognormal_cdf(forward, vol_annual, T_years, p)
        cumulative_at.append((p, cdf * 100.0))
    return {
        "prices": prices,
        "pdf_pct": pdf_pct,
        "pdf_raw": pdf,  # for anomaly comparison
        "cumulative_at": cumulative_at,
        "forward": forward,
        "vol_annual": vol_annual,
        "T_years": T_years,
    }


def market_implied_density_breeden_litzenberger(
    strikes: list[float],
    call_prices_usd: list[float],
    price_grid: list[float],
) -> list[float]:
    """
    Risk-neutral density from call prices via Breeden-Litzenberger: q(K) = d²C/dK² (r=0).
    strikes and call_prices_usd must be same length, sorted by strike.
    Returns density on price_grid; values clamped >= 0 and normalized to integrate to 1.
    """
    if len(strikes) < 3 or len(strikes) != len(call_prices_usd):
        return [0.0] * len(price_grid)
    n = len(strikes)
    # Second derivative at interior points
    q_at_strikes = [0.0] * n
    for i in range(1, n - 1):
        dk_plus = strikes[i + 1] - strikes[i]
        dk_minus = strikes[i] - strikes[i - 1]
        if dk_plus <= 0 or dk_minus <= 0:
            continue
        d2 = 2.0 * (
            (call_prices_usd[i + 1] - call_prices_usd[i]) / dk_plus
            - (call_prices_usd[i] - call_prices_usd[i - 1]) / dk_minus
        ) / (dk_plus + dk_minus)
        q_at_strikes[i] = max(0.0, d2)
    # Interpolate onto price_grid (linear in density)
    out = []
    for p in price_grid:
        if p <= strikes[0] or p >= strikes[-1]:
            out.append(0.0)
            continue
        for i in range(n - 1):
            if strikes[i] <= p <= strikes[i + 1]:
                t = (p - strikes[i]) / (strikes[i + 1] - strikes[i]) if strikes[i + 1] > strikes[i] else 0.0
                v = (1 - t) * q_at_strikes[i] + t * q_at_strikes[i + 1]
                out.append(max(0.0, v))
                break
        else:
            out.append(0.0)
    # Normalize so integral ~ 1
    step = (price_grid[-1] - price_grid[0]) / max(len(price_grid) - 1, 1)
    total = sum(out) * step
    if total > 0:
        out = [x / total for x in out]
    return out


def l2_distance_pdf(
    prices: list[float],
    pdf_a: list[float],
    pdf_b: list[float],
) -> float:
    """L2 distance between two PDFs on the same grid: sqrt(integral (a-b)^2)."""
    if len(prices) < 2 or len(prices) != len(pdf_a) or len(prices) != len(pdf_b):
        return 0.0
    step = (prices[-1] - prices[0]) / max(len(prices) - 1, 1)
    return math.sqrt(step * sum((a - b) ** 2 for a, b in zip(pdf_a, pdf_b)))


def is_anomalous(
    prices: list[float],
    lognormal_pdf: list[float],
    market_pdf: list[float],
    threshold: float = 0.02,
) -> bool:
    """True if L2 distance between lognormal and market-implied PDF exceeds threshold."""
    dist = l2_distance_pdf(prices, lognormal_pdf, market_pdf)
    return dist > threshold
