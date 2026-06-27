"""Tests for multi-leg strategy scanner (engine layer)."""

from __future__ import annotations

from src.engine.strategy_scanner import (
    build_universal_strategy,
    name_universal_strategy,
    payoff_target_to_strikes,
    payoff_target_to_strikes_with_work,
    strategy_payoff_at_prices,
)


def _default_polarity() -> tuple[bool, bool, bool, bool]:
    return False, True, True, False


def test_name_universal_strategy_straddle_at_same_strike() -> None:
    long_k1, long_k2, long_k3, long_k4 = _default_polarity()
    assert name_universal_strategy(100_000, 100_000, 100_000, 100_000, long_k1, long_k2, long_k3, long_k4) == "Straddle"


def test_name_universal_strategy_strangle() -> None:
    long_k1, long_k2, long_k3, long_k4 = _default_polarity()
    assert name_universal_strategy(80_000, 80_000, 120_000, 120_000, long_k1, long_k2, long_k3, long_k4) == "Strangle"


def test_name_universal_strategy_iron_butterfly() -> None:
    long_k1, long_k2, long_k3, long_k4 = _default_polarity()
    assert name_universal_strategy(80_000, 100_000, 100_000, 120_000, long_k1, long_k2, long_k3, long_k4) == "Iron butterfly"


def test_name_universal_strategy_iron_condor() -> None:
    long_k1, long_k2, long_k3, long_k4 = _default_polarity()
    assert name_universal_strategy(80_000, 90_000, 110_000, 120_000, long_k1, long_k2, long_k3, long_k4) == "Iron condor"


def test_name_universal_strategy_short_straddle_non_default_polarity() -> None:
    assert name_universal_strategy(100_000, 100_000, 100_000, 100_000, True, False, False, True) == "Short straddle"


def test_name_universal_strategy_custom_four_leg() -> None:
    assert name_universal_strategy(80_000, 90_000, 110_000, 120_000, True, True, True, True) == "Custom 4-leg"


def test_build_universal_strategy_insufficient_strikes() -> None:
    out = build_universal_strategy(
        forward=100_000.0,
        marks_calls=[{"strike": 100_000, "mark_btc": 0.01}],
        marks_puts=[{"strike": 100_000, "mark_btc": 0.01}],
    )
    assert out["payoff_type"] == "universal_4leg"
    assert out["k1"] is None
    assert out["cost_usd"] == 0.0


def test_build_universal_strategy_picks_atm_and_wings() -> None:
    forward = 100_000.0
    strikes = [80_000.0, 100_000.0, 120_000.0]
    marks = [{"strike": k, "mark_btc": 0.01} for k in strikes]
    out = build_universal_strategy(forward, marks, marks)
    assert out["k1"] == 80_000.0
    assert out["k2"] == 100_000.0
    assert out["k3"] == 100_000.0
    assert out["k4"] == 120_000.0
    assert out["name"] == "Iron butterfly"
    assert out["long_k2"] is True
    assert out["long_k4"] is False


def test_build_universal_strategy_cost_usd_scales_with_forward() -> None:
    forward = 50_000.0
    strikes = [40_000.0, 50_000.0, 60_000.0]
    call_marks = [{"strike": 40_000, "mark_btc": 0.01}, {"strike": 50_000, "mark_btc": 0.03}, {"strike": 60_000, "mark_btc": 0.02}]
    put_marks = [{"strike": 40_000, "mark_btc": 0.02}, {"strike": 50_000, "mark_btc": 0.04}, {"strike": 60_000, "mark_btc": 0.01}]
    out = build_universal_strategy(forward, call_marks, put_marks)
    # Default polarity: -K1 put + K2 put + K3 call - K4 call (BTC marks)
    expected_cost_btc = -0.02 + 0.04 + 0.03 - 0.02
    assert abs(out["cost_usd"] - expected_cost_btc * forward) < 1e-6


def test_payoff_target_to_strikes_invalid_body_range() -> None:
    assert payoff_target_to_strikes(110_000, 100_000, 5_000, 5_000, [80_000, 100_000, 120_000]) is None
    assert payoff_target_to_strikes(100_000, 110_000, 5_000, 5_000, []) is None


def test_payoff_target_to_strikes_snaps_to_available_strikes() -> None:
    avail = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
    result = payoff_target_to_strikes(90_000, 110_000, 5_000, 5_000, avail)
    assert result is not None
    k1, k2, k3, k4 = result
    assert k1 <= k2 <= k3 <= k4
    assert k1 in avail and k4 in avail


def test_payoff_target_to_strikes_with_work_reports_validation_errors() -> None:
    strikes, work = payoff_target_to_strikes_with_work(110_000, 100_000, 1_000, 1_000, [90_000, 100_000])
    assert strikes is None
    assert work["valid"] is False
    assert "body_left" in work["error"]

    strikes, work = payoff_target_to_strikes_with_work(90_000, 110_000, -1, 1_000, [90_000, 100_000])
    assert strikes is None
    assert work["valid"] is False
    assert "wing payoff" in work["error"]


def test_payoff_target_to_strikes_with_work_success_payload() -> None:
    avail = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
    strikes, work = payoff_target_to_strikes_with_work(90_000, 110_000, 5_000, 5_000, avail)
    assert strikes is not None
    assert work["valid"] is True
    assert work["raw"]["k2"] == 90_000.0
    assert work["raw"]["k3"] == 110_000.0
    assert work["ordered"]["k1"] <= work["ordered"]["k2"]


def test_strategy_payoff_at_prices_subtracts_debit_cost() -> None:
    strategy = build_universal_strategy(
        forward=100_000.0,
        marks_calls=[
            {"strike": 80_000, "mark_btc": 0.01},
            {"strike": 100_000, "mark_btc": 0.02},
            {"strike": 120_000, "mark_btc": 0.01},
        ],
        marks_puts=[
            {"strike": 80_000, "mark_btc": 0.01},
            {"strike": 100_000, "mark_btc": 0.02},
            {"strike": 120_000, "mark_btc": 0.01},
        ],
    )
    atm_payoff = strategy_payoff_at_prices(strategy, [100_000.0])[0]
    assert atm_payoff == -strategy["cost_usd"]

    high_payoff = strategy_payoff_at_prices(strategy, [150_000.0])[0]
    # Long K3 call dominates at high spot vs ATM intrinsic-only body
    assert high_payoff > atm_payoff


def test_strategy_payoff_at_prices_unknown_type_returns_negative_cost() -> None:
    payoffs = strategy_payoff_at_prices({"payoff_type": "unknown", "cost_usd": 100.0}, [100_000.0])
    assert payoffs == [-100.0]
