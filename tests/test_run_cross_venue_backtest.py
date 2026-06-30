"""Tests for run_cross_venue_backtest operator script."""

from __future__ import annotations

from pathlib import Path

from scripts.run_cross_venue_backtest import run_cross_venue_backtest
from src.viz.cross_venue_export import serialize_cross_venue_export_csv


def _row(*, as_of: str) -> dict[str, str]:
    return {
        "as_of_utc": as_of,
        "question": "Will Bitcoin hit $100k?",
        "strike_usd": "100000.00",
        "resolution_date": "2026-06-01",
        "matched_expiry_date": "2026-05-15",
        "horizon_days": "30",
        "expiry_alignment": "before_resolution",
        "polymarket_yes_pct": "30.00",
        "options_ln_p_above_pct": "50.00",
        "options_bl_p_above_pct": "45.00",
        "gap_bl_minus_pm_pct": "15.00",
        "gap_ln_minus_pm_pct": "10.00",
        "spread_cost_usd": "1000.00",
        "spread_proxy_prob_pct": "8.00",
        "spot_usd": "105000.00",
        "forward_usd": "100500.00",
        "atm_iv_annual": "0.600000",
        "call_marks_count": "10",
        "match_status": "ok",
    }


def test_run_cross_venue_backtest_writes_reports(tmp_path: Path) -> None:
    snap_root = tmp_path / "snapshots"
    rows = [_row(as_of=f"2026-05-{day:02d}T12:00:00+00:00") for day in range(1, 15)]
    rows[-1] = {**rows[-1], "polymarket_yes_pct": "99.00", "options_bl_p_above_pct": "98.00", "gap_bl_minus_pm_pct": "1.00"}
    path = snap_root / "2026-05" / "ppe_cross_venue_prob_panel_120000Z.csv"
    path.parent.mkdir(parents=True)
    path.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")
    report, md_path, json_path = run_cross_venue_backtest(snapshot_root=snap_root, report_root=tmp_path / "out")
    assert report["resolved_count"] == 1
    assert report.get("strategy_ready") is True
    assert md_path.name == "latest_report.md" and json_path.name == "latest_summary.json"
