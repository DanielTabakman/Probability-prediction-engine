"""Tests for run_cross_venue_scan operator script."""

from __future__ import annotations

from pathlib import Path

from scripts.run_cross_venue_scan import run_cross_venue_scan
from src.viz.cross_venue_export import serialize_cross_venue_export_csv


def _sample_row(*, question: str, gap: str) -> dict[str, str]:
    return {
        "as_of_utc": "2026-06-27T12:00:00+00:00",
        "question": question,
        "strike_usd": "100000.00",
        "resolution_date": "2026-12-31",
        "polymarket_yes_pct": "50.00",
        "options_bl_p_above_pct": "55.00",
        "gap_bl_minus_pm_pct": gap,
        "match_status": "ok",
    }


def test_run_cross_venue_scan_writes_reports(tmp_path: Path) -> None:
    rows = [_sample_row(question="big gap", gap="12.00"), _sample_row(question="small", gap="1.00")]
    report, md_path, json_path = run_cross_venue_scan(rows=rows, min_gap=2.0, report_root=tmp_path)
    assert report["row_count"] == 1
    assert "big gap" in md_path.read_text(encoding="utf-8")
    assert json_path.is_file()
