"""Tests for research summary rollup."""

from __future__ import annotations

import json
from pathlib import Path

from src.viz.cross_venue_export import serialize_cross_venue_export_csv
from src.viz.research_summary import build_research_summary, write_research_summary


def _row(*, as_of: str) -> dict[str, str]:
    return {
        "as_of_utc": as_of,
        "question": "Will Bitcoin hit $100k?",
        "strike_usd": "100000.00",
        "resolution_date": "2026-06-01",
        "matched_expiry_date": "2026-05-15",
        "horizon_days": "30",
        "expiry_alignment": "before_resolution",
        "polymarket_yes_pct": "40.00",
        "options_ln_p_above_pct": "50.00",
        "options_bl_p_above_pct": "55.00",
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


def test_build_research_summary_includes_cross_venue(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "research_pipeline_registry.json").write_text(
        (Path(__file__).resolve().parents[1] / "config" / "research_pipeline_registry.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    scan_dir = tmp_path / "artifacts" / "cross_venue_reports"
    scan_dir.mkdir(parents=True)
    scan_dir.joinpath("latest_summary.json").write_text(
        json.dumps({"row_count": 2, "entries": [{"abs_gap_pct": 11.0}]}),
        encoding="utf-8",
    )
    summary = build_research_summary(tmp_path)
    assert summary.get("cross_venue", {}).get("top_gap_pct") == 11.0
    out = write_research_summary(tmp_path)
    assert out.is_file()
