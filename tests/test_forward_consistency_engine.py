"""Unit tests for forward consistency engine (bid/ask parity)."""

from __future__ import annotations

from src.engine.forward_consistency import (
    ForwardConsistencyConfig,
    FutureLegQuote,
    OptionLegQuote,
    SyntheticForwardRow,
    check_forward_consistency,
    compute_synthetic_forward_rows,
    filter_reliable_synthetic_rows,
    run_forward_consistency_check,
)


def _quote(
    strike: float,
    *,
    cb: float = 0.01,
    ca: float = 0.011,
    pb: float = 0.008,
    pa: float = 0.009,
) -> OptionLegQuote:
    return OptionLegQuote(
        strike=strike,
        call_bid=cb,
        call_ask=ca,
        put_bid=pb,
        put_ask=pa,
    )


def test_no_arb_when_future_inside_synthetic_band() -> None:
    row = SyntheticForwardRow(
        strike=100_000.0,
        synthetic_bid=99_800.0,
        synthetic_ask=100_200.0,
        width_usd=400.0,
        call_bid=1000.0,
        call_ask=1100.0,
        put_bid=800.0,
        put_ask=900.0,
    )
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=99_900.0, ask=100_100.0)
    check = check_forward_consistency(row, future, ForwardConsistencyConfig())
    assert check.status == "NO_ARB"
    assert check.legs == []


def test_possible_arb_when_future_bid_exceeds_synthetic_ask_plus_costs() -> None:
    row = SyntheticForwardRow(
        strike=100_000.0,
        synthetic_bid=99_500.0,
        synthetic_ask=99_700.0,
        width_usd=200.0,
        call_bid=1000.0,
        call_ask=1100.0,
        put_bid=800.0,
        put_ask=900.0,
    )
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=100_500.0, ask=100_600.0)
    check = check_forward_consistency(
        row,
        future,
        ForwardConsistencyConfig(estimated_cost_bps=5.0, estimated_cost_floor_usd=10.0),
    )
    assert check.status == "POSSIBLE_ARB"
    assert check.direction == "SELL_FUTURE_BUY_SYNTHETIC"
    assert len(check.legs) == 3
    assert check.net_edge_usd is not None
    assert check.net_edge_usd > 0


def test_possible_arb_when_future_ask_below_synthetic_bid_minus_costs() -> None:
    row = SyntheticForwardRow(
        strike=100_000.0,
        synthetic_bid=100_400.0,
        synthetic_ask=100_600.0,
        width_usd=200.0,
        call_bid=1000.0,
        call_ask=1100.0,
        put_bid=800.0,
        put_ask=900.0,
    )
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=99_800.0, ask=99_900.0)
    check = check_forward_consistency(
        row,
        future,
        ForwardConsistencyConfig(estimated_cost_bps=5.0, estimated_cost_floor_usd=10.0),
    )
    assert check.status == "POSSIBLE_ARB"
    assert check.direction == "BUY_FUTURE_SELL_SYNTHETIC"


def test_ignores_missing_bids() -> None:
    quotes = [
        OptionLegQuote(strike=100_000.0, call_bid=0.01, call_ask=0.011, put_bid=None, put_ask=0.009),
        _quote(101_000.0),
    ]
    rows = compute_synthetic_forward_rows(quotes, premium_in_usd=False, forward_usd=100_000.0)
    assert len(rows) == 1
    assert rows[0].strike == 101_000.0


def test_ignores_crossed_invalid_synthetic_rows() -> None:
    quotes = [
        OptionLegQuote(
            strike=100_000.0,
            call_bid=0.001,
            call_ask=0.002,
            put_bid=0.08,
            put_ask=0.07,
        ),
    ]
    rows = compute_synthetic_forward_rows(quotes, premium_in_usd=False, forward_usd=100_000.0)
    assert rows == []


def test_ranks_tighter_rows_first() -> None:
    wide = SyntheticForwardRow(
        strike=100_000.0,
        synthetic_bid=99_000.0,
        synthetic_ask=100_500.0,
        width_usd=1500.0,
        call_bid=1.0,
        call_ask=2.0,
        put_bid=1.0,
        put_ask=2.0,
    )
    tight = SyntheticForwardRow(
        strike=101_000.0,
        synthetic_bid=100_800.0,
        synthetic_ask=100_900.0,
        width_usd=100.0,
        call_bid=1.0,
        call_ask=2.0,
        put_bid=1.0,
        put_ask=2.0,
    )
    ranked = filter_reliable_synthetic_rows(
        [wide, tight],
        ForwardConsistencyConfig(max_synthetic_width_usd=2000.0),
    )
    assert ranked[0].strike == 101_000.0


def test_run_check_picks_tightest_strike() -> None:
    quotes = [
        _quote(100_000.0, cb=0.02, ca=0.025, pb=0.015, pa=0.018),
        _quote(101_000.0, cb=0.01, ca=0.011, pb=0.008, pa=0.009),
    ]
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=100_000.0, ask=100_050.0)
    check = run_forward_consistency_check(
        quotes,
        future,
        premium_in_usd=False,
        forward_usd=100_000.0,
        config=ForwardConsistencyConfig(max_synthetic_width_usd=5000.0),
    )
    assert check.best_strike == 101_000.0
