"""Tests for cross-venue probability panel export."""

from __future__ import annotations

from datetime import UTC, datetime

from src.viz.cross_venue_export import (
    CSV_COLUMNS,
    build_cross_venue_export_rows,
    build_cross_venue_panel_rows,
    expiry_alignment_label,
    gap_pct,
    horizon_days_label,
    match_status_for_spread,
    serialize_cross_venue_export_csv,
)


def test_gap_pct_subtracts_polymarket_from_options() -> None:
    assert gap_pct(62.0, 55.0) == 7.0
    assert gap_pct(None, 55.0) is None


def test_expiry_alignment_before_resolution() -> None:
    assert (
        expiry_alignment_label(
            matched_expiry_date="2026-06-27",
            resolution_date="2026-12-31",
        )
        == "before_resolution"
    )


def test_horizon_days_from_as_of() -> None:
    assert (
        horizon_days_label(
            as_of_utc="2026-06-01T12:00:00+00:00",
            resolution_date="2026-06-11",
        )
        == "10"
    )


def test_match_status_ok_when_bl_present() -> None:
    assert match_status_for_spread({"options_chain_p_above_pct": 40.0}) == "ok"
    assert match_status_for_spread({"lognormal_p_above_pct": 40.0}) == "ok_ln_only"
    assert match_status_for_spread({}) == "insufficient_data"


def test_build_cross_venue_export_rows_gap_columns() -> None:
    rows = build_cross_venue_export_rows(
        as_of_utc="2026-06-13T12:00:00+00:00",
        spot_usd=100_000.0,
        enriched_spreads=[
            {
                "question": "Will Bitcoin hit $150k by December 31, 2026?",
                "target": 150_000.0,
                "resolution_date": "2026-12-31",
                "expiry_date": __import__("datetime").datetime(2026, 6, 27),
                "polymarket_yes_pct": 12.5,
                "lognormal_p_above_pct": 15.0,
                "options_chain_p_above_pct": 18.0,
                "cost_usd": 1200.0,
                "approx_implied_prob_pct": 8.0,
                "forward_usd": 101_000.0,
                "atm_iv_annual": 0.62,
                "call_marks_count": 12,
            }
        ],
    )
    assert len(rows) == 1
    assert rows[0]["gap_bl_minus_pm_pct"] == "5.50"
    assert rows[0]["gap_ln_minus_pm_pct"] == "2.50"
    assert rows[0]["match_status"] == "ok"


def test_build_cross_venue_panel_rows_with_mocked_deribit(monkeypatch) -> None:
    expiry = datetime(2026, 6, 27, tzinfo=UTC)

    def _fake_spreads(**_kwargs):
        return [
            {
                "question": "Will Bitcoin hit $150k by December 31, 2026?",
                "target": 150_000.0,
                "resolution_date": "2026-12-31",
                "expiry_date": expiry,
                "expiry_ts": 1_800_000_000_000,
                "polymarket_yes_pct": 12.5,
            }
        ]

    def _fake_enrich(spreads, **_kwargs):
        return [
            {
                **spreads[0],
                "lognormal_p_above_pct": 15.0,
                "options_chain_p_above_pct": 18.0,
            }
        ]

    monkeypatch.setattr(
        "src.viz.cross_venue_export.fetch_deribit_spreads_around_predictions",
        _fake_spreads,
    )
    monkeypatch.setattr(
        "src.viz.cross_venue_export.enrich_prediction_spreads_pointwise",
        _fake_enrich,
    )

    rows = build_cross_venue_panel_rows(
        as_of_utc="2026-06-13T12:00:00+00:00",
        spot_usd=100_000.0,
        btc_questions=[{"strike": 150_000, "resolution_date": "2026-12-31"}],
        forward_iv_fn=lambda _exp_ts, _spot: {"forward": 101_000.0, "atm_iv": 0.62},
        marks_full_fn=lambda _exp_ts: {"calls": [{"strike": 150_000}] * 12},
    )
    assert len(rows) == 1
    assert rows[0]["gap_bl_minus_pm_pct"] == "5.50"
    assert rows[0]["call_marks_count"] == "12"


def test_serialize_cross_venue_export_csv_header() -> None:
    csv_text = serialize_cross_venue_export_csv(
        [
            {
                "as_of_utc": "2026-06-13T12:00:00+00:00",
                "question": "Will Bitcoin hit $150k?",
                "strike_usd": "150000.00",
                "resolution_date": "2026-12-31",
                "matched_expiry_date": "2026-06-27",
                "horizon_days": "201",
                "expiry_alignment": "before_resolution",
                "polymarket_yes_pct": "12.50",
                "options_ln_p_above_pct": "15.00",
                "options_bl_p_above_pct": "18.00",
                "gap_bl_minus_pm_pct": "5.50",
                "gap_ln_minus_pm_pct": "2.50",
                "spread_cost_usd": "1200.00",
                "spread_proxy_prob_pct": "8.00",
                "spot_usd": "100000.00",
                "forward_usd": "101000.00",
                "atm_iv_annual": "0.620000",
                "call_marks_count": "12",
                "match_status": "ok",
            }
        ]
    )
    assert csv_text.splitlines()[0] == ",".join(CSV_COLUMNS)
