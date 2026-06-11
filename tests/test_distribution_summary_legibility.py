"""Distribution summary on-screen table legibility contracts."""

from __future__ import annotations

from src.viz.distribution_export import build_distribution_export_rows
from src.viz.distribution_summary_panel import (
    bl_status_display,
    build_distribution_summary_table_rows,
    distribution_method_label,
    summary_panel_contract,
)
from src.viz.implied_lab_legibility import (
    BL_STATUS_SKIPPED_INSUFFICIENT,
    DIST_COL_MEAN,
    DIST_COL_METHOD,
    DIST_COL_STATUS,
    DIST_METHOD_BL,
    DIST_METHOD_LOGNORMAL,
    DIST_SUMMARY_ANCHOR_ID,
    DIST_SUMMARY_TITLE,
)


def _sample_rows() -> list[dict[str, str]]:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    return build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )


def test_distribution_method_labels() -> None:
    assert DIST_METHOD_LOGNORMAL in distribution_method_label("lognormal_reference")
    assert DIST_METHOD_BL in distribution_method_label("market_implied_bl")


def test_bl_status_honest_skip() -> None:
    assert BL_STATUS_SKIPPED_INSUFFICIENT == bl_status_display(
        "skipped:insufficient_marks",
        distribution="market_implied_bl",
    )
    assert bl_status_display("", distribution="lognormal_reference") == ""


def test_summary_table_uses_plain_english_headers() -> None:
    rows = build_distribution_summary_table_rows(_sample_rows())
    assert len(rows) == 2
    assert rows[0][DIST_COL_METHOD] == DIST_METHOD_LOGNORMAL
    assert rows[0][DIST_COL_MEAN].startswith("$")
    assert rows[1][DIST_COL_STATUS] == BL_STATUS_SKIPPED_INSUFFICIENT
    assert rows[1][DIST_COL_MEAN] == "—"


def test_summary_panel_contract_anchor() -> None:
    contract = summary_panel_contract(_sample_rows())
    assert contract["anchor_id"] == DIST_SUMMARY_ANCHOR_ID
    assert contract["title"] == DIST_SUMMARY_TITLE
    assert contract["row_count"] == 2
