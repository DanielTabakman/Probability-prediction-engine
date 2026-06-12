"""MVP1 distribution quant research v2 — export and summary panel witnesses."""

from __future__ import annotations

from src.engine.implied_distribution import (
    density_distribution_stats,
    lognormal_distribution_stats,
    lognormal_pdf,
)
from src.viz.distribution_export import (
    CSV_COLUMNS,
    build_distribution_export_rows,
)
from src.viz.distribution_summary_panel import build_distribution_summary_table_rows
from src.viz.implied_lab_legibility import DIST_COL_BL_LN_GAP, DIST_COL_RANGE


def test_export_rows_include_tail_quantiles_and_iqr() -> None:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        strikes = [80_000.0, 100_000.0, 120_000.0]
        return {
            "calls": [{"strike": k, "mark_btc": 0.01} for k in strikes],
        }

    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )
    ln_row = rows[0]
    for col in ("q05_usd", "q10_usd", "q90_usd", "q95_usd", "iqr_usd"):
        assert col in CSV_COLUMNS
        assert ln_row[col]
    iqr = float(ln_row["iqr_usd"])
    q_spread = float(ln_row["q75_usd"]) - float(ln_row["q25_usd"])
    assert abs(iqr - q_spread) < 0.02


def test_bl_ln_mean_gap_on_computed_chain_row() -> None:
    prices = [80_000.0, 100_000.0, 120_000.0]
    pdf = lognormal_pdf(100_000.0, 0.5, 0.25, prices)
    bl_stats = density_distribution_stats(prices, pdf)
    ln_stats = lognormal_distribution_stats(100_000.0, 0.5, 0.25)
    gap = float(bl_stats["mean_usd"]) - float(ln_stats["mean_usd"])
    assert abs(gap) < 50_000.0


def test_summary_table_shows_iqr_and_bl_ln_gap_columns() -> None:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    export_rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )
    table_rows = build_distribution_summary_table_rows(export_rows)
    assert table_rows[0][DIST_COL_RANGE].startswith("$")
    assert table_rows[0][DIST_COL_BL_LN_GAP] == "—"
    assert table_rows[1][DIST_COL_BL_LN_GAP] == "—"
