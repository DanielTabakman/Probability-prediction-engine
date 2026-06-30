"""MSOS cross-venue gap panel smoke tests."""

from __future__ import annotations

from pathlib import Path


def test_cross_venue_gap_panel_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "apps/msos-web/src/components/CrossVenueGapPanel.tsx").is_file()
    assert (root / "apps/msos-web/src/lib/crossVenueResearch.ts").is_file()


def test_strategy_lab_work_section_references_panel() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "apps/msos-web/src/components/StrategyLabWorkSection.tsx").read_text(encoding="utf-8")
    assert "CrossVenueGapPanel" in text
    assert 'assetMeta.id === "BTC"' in text
