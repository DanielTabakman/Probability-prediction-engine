"""Unit tests for forward consistency engine (bid/ask parity)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from src.data.forward_consistency_quotes import (
    ForwardConsistencyHeatmapCell,
    build_forward_consistency_dashboard,
    dashboard_payload_to_dict,
    summarize_forward_consistency_cells,
)
from src.engine.forward_consistency import (
    ForwardConsistencyConfig,
    ForwardConsistencyQualityFlag,
    FutureLegQuote,
    OptionLegQuote,
    SyntheticForwardRow,
    check_forward_consistency,
    compute_synthetic_forward_rows,
    derive_quality_flags,
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
        config=ForwardConsistencyConfig(max_synthetic_width_usd=5000.0, min_reliable_strikes=1),
    )
    assert check.best_strike == 101_000.0


def test_derive_stale_quotes_flag() -> None:
    now_ms = 1_700_000_000_000
    quotes = [
        OptionLegQuote(
            strike=100_000.0,
            call_bid=0.01,
            call_ask=0.011,
            put_bid=0.008,
            put_ask=0.009,
            quote_ts_ms=now_ms - 500_000,
        ),
    ]
    future = FutureLegQuote(
        instrument_name="BTC-TEST",
        bid=100_000.0,
        ask=100_050.0,
        quote_ts_ms=now_ms - 1_000,
    )
    rows = compute_synthetic_forward_rows(quotes, premium_in_usd=False, forward_usd=100_000.0)
    cfg = ForwardConsistencyConfig(max_quote_age_ms=60_000, min_reliable_strikes=1)
    flags = derive_quality_flags(
        option_quotes=quotes,
        future=future,
        all_rows=rows,
        reliable_rows=rows,
        config=cfg,
        now_ms=now_ms,
    )
    assert ForwardConsistencyQualityFlag.STALE_QUOTES in flags


def test_derive_wide_spread_flag_when_all_rows_filtered() -> None:
    quotes = [_quote(100_000.0, cb=0.05, ca=0.08, pb=0.04, pa=0.07)]
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=100_000.0, ask=100_050.0)
    rows = compute_synthetic_forward_rows(quotes, premium_in_usd=False, forward_usd=100_000.0)
    cfg = ForwardConsistencyConfig(max_synthetic_width_usd=100.0, min_reliable_strikes=1)
    reliable = filter_reliable_synthetic_rows(rows, cfg)
    flags = derive_quality_flags(
        option_quotes=quotes,
        future=future,
        all_rows=rows,
        reliable_rows=reliable,
        config=cfg,
    )
    assert ForwardConsistencyQualityFlag.WIDE_SPREAD in flags
    assert ForwardConsistencyQualityFlag.INSUFFICIENT_DEPTH in flags


def test_derive_missing_leg_and_expiry_mismatch_flags() -> None:
    quotes = [
        OptionLegQuote(
            strike=100_000.0,
            call_bid=0.01,
            call_ask=0.011,
            put_bid=None,
            put_ask=0.009,
        ),
    ]
    future = FutureLegQuote(
        instrument_name="BTC-TEST",
        bid=100_000.0,
        ask=100_050.0,
        expiry_ts_ms=1_800_000_000_000,
    )
    flags = derive_quality_flags(
        option_quotes=quotes,
        future=future,
        all_rows=[],
        reliable_rows=[],
        config=ForwardConsistencyConfig(min_reliable_strikes=1),
        expected_expiry_ts_ms=1_700_000_000_000,
    )
    assert ForwardConsistencyQualityFlag.MISSING_LEG in flags
    assert ForwardConsistencyQualityFlag.EXPIRY_MISMATCH in flags


def test_run_check_attaches_quality_flags() -> None:
    now_ms = 1_700_000_000_000
    quotes = [
        OptionLegQuote(
            strike=100_000.0,
            call_bid=0.01,
            call_ask=0.011,
            put_bid=0.008,
            put_ask=0.009,
            quote_ts_ms=now_ms - 500_000,
        ),
    ]
    future = FutureLegQuote(instrument_name="BTC-TEST", bid=100_000.0, ask=100_050.0)
    check = run_forward_consistency_check(
        quotes,
        future,
        premium_in_usd=False,
        forward_usd=100_000.0,
        config=ForwardConsistencyConfig(max_quote_age_ms=60_000, min_reliable_strikes=1),
        now_ms=now_ms,
    )
    assert ForwardConsistencyQualityFlag.STALE_QUOTES.value in [f.value for f in check.quality_flags]


def test_summarize_forward_consistency_cells() -> None:
    as_of = datetime.now(timezone.utc).isoformat()
    cells = [
        ForwardConsistencyHeatmapCell("BTC", "2026-07-25", "WATCH", 10.0, [], as_of),
        ForwardConsistencyHeatmapCell("BTC", "2026-08-29", "POSSIBLE_ARB", 50.0, [], as_of),
        ForwardConsistencyHeatmapCell("ETH", "2026-07-25", "BAD_DATA", None, ["MISSING_LEG"], as_of),
        ForwardConsistencyHeatmapCell("ETH", "2026-08-29", "NO_ARB", 0.0, [], as_of),
    ]
    summary = summarize_forward_consistency_cells(cells)
    assert summary == {
        "assets_checked": 2,
        "expiries_checked": 4,
        "watch_count": 1,
        "possible_count": 1,
        "bad_data_count": 1,
    }


def test_build_forward_consistency_dashboard_matrix() -> None:
    as_of = "2026-06-30T12:00:00+00:00"
    mock_cell_btc = ForwardConsistencyHeatmapCell(
        "BTC", "2026-07-25", "NO_ARB", 0.0, [], as_of
    )
    mock_cell_eth = ForwardConsistencyHeatmapCell(
        "ETH", "2026-07-25", "WATCH", 5.0, ["STALE_QUOTES"], as_of
    )

    with patch(
        "src.data.forward_consistency_quotes.list_enabled_asset_ids",
        return_value=["BTC", "ETH"],
    ), patch(
        "src.data.forward_consistency_quotes.list_forward_consistency_expiries",
        side_effect=lambda aid, **_: ["2026-07-25"] if aid in ("BTC", "ETH") else [],
    ), patch(
        "src.data.forward_consistency_quotes.build_forward_consistency_matrix_cell",
        side_effect=lambda asset_id, **_: mock_cell_btc if asset_id == "BTC" else mock_cell_eth,
    ):
        payload = build_forward_consistency_dashboard(as_of_utc=as_of)

    doc = dashboard_payload_to_dict(payload)
    assert doc["kind"] == "forward_consistency_dashboard"
    assert doc["schema_version"] == 1
    assert doc["summary"]["assets_checked"] == 2
    assert doc["summary"]["expiries_checked"] == 2
    assert doc["summary"]["watch_count"] == 1
    assert len(doc["cells"]) == 2
    assert doc["cells"][0]["asset_id"] == "BTC"
    assert doc["cells"][1]["quality_flags"] == ["STALE_QUOTES"]
