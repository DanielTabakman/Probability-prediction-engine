"""Tests for cross-venue probability panel snapshot collector script."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scripts.collect_cross_venue_snapshot import (
    collect_cross_venue_snapshot,
    default_snapshot_path,
)
from src.viz.cross_venue_export import CSV_COLUMNS


def test_default_snapshot_path_uses_utc_day_folder() -> None:
    ts = datetime(2026, 6, 13, 15, 30, 0, tzinfo=UTC)
    path = default_snapshot_path(as_of_utc=ts, root=Path("artifacts/cross_venue_snapshots"))
    assert path.parent.name == "2026-06-13"
    assert path.name.startswith("ppe_cross_venue_prob_panel_")


def test_collect_snapshot_writes_csv(tmp_path: Path, monkeypatch) -> None:
    def _spot() -> float:
        return 99_000.0

    def _polymarket(_active: bool, _closed: bool, _limit: int) -> list[dict]:
        return [{"id": "evt-1"}]

    monkeypatch.setattr(
        "scripts.collect_cross_venue_snapshot._btc_questions_from_polymarket",
        lambda **_kwargs: [{"strike": 150_000, "resolution_date": "2026-12-31"}],
    )
    monkeypatch.setattr(
        "scripts.collect_cross_venue_snapshot.build_cross_venue_panel_rows",
        lambda **_kwargs: [
            {
                "as_of_utc": "2026-06-13T12:00:00+00:00",
                "question": "Will Bitcoin hit $150k?",
                "strike_usd": "150000.00",
                "resolution_date": "2026-12-31",
                "matched_expiry_date": "2026-06-27",
                "horizon_days": "201",
                "expiry_alignment": "before_resolution",
                "polymarket_yes_pct": "12.50",
                "options_ln_p_above_pct": "15.00",
                "options_bl_p_above_pct": "18.00",
                "gap_bl_minus_pm_pct": "5.50",
                "gap_ln_minus_pm_pct": "2.50",
                "spread_cost_usd": "1200.00",
                "spread_proxy_prob_pct": "8.00",
                "spot_usd": "99000.00",
                "forward_usd": "100000.00",
                "atm_iv_annual": "0.620000",
                "call_marks_count": "12",
                "match_status": "ok",
            }
        ],
    )

    out = tmp_path / "snapshot.csv"
    written = collect_cross_venue_snapshot(
        max_questions=1,
        output=out,
        spot_fn=_spot,
        polymarket_fn=_polymarket,
        now=datetime(2026, 6, 13, 12, 0, 0, tzinfo=UTC),
    )
    assert written == out
    text = out.read_text(encoding="utf-8")
    assert text.splitlines()[0] == ",".join(CSV_COLUMNS)
    assert "5.50" in text
