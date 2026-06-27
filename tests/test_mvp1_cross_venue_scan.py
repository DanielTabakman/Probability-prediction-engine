"""Tests for cross-venue scan ranking and report serialization."""

from __future__ import annotations

from src.viz.cross_venue_scan import (
    build_cross_venue_scan_report,
    rank_cross_venue_rows,
    render_cross_venue_scan_markdown,
    serialize_cross_venue_scan_json,
)


def _sample_row(
    *,
    question: str,
    gap: str,
    as_of: str = "2026-06-27T12:00:00+00:00",
) -> dict[str, str]:
    return {
        "as_of_utc": as_of,
        "question": question,
        "strike_usd": "100000.00",
        "resolution_date": "2026-12-31",
        "polymarket_yes_pct": "50.00",
        "options_bl_p_above_pct": "55.00",
        "gap_bl_minus_pm_pct": gap,
        "match_status": "ok",
    }


def test_rank_cross_venue_rows_orders_by_abs_gap() -> None:
    rows = [
        _sample_row(question="small", gap="2.00"),
        _sample_row(question="large", gap="-10.00"),
        _sample_row(question="medium", gap="5.00"),
        _sample_row(question="missing", gap=""),
    ]
    ranked = rank_cross_venue_rows(rows)
    assert [r["question"] for r in ranked] == ["large", "medium", "small"]


def test_build_cross_venue_scan_report_caps_rows() -> None:
    rows = [
        _sample_row(question=f"q{i}", gap=f"{i}.00") for i in range(1, 6)
    ]
    report = build_cross_venue_scan_report(rows, max_rows=3)
    assert report["row_count"] == 3
    assert report["entries"][0]["rank"] == 1
    assert report["entries"][-1]["question"] == "q3"


def test_render_and_serialize_scan_report() -> None:
    report = build_cross_venue_scan_report([_sample_row(question="BTC 100k", gap="7.50")])
    md = render_cross_venue_scan_markdown(report)
    assert "# Cross-venue scan report" in md
    assert "BTC 100k" in md
    payload = serialize_cross_venue_scan_json(report)
    assert '"row_count": 1' in payload
