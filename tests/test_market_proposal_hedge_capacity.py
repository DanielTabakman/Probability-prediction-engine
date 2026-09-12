from __future__ import annotations

import copy
from pathlib import Path

import pytest

from src.engine.market_proposal_hedge_capacity import (
    MarketProposalError,
    adjacent_strikes,
    build_preview,
    build_preview_from_fixture,
    capacity_ladder,
    compute_cost_stack,
    payoff_ramp,
    render_markdown,
    select_proposed_threshold,
    to_dict,
)

FIXTURE_PATH = Path("fixtures/market_proposal_hedge_capacity/btc_terminal_v0.json")


def _fixture_data() -> dict:
    import json

    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_builds_shareable_preview_and_exports_schema() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)

    assert preview.schema_version == "MarketProposalHedgeCapacityPreviewV0"
    assert preview.readiness_state == "SHAREABLE_DESIGN"
    assert preview.threshold_adjustment == {
        "requested_threshold_usd": 93000.0,
        "proposed_threshold_usd": 95000.0,
        "threshold_delta_usd": 2000.0,
    }
    assert preview.yes_hedge.supported_payout_usd == 8000.0
    assert preview.no_hedge.supported_payout_usd == 6000.0
    assert "PREVIEW ONLY" in render_markdown(preview)
    assert to_dict(preview)["review_stop"].startswith("Preview only.")


def test_requested_threshold_is_not_silently_changed_and_strike_selection_is_deterministic() -> None:
    data = _fixture_data()
    selected = select_proposed_threshold(
        data["instruments"],
        "2026-09-25T08:00:00Z",
        data["requested_event"]["requested_threshold_usd"],
    )

    assert selected == 95000.0
    preview = build_preview(data)
    assert preview.requested_event.requested_threshold_usd == 93000.0
    assert preview.proposed_contract.proposed_threshold_usd == 95000.0
    assert "$95,000" in preview.proposed_contract.question
    assert "$93,000" not in preview.proposed_contract.question


def test_above_and_below_hedge_side_mapping_uses_expected_option_types() -> None:
    above = build_preview(_fixture_data())
    below_data = _fixture_data()
    below_data["requested_event"]["comparator"] = "below"
    below = build_preview(below_data)

    assert [leg.option_type for leg in above.yes_hedge.legs] == ["call", "call"]
    assert [leg.option_type for leg in above.no_hedge.legs] == ["put", "put"]
    assert [leg.option_type for leg in below.yes_hedge.legs] == ["put", "put"]
    assert [leg.option_type for leg in below.no_hedge.legs] == ["call", "call"]


def test_buy_uses_asks_sell_uses_bids_and_smaller_leg_limits_capacity() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)
    yes_long, yes_short = preview.yes_hedge.legs

    assert yes_long.action == "buy"
    assert yes_long.levels_consumed[0].price_btc == 0.055
    assert yes_short.action == "sell"
    assert yes_short.levels_consumed[0].price_btc == 0.032
    assert preview.yes_hedge.top_of_book_capacity_usd == 4000.0
    assert preview.yes_hedge.policy_capacity_usd == 9000.0
    assert preview.yes_hedge.capacity_levels[0].spread_amount == 0.8
    assert preview.yes_hedge.capacity_levels[1].spread_amount == 1.8


def test_slippage_policy_truncates_depth_capacity() -> None:
    data = _fixture_data()
    data["requested_event"]["max_slippage_bps"] = 100.0
    preview = build_preview(data)

    assert preview.yes_hedge.policy_capacity_usd == 4000.0
    assert len(preview.yes_hedge.legs[0].levels_consumed) == 1
    assert len(preview.yes_hedge.legs[1].levels_consumed) == 1


def test_multiplier_and_strike_width_normalize_capacity() -> None:
    data = _fixture_data()
    for row in data["instruments"]:
        row["contract_size"] = 0.5
    preview = build_preview(data)

    assert preview.yes_hedge.strike_width_usd == 5000.0
    assert preview.yes_hedge.policy_capacity_usd == 4500.0
    assert preview.yes_hedge.unsupported_payout_usd == 3500.0


def test_minimum_order_amount_rejects_below_min_trade_result() -> None:
    data = _fixture_data()
    for row in data["instruments"]:
        row["min_trade_amount"] = 5.0
    preview = build_preview(data)

    assert preview.readiness_state == "REVIEW_ONLY"
    assert "below_min_trade_amount" in preview.yes_hedge.flags
    assert "below_min_trade_amount" in preview.no_hedge.flags


def test_requested_supported_unsupported_reconcile_exactly() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)

    for side in (preview.yes_hedge, preview.no_hedge):
        assert side.supported_payout_usd + side.unsupported_payout_usd == side.requested_payout_usd
    assert preview.capacity_summary["unsupported_remainder_usd"] == 0.0


def test_option_fee_cap_and_reserves_are_separate_from_observed_premium() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)
    side = preview.yes_hedge

    assert side.observed_premium["net_observed_premium_btc"] == pytest.approx(0.0432526316)
    assert side.fees["option_fees_btc"] == pytest.approx(0.00108)
    assert side.fees["option_fees_usd"] == pytest.approx(99.36)
    assert side.reserves["legging_reserve_usd"] > 0
    assert side.reserves["settlement_currency_basis_reserve_usd"] > side.reserves["stale_sync_reserve_usd"]
    assert side.fees["prediction_venue_fees"] == "UNKNOWN_NOT_SELECTED"


