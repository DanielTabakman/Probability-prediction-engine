"""Compatibility tests for the daily distribution stats collector."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from scripts.collect_distribution_stats_snapshot import (
    RETENTION_MIN_DAYS,
    archive_meta,
    collect_distribution_stats_snapshot,
    default_snapshot_path,
)


def _write_snapshot(path: Path, as_of: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "as_of_utc,spot_usd,method\n"
        f"{as_of.isoformat()},100000,market_implied_bl\n",
        encoding="utf-8",
    )


def test_default_snapshot_path_uses_utc_day_folder() -> None:
    ts = datetime(2026, 6, 12, 23, 30, 0, tzinfo=UTC)
    path = default_snapshot_path(as_of_utc=ts, root=Path("artifacts/distribution_snapshots"))
    assert path.parent.name == "2026-06-12"
    assert path.name == "ppe_btc_distribution_stats_233000Z.csv"


def test_collect_snapshot_writes_csv(tmp_path: Path) -> None:
    exp_ts = 1893456000000

    out = tmp_path / "snapshot.csv"
    written = collect_distribution_stats_snapshot(
        max_expiries=1,
        output=out,
        spot_fn=lambda: 99_000.0,
        expiries_fn=lambda _max: [{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.6},
        marks_full_fn=lambda _exp: {"calls": []},
        now=datetime(2026, 6, 12, 12, 0, 0, tzinfo=UTC),
    )

    assert written == out
    text = out.read_text(encoding="utf-8")
    assert "q05_usd" in text.splitlines()[0]
    assert "lognormal_reference" in text
    assert "market_implied_bl" in text


def test_archive_meta_reports_replay_readiness_and_retention_floor(tmp_path: Path) -> None:
    start = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
    for offset in range(30):
        ts = start + timedelta(days=offset)
        _write_snapshot(
            tmp_path / ts.strftime("%Y-%m-%d") / f"ppe_btc_distribution_stats_{ts:%H%M%S}Z.csv",
            ts,
        )

    meta = archive_meta(tmp_path)

    assert meta["available_days"] == 30
    assert meta["snapshot_count"] == 30
    assert meta["replay_ready"] is True
    assert meta["replay_threshold_days"] == 30
    assert meta["retention_min_days"] == RETENTION_MIN_DAYS
    assert meta["earliest_utc"] == start.isoformat()
    assert meta["latest_utc"] == (start + timedelta(days=29)).isoformat()


def test_archive_meta_ignores_unreadable_snapshot_dates(tmp_path: Path) -> None:
    day_dir = tmp_path / "2026-01-01"
    day_dir.mkdir()
    (day_dir / "ppe_btc_distribution_stats_080000Z.csv").write_text(
        "as_of_utc,spot_usd\nnot-a-date,100000\n",
        encoding="utf-8",
    )

    meta = archive_meta(tmp_path)

    assert meta["available_days"] == 1
    assert meta["snapshot_count"] == 1
    assert meta["earliest_utc"] is None
    assert meta["latest_utc"] is None
    assert meta["replay_ready"] is False


def test_distribution_stats_task_wrapper_points_at_distribution_installer() -> None:
    root = Path(__file__).resolve().parents[1]
    wrapper = root / "install_distribution_stats_collector_task.cmd"
    text = wrapper.read_text(encoding="utf-8")
    assert "install_distribution_collector_task.cmd" in text


def test_install_distribution_task_ps1_references_snapshot_runner() -> None:
    root = Path(__file__).resolve().parents[1]
    ps1 = root / "scripts" / "install_ppe_distribution_collector_task.ps1"
    text = ps1.read_text(encoding="utf-8")
    assert "collect_distribution_stats_snapshot.cmd" in text
    assert "07:45" in text
    assert "PPE Distribution Stats Daily" in text
