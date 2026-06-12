"""MVP1 distribution quant research v2 — core quant depth witnesses."""

from __future__ import annotations

from src.engine.implied_distribution import (
    lognormal_cdf,
    lognormal_distribution_stats,
    probability_above_strike_ladder_lognormal,
)


def test_tail_quantiles_match_cdf_levels() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    stats = lognormal_distribution_stats(forward, vol, T)
    for key, level in (
        ("q05_usd", 0.05),
        ("q10_usd", 0.10),
        ("q90_usd", 0.90),
        ("q95_usd", 0.95),
    ):
        cdf_at_quantile = lognormal_cdf(forward, vol, T, stats[key])
        assert abs(cdf_at_quantile - level) < 0.02


def test_strike_ladder_covers_otm_and_itm() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    ladder = probability_above_strike_ladder_lognormal(
        forward,
        vol,
        T,
        [70_000.0, 100_000.0, 130_000.0],
    )
    by_strike = {row["strike_usd"]: row["p_above"] for row in ladder}
    assert by_strike[70_000.0] > by_strike[100_000.0] > by_strike[130_000.0]
    assert 0.0 < by_strike[100_000.0] < 1.0
