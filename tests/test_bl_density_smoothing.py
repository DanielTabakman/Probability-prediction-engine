"""Tests for Breeden-Litzenberger density smoothing (MVP1 bl_density_smoothing v1)."""

from __future__ import annotations

import math

from src.engine.implied_distribution import (
    _bl_density_from_calls,
    _integrate_density_trapezoid,
    market_implied_density_breeden_litzenberger,
    smooth_bl_density,
)


def _black_scholes_call(forward: float, strike: float, vol: float, T: float) -> float:
    if T <= 0 or vol <= 0 or forward <= 0 or strike <= 0:
        return max(0.0, forward - strike)
    sigma_sqrt_t = vol * math.sqrt(T)
    d1 = (math.log(forward / strike) + 0.5 * sigma_sqrt_t**2) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t
    nd1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2.0)))
    nd2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2.0)))
    return forward * nd1 - strike * nd2


def _price_grid(k_lo: float, k_hi: float, n: int = 80) -> list[float]:
    step = (k_hi - k_lo) / max(n - 1, 1)
    return [k_lo + i * step for i in range(n)]


def test_smooth_bl_density_integrates_to_one() -> None:
    prices = [80_000.0 + i * 1_000.0 for i in range(41)]
    pdf = [0.02 + 0.01 * math.sin(i * 0.4) for i in range(len(prices))]
    pdf[20] += 0.15
    smoothed = smooth_bl_density(prices, pdf)
    assert min(smoothed) >= 0.0
    area = _integrate_density_trapezoid(prices, smoothed)
    assert abs(area - 1.0) < 0.02


def test_smooth_bl_density_dampens_interior_spike() -> None:
    prices = [float(i) for i in range(30)]
    pdf = [0.04] * len(prices)
    pdf[15] = 0.45
    smoothed = smooth_bl_density(prices, pdf)
    assert smoothed[15] < pdf[15]
    assert max(smoothed) > 0.0


def test_bl_smoothed_noisy_calls_integrates_and_nonnegative() -> None:
    forward, vol, T = 100_000.0, 0.55, 0.25
    strikes = [70_000.0 + i * 5_000.0 for i in range(15)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    noisy = [c * (1.0 + 0.04 * math.sin(i * 1.7)) for i, c in enumerate(calls)]
    grid = _price_grid(65_000.0, 145_000.0)
    pdf = market_implied_density_breeden_litzenberger(strikes, noisy, grid)
    assert min(pdf) >= 0.0
    assert max(pdf) > 0.0
    area = _integrate_density_trapezoid(grid, pdf)
    assert abs(area - 1.0) < 0.08


def test_bl_smoothing_improves_mass_recovery_with_noise() -> None:
    forward, vol, T = 100_000.0, 0.5, 0.3
    strikes = [80_000.0 + i * 4_000.0 for i in range(12)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    noisy = [c * (1.0 + 0.07 * math.sin(i * 2.7)) for i, c in enumerate(calls)]
    grid = _price_grid(75_000.0, 130_000.0)
    raw_pdf = _normalize_via_bl(strikes, noisy, grid, apply_smoothing=False)
    smooth_pdf = market_implied_density_breeden_litzenberger(strikes, noisy, grid)
    raw_area = _integrate_density_trapezoid(grid, raw_pdf)
    smooth_area = _integrate_density_trapezoid(grid, smooth_pdf)
    assert abs(smooth_area - 1.0) <= abs(raw_area - 1.0) + 0.02
    assert max(smooth_pdf) > 0.0


def _normalize_via_bl(
    strikes: list[float],
    calls: list[float],
    grid: list[float],
    *,
    apply_smoothing: bool,
) -> list[float]:
    return market_implied_density_breeden_litzenberger(
        strikes,
        calls,
        grid,
        apply_smoothing=apply_smoothing,
    )


def test_bl_raw_path_available_for_toggle() -> None:
    forward, vol, T = 100_000.0, 0.5, 0.25
    strikes = [85_000.0 + i * 3_000.0 for i in range(9)]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    grid = _price_grid(80_000.0, 115_000.0)
    raw = market_implied_density_breeden_litzenberger(
        strikes, calls, grid, apply_smoothing=False
    )
    smoothed = market_implied_density_breeden_litzenberger(strikes, calls, grid)
    assert raw != smoothed or max(raw) == 0.0
    assert abs(_integrate_density_trapezoid(grid, raw) - 1.0) < 0.05


def test_bl_density_from_calls_matches_unsmoothed_pipeline() -> None:
    forward, vol, T = 100_000.0, 0.45, 0.2
    strikes = [90_000.0, 100_000.0, 110_000.0, 120_000.0, 130_000.0]
    calls = [_black_scholes_call(forward, k, vol, T) for k in strikes]
    grid = _price_grid(85_000.0, 135_000.0, n=40)
    from src.engine.implied_distribution import _normalize_density

    expected = _normalize_density(grid, _bl_density_from_calls(strikes, calls, grid))
    actual = market_implied_density_breeden_litzenberger(
        strikes, calls, grid, apply_smoothing=False
    )
    assert len(expected) == len(actual)
    assert all(abs(a - b) < 1e-12 for a, b in zip(actual, expected, strict=True))
