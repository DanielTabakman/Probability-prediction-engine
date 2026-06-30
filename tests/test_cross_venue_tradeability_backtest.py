"""Tests for tradeability backtest scoring."""

from __future__ import annotations

from pathlib import Path

from src.viz.cross_venue_export import serialize_cross_venue_export_csv
from src.viz.cross_venue_tradeability_backtest import build_cross_venue_tradeability_backtest_report


def _row(*, as_of: str, pm: str = "40.00", gap: str = "15.00", cost: str = "8.00") -> dict[str, str]:
    return {
        "as_of_utc": as_of,
        "question": "Will Bitcoin hit $100k?",
        "strike_usd": "100000.00",
        "resolution_date": "2026-06-01",
        "matched_expiry_date": "2026-05-15",
        "horizon_days": "30",
        "expiry_alignment": "before_resolution",
        "polymarket_yes_pct": pm,
        "options_ln_p_above_pct": "50.00",
        "options_bl_p_above_pct": "55.00",
        "gap_bl_minus_pm_pct": gap,
        "gap_ln_minus_pm_pct": "10.00",
        "spread_cost_usd": "1000.00",
        "spread_proxy_prob_pct": cost,
        "spot_usd": "105000.00",
        "forward_usd": "100500.00",
        "atm_iv_annual": "0.600000",
        "call_marks_count": "10",
        "match_status": "ok",
    }


def test_tradeability_backtest_scores_tradeable_resolved(tmp_path: Path) -> None:
    snap = tmp_path / "snap.csv"
    rows = [_row(as_of=f"2026-05-{d:02d}T12:00:00+00:00") for d in range(1, 15)]
    rows[-1] = {**rows[-1], "polymarket_yes_pct": "99.00", "gap_bl_minus_pm_pct": "1.00"}
    snap.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")
    report = build_cross_venue_tradeability_backtest_report([snap], min_snapshots=14)
    assert report["tradeable_resolved_count"] == 1
