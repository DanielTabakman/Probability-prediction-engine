"""Tests for implied distribution engine helpers."""

from __future__ import annotations

from src.engine.implied_distribution import (
    density_distribution_stats,
    lognormal_cdf,
    lognormal_distribution_stats,
    lognormal_pdf,
    probability_above_strike_ladder_from_density,
    probability_above_strike_ladder_lognormal,
    probability_above_strike_lognormal,
)


def test_lognormal_distribution_stats_mean_is_forward() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    stats = lognormal_distribution_stats(forward, vol, T)
    assert abs(stats["mean_usd"] - forward) < 1e-6


def test_lognormal_distribution_stats_quantiles_ordered() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    stats = lognormal_distribution_stats(forward, vol, T)
    ordered = [
        stats["q05_usd"],
        stats["q10_usd"],
        stats["q25_usd"],
        stats["q50_usd"],
        stats["q75_usd"],
        stats["q90_usd"],
        stats["q95_usd"],
    ]
    assert ordered == sorted(ordered)
    assert abs(lognormal_cdf(forward, vol, T, stats["q50_usd"]) - 0.5) < 0.02


def test_density_distribution_stats_symmetric_grid() -> None:
    prices = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
    pdf = lognormal_pdf(100_000.0, 0.5, 0.25, prices)
    stats = density_distribution_stats(prices, pdf)
    ordered = [
        stats["q05_usd"],
        stats["q10_usd"],
        stats["q25_usd"],
        stats["q50_usd"],
        stats["q75_usd"],
        stats["q90_usd"],
        stats["q95_usd"],
    ]
    assert ordered == sorted(ordered)
    assert stats["mean_usd"] > 0


def test_probability_above_strike_lognormal_complement() -> None:
    forward, vol, T, strike = 100_000.0, 0.6, 0.25, 110_000.0
    p_below = lognormal_cdf(forward, vol, T, strike)
    p_above = probability_above_strike_lognormal(forward, vol, T, strike)
    assert abs((p_below + p_above) - 1.0) < 1e-9


def test_probability_above_strike_ladder_lognormal_monotone() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    strikes = [80_000.0, 100_000.0, 120_000.0]
    ladder = probability_above_strike_ladder_lognormal(forward, vol, T, strikes)
    assert [row["strike_usd"] for row in ladder] == strikes
    probs = [row["p_above"] for row in ladder]
    assert probs == sorted(probs, reverse=True)


def test_probability_above_strike_ladder_from_density() -> None:
    prices = [80_000.0, 100_000.0, 120_000.0]
    pdf = lognormal_pdf(100_000.0, 0.5, 0.25, prices)
    ladder = probability_above_strike_ladder_from_density(prices, pdf, [90_000.0, 110_000.0])
    assert len(ladder) == 2
    assert ladder[0]["p_above"] > ladder[1]["p_above"]