def test_inverse_btc_conversion_disclosure_and_settlement_provenance() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)

    assert preview.settlement_spec["settlement_currency"] == "BTC"
    assert "BTC" in preview.settlement_spec["currency_basis"]
    assert "07:30 to 08:00 UTC" in preview.proposed_contract.resolution_language
    assert any("Inverse-Options" in url for url in preview.provenance["official_specification_references"])


def test_payoff_ramp_and_maximum_binary_mismatch_are_visible() -> None:
    ramp = payoff_ramp(90000.0, 95000.0, 95000.0)

    assert ramp.zero_payoff_region == "delivery <= $90,000"
    assert ramp.linear_ramp_region == "$90,000 < delivery < $95,000"
    assert ramp.full_payoff_region == "delivery >= $95,000"
    assert ramp.maximum_binary_replication_error_usd == 5000.0
    assert ramp.ramp_width_pct_of_threshold == pytest.approx(5.26315789)


def test_stale_or_timestamp_skew_rejects_to_review_only() -> None:
    data = _fixture_data()
    data["order_books"]["BTC-25SEP26-95000-C"]["timestamp_utc"] = "2026-07-19T01:31:30Z"
    preview = build_preview(data)

    assert preview.readiness_state == "SHAREABLE_DESIGN"
    assert preview.yes_hedge.status == "REVIEW_ONLY"
    assert "book_timestamp_skew_over_30s" in preview.yes_hedge.flags
    assert preview.no_hedge.status == "SUPPORTED"


def test_missing_or_crossed_book_rejects_side() -> None:
    missing = _fixture_data()
    missing["order_books"].pop("BTC-25SEP26-95000-C")
    missing_preview = build_preview(missing)

    assert missing_preview.yes_hedge.status == "NOT_SAFELY_HEDGEABLE"
    assert "Missing order book" in missing_preview.yes_hedge.flags[0]

    crossed = _fixture_data()
    crossed["order_books"]["BTC-25SEP26-90000-C"]["bids"] = [[0.06, 1.0]]
    crossed_preview = build_preview(crossed)
    assert crossed_preview.yes_hedge.status == "NOT_SAFELY_HEDGEABLE"
    assert "Crossed or locked book" in crossed_preview.yes_hedge.flags[0]


def test_one_sided_supported_result_remains_shareable_when_one_side_is_safe() -> None:
    data = _fixture_data()
    data["order_books"].pop("BTC-25SEP26-95000-P")
    preview = build_preview(data)

    assert preview.yes_hedge.status == "SUPPORTED"
    assert preview.no_hedge.status == "NOT_SAFELY_HEDGEABLE"
    assert preview.readiness_state == "SHAREABLE_DESIGN"


def test_all_readiness_states_are_reachable() -> None:
    review = _fixture_data()
    for row in review["instruments"]:
        row["min_trade_amount"] = 5.0
    assert build_preview(review).readiness_state == "REVIEW_ONLY"

    unsafe = _fixture_data()
    unsafe["order_books"] = {}
    assert build_preview(unsafe).readiness_state == "NOT_SAFELY_HEDGEABLE"


def test_capacity_ladder_and_cost_stack_are_pure() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)
    long_leg, short_leg = preview.yes_hedge.legs

    ladder = capacity_ladder(long_leg, short_leg, 5000.0, 2)
    cost = compute_cost_stack(
        long_leg=long_leg,
        short_leg=short_leg,
        spread_amount=1.8,
        current_index_usd=92000.0,
        reserve_policy={
            "legging_reserve_bps": 15.0,
            "stale_sync_reserve_bps": 10.0,
            "settlement_currency_basis_reserve_bps": 25.0,
        },
    )

    assert ladder[-1].capacity_usd == 9000.0
    assert cost.observed_premium_usd == pytest.approx(3979.2421052631585)


def test_no_network_fixture_render_and_export_contract() -> None:
    preview = build_preview_from_fixture(FIXTURE_PATH)
    rendered = render_markdown(preview)
    exported = to_dict(preview)

    assert "Market Proposal + Hedge Capacity Preview v0" in rendered
    assert "Download" not in rendered
    assert exported["requested_event"]["underlying"] == "BTC"
    assert exported["yes_hedge"]["legs"][0]["instrument_name"] == "BTC-25SEP26-90000-C"


def test_invalid_inputs_and_missing_settlement_metadata_fail_closed() -> None:
    data = _fixture_data()
    data["requested_event"]["underlying"] = "ETH"
    with pytest.raises(MarketProposalError, match="BTC only"):
        build_preview(data)

    data = _fixture_data()
    data["settlement_metadata"].pop("settlement_method")
    with pytest.raises(MarketProposalError, match="Settlement method"):
        build_preview(data)


def test_adjacent_strikes_require_bounds_around_threshold() -> None:
    data = _fixture_data()
    with pytest.raises(MarketProposalError, match="outside adjacent"):
        adjacent_strikes(data["instruments"], "2026-09-25T08:00:00Z", 200000.0)


def test_fixture_expected_values_match_actual_preview() -> None:
    data = _fixture_data()
    expected = data["expected"]
    preview = build_preview(copy.deepcopy(data))

    assert preview.proposed_contract.proposed_threshold_usd == expected["proposed_threshold_usd"]
    assert preview.yes_hedge.top_of_book_capacity_usd == expected["yes_top_of_book_capacity_usd"]
    assert preview.yes_hedge.policy_capacity_usd == expected["yes_policy_capacity_usd"]
    assert preview.no_hedge.top_of_book_capacity_usd == expected["no_top_of_book_capacity_usd"]
    assert preview.no_hedge.policy_capacity_usd == expected["no_policy_capacity_usd"]
    assert preview.readiness_state == expected["readiness_state"]
