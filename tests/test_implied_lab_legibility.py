"""Legibility copy contracts for implied lab probability methods."""
from __future__ import annotations

from src.engine.implied_distribution import (
    lognormal_cdf,
    probability_above_strike_from_density,
    probability_above_strike_lognormal,
)
from src.viz.implied_lab_legibility import (
    COL_PREDICTION_MARKET,
    COL_SPREAD_PROXY,
    TRACE_MODEL_BELL,
    TRACE_OPTIONS_CHAIN,
    TRACE_USER_BELIEF,
    YAXIS_DENSITY_TITLE,
    contains_forbidden_phrase,
)
from src.viz.prediction_spread_probs import enrich_prediction_spreads_pointwise


def test_trace_labels_are_method_explicit() -> None:
    assert "lognormal" in TRACE_MODEL_BELL.lower()
    assert "Breeden" in TRACE_OPTIONS_CHAIN
    assert "subjective" in TRACE_USER_BELIEF.lower()
    assert "Density" in YAXIS_DENSITY_TITLE
    assert "direct" in COL_PREDICTION_MARKET.lower()
    assert "proxy" in COL_SPREAD_PROXY.lower()


def test_forbidden_phrases_guard() -> None:
    assert contains_forbidden_phrase("What the market truly believes")
    assert not contains_forbidden_phrase("Market-implied pricing distribution")


def test_probability_above_strike_lognormal_complement() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    strike = 110_000.0
    p_below = lognormal_cdf(forward, vol, T, strike)
    p_above = probability_above_strike_lognormal(forward, vol, T, strike)
    assert abs(p_above + p_below - 1.0) < 1e-9


def test_probability_above_strike_from_density_normalized() -> None:
    prices = [80_000.0, 100_000.0, 120_000.0]
    pdf = [0.2, 0.5, 0.3]
    p_above_100k = probability_above_strike_from_density(prices, pdf, 100_000.0)
    assert 0.0 < p_above_100k < 1.0


def test_enrich_prediction_spreads_pointwise_adds_lognormal() -> None:
    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    rows = enrich_prediction_spreads_pointwise(
        [{"target": 150_000.0, "expiry_ts": 1893456000000}],
        current_spot=100_000.0,
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
    )
    assert rows[0].get("lognormal_p_above_pct") is not None
