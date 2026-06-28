"""Cross-venue collector pipeline cmd wrappers exist and point at scripts."""

from __future__ import annotations

from pathlib import Path


def test_cross_venue_collector_cmd_wrappers_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for name in (
        "collect_cross_venue_snapshot.cmd",
        "run_cross_venue_scan.cmd",
        "run_cross_venue_backtest.cmd",
        "run_cross_venue_daily.cmd",
        "install_cross_venue_collector_task.cmd",
    ):
        path = root / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "python" in text.lower()


def test_install_cross_venue_task_ps1_references_daily_runner() -> None:
    root = Path(__file__).resolve().parents[1]
    ps1 = root / "scripts" / "install_ppe_cross_venue_collector_task.ps1"
    text = ps1.read_text(encoding="utf-8")
    assert "run_cross_venue_daily.cmd" in text
    assert "07:15" in text
