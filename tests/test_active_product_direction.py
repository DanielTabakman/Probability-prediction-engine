"""Tests for ACTIVE_PRODUCT_DIRECTION propagation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.active_product_direction import (
    DIRECTION_REL,
    MARKER_END,
    MARKER_START,
    load_direction,
    render_frontier_block,
    _replace_marked_block,
)

REPO = Path(__file__).resolve().parents[1]


def test_load_direction_has_pivot() -> None:
    d = load_direction(REPO)
    assert d.pivot_id == "usable-demo-build-v1"
    assert d.active_chapter_id == "msos_usable_demo_v1"


def test_render_frontier_block_contains_markers() -> None:
    d = load_direction(REPO)
    block = render_frontier_block(d)
    assert block.startswith(MARKER_START)
    assert block.endswith(MARKER_END)
    assert "usable demo" in block.lower()


def test_replace_marked_block_on_frontier() -> None:
    src = REPO / "docs/SOP/MSOS_FRONTIER.md"
    text = src.read_text(encoding="utf-8")
    assert MARKER_START in text
    d = load_direction(REPO)
    updated, ok = _replace_marked_block(text, render_frontier_block(d))
    assert ok
    assert "msos_usable_demo_v1" in updated


def test_sync_product_direction_alias() -> None:
    from scripts.active_product_direction import load_direction, sync_product_direction

    report = sync_product_direction(REPO)
    assert report.get("pivotId") == load_direction(REPO).pivot_id
    assert "docs/SOP/MSOS_FRONTIER.md" in (report.get("updated") or [])
