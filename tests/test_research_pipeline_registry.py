"""Tests for research pipeline registry."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_registry_loads_collectors_and_tests() -> None:
    from scripts.research_pipeline_registry import collectors, load_registry, tests

    reg = load_registry(REPO)
    assert reg.get("version") == 1
    c = collectors(REPO)
    t = tests(REPO)
    assert len(c) >= 3
    assert len(t) >= 3
    ids = {item["id"] for item in c}
    assert "cross_venue_event_gap" in ids
    assert "implied_distribution_ts" in ids


def test_collector_by_id() -> None:
    from scripts.research_pipeline_registry import collector_by_id

    spec = collector_by_id("cross_venue_event_gap", REPO)
    assert spec is not None
    assert "collect_cross_venue_snapshot" in str(spec.get("script"))
