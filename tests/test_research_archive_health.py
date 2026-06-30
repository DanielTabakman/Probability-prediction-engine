"""Tests for research archive health counters."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_collector_health_counts_calendar_days(tmp_path: Path) -> None:
    from scripts.research_archive_health import build_archive_health, collector_health

    root = tmp_path / "artifacts" / "cross_venue_snapshots"
    (root / "2026-06-01").mkdir(parents=True)
    (root / "2026-06-02").mkdir(parents=True)
    (root / "2026-06-02" / "ppe_cross_venue_prob_panel_120000Z.csv").write_text("x", encoding="utf-8")

    spec = {
        "id": "cross_venue_event_gap",
        "label": "test",
        "archive_root": "artifacts/cross_venue_snapshots",
        "file_glob": "**/ppe_cross_venue_prob_panel_*.csv",
        "min_calendar_days": 14,
    }
    item = collector_health(tmp_path, spec)
    assert item["calendar_days"] == 2
    assert item["file_count"] == 1
    assert item["ready"] is False
    assert "last_snapshot_utc" in item


def test_build_archive_health_writes_json(tmp_path: Path) -> None:
    from scripts.research_archive_health import write_archive_health

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "research_pipeline_registry.json").write_text(
        (REPO / "config" / "research_pipeline_registry.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    out = write_archive_health(tmp_path)
    assert out.is_file()
    assert "collectors" in out.read_text(encoding="utf-8")


def test_format_health_line_replaces_unicode_arrow_for_console() -> None:
    from scripts.research_archive_health import format_health_line

    line = format_health_line(
        {"label": "Cross-venue PM \u2194 Deribit", "calendar_days": 8, "min_calendar_days": 14}
    )
    assert "<->" in line
    assert "\u2194" not in line
