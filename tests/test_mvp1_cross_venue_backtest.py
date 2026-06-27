"""Tests for cross-venue backtest scoring from snapshot history."""

from __future__ import annotations

from pathlib import Path

from src.viz.cross_venue_backtest import (
    brier_score_pct,
    build_cross_venue_backtest_report,
    gap_bucket_label,
    infer_resolved_outcome,
    merge_snapshot_history,
    render_cross_venue_backtest_markdown,
    score_question_series,
    serialize_cross_venue_backtest_json,
)
from src.viz.cross_venue_export import CSV_COLUMNS, serialize_cross_venue_export_csv


def _row(
    *,
    as_of: str,
    question: str = "Will Bitcoin hit $100k?",
    strike: str = "100000.00",
    resolution: str = "2026-06-01",
    pm: str = "40.00",
    bl: str = "55.00",
    gap: str = "15.00",
    spot: str = "105000.00",
) -> dict[str, str]:
    return {
        "as_of_utc": as_of,
        "question": question,
        "strike_usd": strike,
        "resolution_date": resolution,
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
        "spot_usd": spot,
        "forward_usd": "100500.00",
        "atm_iv_annual": "0.600000",
        "call_marks_count": "10",
        "match_status": "ok",
    }


def _write_snapshot(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_cross_venue_export_csv(rows), encoding="utf-8")


def test_brier_score_pct() -> None:
    assert brier_score_pct(100.0, 1) == 0.0
    assert brier_score_pct(0.0, 0) == 0.0
    assert brier_score_pct(50.0, 1) == 0.25


def test_gap_bucket_label() -> None:
    assert gap_bucket_label(1.5) == "0-2"
    assert gap_bucket_label(7.0) == "5-10"
    assert gap_bucket_label(12.0) == "10+"


def test_infer_resolved_outcome_from_spot_after_resolution() -> None:
    row = _row(as_of="2026-06-02T12:00:00+00:00", spot="105000.00")
    assert infer_resolved_outcome(row) == 1
    row_fail = _row(as_of="2026-06-02T12:00:00+00:00", spot="95000.00")
    assert infer_resolved_outcome(row_fail) == 0


def test_score_question_series() -> None:
    rows = [
        _row(as_of="2026-05-01T12:00:00+00:00", pm="40.00", bl="55.00", gap="15.00"),
        _row(as_of="2026-06-02T12:00:00+00:00", pm="99.00", bl="98.00", gap="1.00", spot="105000.00"),
    ]
    scored = score_question_series(rows)
    assert scored is not None
    assert scored["resolved_outcome"] == 1
    assert scored["gap_bucket"] == "10+"
    assert scored["brier_pm"] == 0.36
    assert scored["bl_beat_pm"] is True


def test_build_backtest_report_from_snapshots(tmp_path: Path) -> None:
    rows_template = [
        _row(as_of=f"2026-05-{day:02d}T12:00:00+00:00", pm="30.00", bl="45.00", gap="15.00")
        for day in range(1, 15)
    ]
    rows_template.append(
        _row(
            as_of="2026-06-02T12:00:00+00:00",
            pm="99.00",
            bl="98.00",
            gap="1.00",
            spot="105000.00",
        )
    )
    csv_path = tmp_path / "2026-05" / "ppe_cross_venue_prob_panel_120000Z.csv"
    _write_snapshot(csv_path, rows_template)

    report = build_cross_venue_backtest_report([csv_path], min_snapshots=14)
    assert report["resolved_count"] == 1
    assert report["mean_brier_pm"] is not None
    assert report["gap_buckets"]
    md = render_cross_venue_backtest_markdown(report)
    assert "# Cross-venue backtest report" in md
    payload = serialize_cross_venue_backtest_json(report)
    assert '"resolved_count": 1' in payload


def test_merge_snapshot_history_sorts_by_as_of(tmp_path: Path) -> None:
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    _write_snapshot(first, [_row(as_of="2026-05-02T12:00:00+00:00")])
    _write_snapshot(second, [_row(as_of="2026-05-01T12:00:00+00:00")])
    history = merge_snapshot_history([first, second])
    key = next(iter(history))
    assert history[key][0]["as_of_utc"].startswith("2026-05-01")


def test_csv_columns_contract() -> None:
    row = _row(as_of="2026-05-01T12:00:00+00:00")
    assert set(row.keys()) == set(CSV_COLUMNS)
