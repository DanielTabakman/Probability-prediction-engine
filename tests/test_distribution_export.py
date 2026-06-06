"""Tests for distribution quantile helpers and CSV export."""

from __future__ import annotations

from src.engine.implied_distribution import (
    density_distribution_stats,
    lognormal_cdf,
    lognormal_distribution_stats,
    lognormal_pdf,
)
from src.viz.distribution_export import (
    CSV_COLUMNS,
    build_distribution_export_rows,
    serialize_distribution_export_csv,
)


def test_lognormal_distribution_stats_mean_is_forward() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    stats = lognormal_distribution_stats(forward, vol, T)
    assert abs(stats["mean_usd"] - forward) < 1e-6


def test_lognormal_distribution_stats_quartiles_ordered() -> None:
    forward, vol, T = 100_000.0, 0.6, 0.25
    stats = lognormal_distribution_stats(forward, vol, T)
    assert stats["q25_usd"] < stats["q50_usd"] < stats["q75_usd"]
    assert abs(lognormal_cdf(forward, vol, T, stats["q50_usd"]) - 0.5) < 0.02


def test_density_distribution_stats_symmetric_grid() -> None:
    prices = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
    pdf = lognormal_pdf(100_000.0, 0.5, 0.25, prices)
    stats = density_distribution_stats(prices, pdf)
    assert stats["q25_usd"] < stats["q50_usd"] < stats["q75_usd"]
    assert stats["mean_usd"] > 0


def test_build_distribution_export_rows_lognormal_and_skipped_bl() -> None:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )
    assert len(rows) == 2
    assert rows[0]["distribution"] == "lognormal_reference"
    assert rows[0]["mean_usd"]
    assert rows[1]["distribution"] == "market_implied_bl"
    assert rows[1]["bl_status"].startswith("skipped")


def test_serialize_distribution_export_csv_header() -> None:
    csv_text = serialize_distribution_export_csv(
        [
            {
                "as_of_utc": "2026-06-06T12:00:00+00:00",
                "asset": "BTC",
                "expiry_date": "2030-01-01",
                "T_years": "0.250000",
                "distribution": "lognormal_reference",
                "mean_usd": "100000.00",
                "q25_usd": "90000.00",
                "q50_usd": "98000.00",
                "q75_usd": "110000.00",
                "forward_usd": "100000.00",
                "atm_iv_annual": "0.600000",
                "spot_usd": "99000.00",
                "call_marks_count": "",
                "bl_status": "",
            }
        ]
    )
    header = csv_text.splitlines()[0]
    assert header == ",".join(CSV_COLUMNS)
