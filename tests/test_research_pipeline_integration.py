"""Integration: fixture archive → scan + backtest + tradeability pipeline."""

from __future__ import annotations

from pathlib import Path

from scripts.run_cross_venue_backtest import run_cross_venue_backtest
from scripts.run_cross_venue_scan import run_cross_venue_scan
from scripts.run_cross_venue_tradeability import run_cross_venue_tradeability
from src.viz.cross_venue_export import serialize_cross_venue_export_csv


def _row(*, as_of: str, pm: str = "40.00", bl: str = "55.00", gap: str = "15.00") -> dict[str, str]:
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
        "options_bl_p_above_pct": bl,
        "gap_bl_minus_pm_pct": gap,
        "gap_ln_minus_pm_pct": "10.00",
        "spread_cost_usd": "1000.00",
        "spread_proxy_prob_pct": "8.00",
        "spot_usd": "105000.00",
        "forward_usd": "100500.00",
        "atm_iv_annual": "0.600000",
        "call_marks_count": "10",
        "match_status": "ok",
    }


def test_fixture_archive_full_research_pipeline(tmp_path: Path) -> None:
    snap_root = tmp_path / "snapshots"
    rows = [_row(as_of=f"2026-05-{day:02d}T12:00:00+00:00") for day in range(1, 15)]
    rows[-1] = {**rows[-1], "polymarket_yes_pct": "99.00", "gap_bl_minus_pm_pct": "1.00"}
    path = snap_root / "2026-05" / "ppe_cross_venue_prob_panel_120000Z.csv"
    path.parent.mkdir(parents=True)
    path.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")

    scan_report, _, _ = run_cross_venue_scan(rows=rows[-1:], report_root=tmp_path / "scan")
    assert scan_report.get("row_count", 0) >= 1

    bt_report, _, _ = run_cross_venue_backtest(
        snapshot_root=snap_root,
        report_root=tmp_path / "backtest",
        min_snapshots=14,
    )
    assert bt_report["resolved_count"] == 1
    assert bt_report["strategy_ready"] is True

    tr_report, _, _ = run_cross_venue_tradeability(
        rows=rows[-1:],
        report_root=tmp_path / "tradeability",
    )
    assert tr_report["scored_count"] == 1
