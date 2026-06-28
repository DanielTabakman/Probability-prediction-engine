"""Trust surface v1 — display payload trust_state contract."""

from __future__ import annotations

from src.data.fetch_equity_options import assess_equity_chain_trust, format_equity_trust_suffix
from src.viz.distribution_export import build_distribution_export_rows
from src.viz.distribution_summary_panel import (
    aggregate_trust_state,
    annotate_export_rows_trust,
    trust_state_from_export_row,
)
from src.viz.embed_display_boundary import build_distribution_display_payload


def _thin_chain_export_row() -> dict[str, str]:
    call_marks = [
        {"strike": 100.0, "mark_btc": 5.0, "open_interest": 10},
        {"strike": 105.0, "mark_btc": 3.0, "open_interest": 5},
    ]
    trust = assess_equity_chain_trust(call_marks)
    return {
        "asset": "NVDA",
        "distribution": "market_implied_bl",
        "expiry_date": "2030-06-21",
        "call_marks_count": str(len(call_marks)),
        "bl_status": f"computed_caution|{format_equity_trust_suffix(trust)}",
        "mean_usd": "150.00",
        "q25_usd": "130.00",
        "q50_usd": "145.00",
        "q75_usd": "160.00",
    }


def test_trust_state_from_export_row_thin_chain() -> None:
    row = _thin_chain_export_row()
    assert trust_state_from_export_row(row) == "thin_chain"


def test_trust_state_from_export_row_degraded_when_no_marks() -> None:
    row = {
        "distribution": "market_implied_bl",
        "bl_status": "skipped:insufficient_marks",
        "call_marks_count": "0",
    }
    assert trust_state_from_export_row(row) == "degraded"


def test_build_distribution_export_rows_annotates_insufficient_marks() -> None:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": [{"strike": 100_000.0, "mark_btc": 0.01}]}

    rows = build_distribution_export_rows(
        as_of_utc="2026-06-28T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
        asset_id="BTC",
    )
    bl = next(r for r in rows if r["distribution"] == "market_implied_bl")
    assert bl["trust_state"] == "thin_chain"


def test_display_payload_thin_chain_aggregate() -> None:
    row = annotate_export_rows_trust([_thin_chain_export_row()])[0]
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-28T12:00:00+00:00",
        spot_usd=150.0,
        export_rows=[row],
        asset_id="NVDA",
    )
    assert payload["trust_state"] == "thin_chain"
    assert payload["meta"]["trust_state"] == "thin_chain"


def test_aggregate_trust_state_thin_chain_wins_over_ok() -> None:
    rows = annotate_export_rows_trust(
        [
            {"distribution": "lognormal_reference", "bl_status": ""},
            _thin_chain_export_row(),
        ]
    )
    assert aggregate_trust_state(rows) == "thin_chain"
