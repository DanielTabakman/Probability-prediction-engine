"""Tests for run_research_daily orchestrator."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_run_research_daily_dry_run_skips_subprocess(tmp_path: Path) -> None:
    from scripts.run_research_daily import run_research_daily

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "research_pipeline_registry.json").write_text(
        (REPO / "config" / "research_pipeline_registry.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    summary = run_research_daily(tmp_path, collect=True, run_tests=True, dry_run=True)
    assert summary.get("collectors")
    tests_out = summary.get("tests") or []
    skipped = summary.get("skipped_tests") or []
    assert tests_out or skipped


def test_run_research_daily_skips_test_when_archive_thin(tmp_path: Path) -> None:
    from scripts.run_research_daily import run_research_daily

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "research_pipeline_registry.json").write_text(
        (REPO / "config" / "research_pipeline_registry.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    summary = run_research_daily(tmp_path, collect=False, run_tests=True, dry_run=False)
    skipped = summary.get("skipped_tests") or []
    assert any(s.get("id") == "cross_venue_backtest" for s in skipped)
