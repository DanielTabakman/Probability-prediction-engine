"""
Implied probability distribution from options (lognormal model + market-implied via Breeden-Litzenberger).
Phase 1: lognormal. Phase 2: market-implied density + anomaly detection.

Agent: ppe-core math — no Streamlit; consumed by src/viz/ and tests only.
Tests: tests/test_implied*
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


def _standard_normal_ppf(p: float) -> float:
    """Inverse standard normal CDF for p in (0, 1) via bisection."""
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    lo, hi = -12.0, 12.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        cdf = 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0)))
        if cdf < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _lognormal_quantile(forward: float, vol_annual: float, T_years: float, p: float) -> float:
    """Terminal price quantile under risk-neutral lognormal."""
    if forward <= 0 or vol_annual <= 0 or T_years <= 0 or p <= 0.0:
        return 0.0
    if p >= 1.0:
        return float("inf")
    sigma = vol_annual * math.sqrt(T_years)
    mu = math.log(forward) - 0.5 * sigma * sigma
    z = _standard_normal_ppf(p)
    return math.exp(mu + sigma * z)


_QUANTILE_LEVELS: tuple[tuple[str, float], ...] = (
    ("q05_usd", 0.05),
    ("q10_usd", 0.10),
    ("q25_usd", 0.25),
    ("q50_usd", 0.50),
    ("q75_usd", 0.75),
    ("q90_usd", 0.90),
    ("q95_usd", 0.95),
)


def _empty_distribution_stats() -> dict[str, float]:
    return {"mean_usd": 0.0, **{key: 0.0 for key, _ in _QUANTILE_LEVELS}}


def lognormal_distribution_stats(
    forward: float,
    vol_annual: float,
    T_years: float,
) -> dict[str, float]:
    """
    Mean and quantiles for risk-neutral lognormal terminal distribution.
    Mean equals forward; q50 is the median terminal price.
    """
    if forward <= 0 or vol_annual <= 0 or T_years <= 0:
        return _empty_distribution_stats()
    return {
        "mean_usd": float(forward),
        **{
            key: _lognormal_quantile(forward, vol_annual, T_years, p)
            for key, p in _QUANTILE_LEVELS
        },
    }


def _integrate_density_trapezoid(prices: list[float], values: list[float]) -> float:
    if len(prices) < 2 or len(values) != len(prices):
        return 0.0
    total = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        total += 0.5 * (float(values[i]) + float(values[i + 1])) * dx
    return total


def _normalize_density(prices: list[float], pdf_raw: list[float]) -> list[float]:
    area = _integrate_density_trapezoid(prices, pdf_raw)
    if area <= 0:
        return [0.0] * len(pdf_raw)
    return [float(x) / area for x in pdf_raw]


def _density_cdf_at(prices: list[float], pdf_norm: list[float], strike: float) -> float:
    """P(S <= strike) on the price grid."""
    if len(prices) < 2 or len(pdf_norm) != len(prices):
        return 0.0
    if strike <= float(prices[0]):
        return 0.0
    if strike >= float(prices[-1]):
        return 1.0
    area = 0.0
    for i in range(len(prices) - 1):
        p0 = float(prices[i])
        p1 = float(prices[i + 1])
        if strike <= p0:
            break
        f0 = float(pdf_norm[i])
        f1 = float(pdf_norm[i + 1])
        if strike >= p1:
            area += 0.5 * (f0 + f1) * (p1 - p0)
            continue
        if p1 > p0:
            t = (strike - p0) / (p1 - p0)
            f_at = f0 + t * (f1 - f0)
            area += 0.5 * (f0 + f_at) * (strike - p0)
        break
    return max(0.0, min(1.0, area))


def _density_quantile(prices: list[float], pdf_norm: list[float], p: float) -> float:
    if not prices or p <= 0.0:
        return float(prices[0]) if prices else 0.0
    if p >= 1.0:
        return float(prices[-1])
    target = p
    for i in range(len(prices) - 1):
        p0 = float(prices[i])
        p1 = float(prices[i + 1])
        if p1 <= p0:
            continue
        cdf_lo = _density_cdf_at(prices, pdf_norm, p0)
        cdf_hi = _density_cdf_at(prices, pdf_norm, p1)
        if cdf_hi < target:
            continue
        if cdf_hi == cdf_lo:
            return p1
        t = (target - cdf_lo) / (cdf_hi - cdf_lo)
        return p0 + t * (p1 - p0)
    return float(prices[-1])


def density_distribution_stats(
    prices: list[float],
    pdf_raw: list[float],
) -> dict[str, float]:
    """
    Mean and quantiles from a density on a price grid (area-normalized internally).
    Mean is integral x·f(x) dx.
    """
    if len(prices) < 2 or len(pdf_raw) != len(prices):
        return _empty_distribution_stats()
    pdf_norm = _normalize_density(prices, pdf_raw)
    if max(pdf_norm) <= 0:
        return _empty_distribution_stats()
    mean = _integrate_density_trapezoid(
        prices,
        [float(prices[i]) * pdf_norm[i] for i in range(len(prices))],
    )
    return {
        "mean_usd": float(mean),
        **{
            key: _density_quantile(prices, pdf_norm, p)
            for key, p in _QUANTILE_LEVELS
        },
    }


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


def probability_above_strike_ladder_lognormal(
    forward: float,
    vol_annual: float,
    T_years: float,
    strikes_usd: list[float],
) -> list[dict[str, float]]:
    """P(S > K) for each strike under risk-neutral lognormal."""
    return [
        {
            "strike_usd": float(strike),
            "p_above": probability_above_strike_lognormal(
                forward, vol_annual, T_years, float(strike)
            ),
        }
        for strike in strikes_usd
    ]


def probability_above_strike_ladder_from_density(
    prices: list[float],
    pdf_raw: list[float],
    strikes_usd: list[float],
) -> list[dict[str, float]]:
    """P(S > K) for each strike via trapezoid integral on the price grid."""
    return [
        {
            "strike_usd": float(strike),
            "p_above": probability_above_strike_from_density(
                prices, pdf_raw, float(strike)
            ),
        }
        for strike in strikes_usd
    ]


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
