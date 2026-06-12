"""Tests for distribution stats snapshot collector script."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scripts.collect_distribution_stats_snapshot import (
    collect_distribution_stats_snapshot,
    default_snapshot_path,
)


def test_default_snapshot_path_uses_utc_day_folder() -> None:
    ts = datetime(2026, 6, 12, 15, 30, 0, tzinfo=UTC)
    path = default_snapshot_path(as_of_utc=ts, root=Path("artifacts/distribution_snapshots"))
    assert path.parent.name == "2026-06-12"
    assert path.name.startswith("ppe_btc_distribution_stats_")


def test_collect_snapshot_writes_csv(tmp_path: Path) -> None:
    exp_ts = 1893456000000

    def _spot() -> float:
        return 99_000.0

    def _expiries(_max: int) -> list[dict]:
        return [{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}]

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    out = tmp_path / "snapshot.csv"
    written = collect_distribution_stats_snapshot(
        max_expiries=1,
        output=out,
        spot_fn=_spot,
        expiries_fn=_expiries,
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now=datetime(2026, 6, 12, 12, 0, 0, tzinfo=UTC),
    )
    assert written == out
    text = out.read_text(encoding="utf-8")
    assert "q05_usd" in text.splitlines()[0]
    assert "lognormal_reference" in text
    assert "market_implied_bl" in text
