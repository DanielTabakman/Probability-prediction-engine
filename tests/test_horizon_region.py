"""Tests for Options Horizon region implied mass."""

from __future__ import annotations

from src.engine.horizon_region import (
    compute_region_implied_mass,
    implied_mass_in_price_band_lognormal,
)


def test_lognormal_mass_in_band() -> None:
    mass = implied_mass_in_price_band_lognormal(
        forward_usd=100_000.0,
        atm_iv_annual=0.5,
        T_years=0.25,
        price_min_usd=90_000.0,
        price_max_usd=110_000.0,
    )
    assert 0.0 < mass < 100.0


def test_compute_region_implied_mass() -> None:
    out = compute_region_implied_mass(
        price_min_usd=95_000.0,
        price_max_usd=105_000.0,
        time_end_utc="2026-12-31T00:00:00Z",
        expiry_ts=1893456000000,
        forward_usd=100_000.0,
        atm_iv_annual=0.5,
        T_years=0.25,
    )
    assert "implied_mass_pct" in out
    assert out["method"] == "lognormal_reference"
