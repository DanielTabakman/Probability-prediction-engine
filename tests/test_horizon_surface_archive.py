"""Tests for Options Horizon surface archive."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.collect_horizon_surface_snapshot import collect_horizon_surface_snapshot
from src.data.horizon_surface_archive import (
    archive_meta,
    build_surface_snapshot,
    default_snapshot_path,
    load_nearest_snapshot,
)


def test_default_snapshot_path_uses_utc_day_folder() -> None:
    ts = datetime(2026, 6, 26, 15, 30, 0, tzinfo=UTC)
    path = default_snapshot_path(as_of_utc=ts, root=Path("artifacts/horizon_surface_archive"))
    assert path.parent.name == "2026-06-26"
    assert path.name.startswith("horizon_surface_")


def test_collect_snapshot_writes_json(tmp_path: Path) -> None:
    exp_ts = 1893456000000

    def _spot() -> float:
        return 99_000.0

    def _expiries(_max: int) -> list[dict]:
        return [{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}]

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {
            "calls": [
                {"strike": 95_000.0, "mark_btc": 0.05},
                {"strike": 100_000.0, "mark_btc": 0.03},
                {"strike": 105_000.0, "mark_btc": 0.02},
            ]
        }

    out = tmp_path / "snap.json"
    written = collect_horizon_surface_snapshot(
        max_expiries=1,
        output=out,
        archive_root=tmp_path,
        spot_fn=_spot,
        expiries_fn=_expiries,
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now=datetime(2026, 6, 26, 12, 0, 0, tzinfo=UTC),
    )
    assert written == out
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["asset_id"] == "BTC"
    assert len(data["expiries"]) == 1
    assert data["expiries"][0]["call_ladder"]


def test_archive_meta_and_nearest_load(tmp_path: Path) -> None:
    day = tmp_path / "2026-06-25"
    day.mkdir(parents=True)
    snap = build_surface_snapshot(
        as_of_utc="2026-06-25T10:00:00+00:00",
        spot_usd=100_000.0,
        expiries=[{"expiry_ts": 1893456000000, "expiry_date_str": "2030-01-01"}],
        forward_iv_fn=lambda _e, _s: {"forward": 100_000.0, "atm_iv": 0.5},
        marks_full_fn=lambda _e: {"calls": [{"strike": 100_000.0, "mark_btc": 0.03}]},
        now_ms=datetime(2026, 6, 25, 10, 0, 0, tzinfo=UTC).timestamp() * 1000,
    )
    (day / "horizon_surface_100000Z.json").write_text(json.dumps(snap), encoding="utf-8")

    meta = archive_meta(tmp_path)
    assert meta["available_days"] == 1
    assert meta["replay_ready"] is False

    loaded = load_nearest_snapshot(tmp_path, as_of="2026-06-25T12:00:00Z")
    assert loaded is not None
    assert loaded["spot_usd"] == 100_000.0
