"""Implied probability mass in a price × time thesis region (Options Horizon)."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

from src.engine.implied_distribution import (
    build_distribution_chart_data,
    lognormal_cdf,
    market_implied_density_breeden_litzenberger,
)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def implied_mass_in_price_band_lognormal(
    *,
    forward_usd: float,
    atm_iv_annual: float,
    T_years: float,
    price_min_usd: float,
    price_max_usd: float,
) -> float:
    """Risk-neutral probability mass between price bounds at expiry (lognormal)."""
    lo = min(float(price_min_usd), float(price_max_usd))
    hi = max(float(price_min_usd), float(price_max_usd))
    if hi <= lo or forward_usd <= 0 or atm_iv_annual <= 0 or T_years <= 0:
        return 0.0
    cdf_hi = lognormal_cdf(forward_usd, atm_iv_annual, T_years, hi)
    cdf_lo = lognormal_cdf(forward_usd, atm_iv_annual, T_years, lo)
    return max(0.0, min(1.0, cdf_hi - cdf_lo)) * 100.0


def _mass_from_density_grid(
    prices: list[float],
    pdf: list[float],
    price_min_usd: float,
    price_max_usd: float,
) -> float:
    lo = min(float(price_min_usd), float(price_max_usd))
    hi = max(float(price_min_usd), float(price_max_usd))
    if not prices or len(prices) != len(pdf) or hi <= lo:
        return 0.0
    total = sum(pdf) or 1.0
    mass = 0.0
    for i, price in enumerate(prices):
        if lo <= float(price) <= hi:
            mass += float(pdf[i])
    return max(0.0, min(1.0, mass / total)) * 100.0


def compute_region_implied_mass(
    *,
    price_min_usd: float,
    price_max_usd: float,
    time_end_utc: str,
    expiry_ts: int,
    forward_usd: float,
    atm_iv_annual: float,
    T_years: float,
    call_ladder: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Implied % mass in price band for the linked expiry.
    Time window is informational in v1; mass uses expiry-linked distribution.
    """
    _ = _parse_utc(time_end_utc)
    method = "lognormal_reference"
    mass_pct = implied_mass_in_price_band_lognormal(
        forward_usd=forward_usd,
        atm_iv_annual=atm_iv_annual,
        T_years=T_years,
        price_min_usd=price_min_usd,
        price_max_usd=price_max_usd,
    )
    if call_ladder and len(call_ladder) >= 3:
        price_min = max(1000.0, forward_usd * 0.4)
        price_max = forward_usd * 2.2
        dist = build_distribution_chart_data(
            forward=forward_usd,
            vol_annual=max(atm_iv_annual, 0.01),
            T_years=max(T_years, 0.02),
            price_min=price_min,
            price_max=price_max,
            num_points=80,
        )
        prices = dist["prices"]
        strikes = [float(row["strike"]) for row in call_ladder]
        call_usd = [float(row.get("mark_usd") or 0) for row in call_ladder]
        market_pdf = market_implied_density_breeden_litzenberger(strikes, call_usd, prices)
        if market_pdf and max(market_pdf) > 1e-20:
            bl_mass = _mass_from_density_grid(prices, market_pdf, price_min_usd, price_max_usd)
            if math.isfinite(bl_mass):
                mass_pct = bl_mass
                method = "breeden_litzenberger"
    return {
        "implied_mass_pct": round(mass_pct, 2),
        "method": method,
        "linked_expiry_ts": int(expiry_ts),
    }
