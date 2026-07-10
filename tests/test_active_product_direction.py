"""Tests for ACTIVE_PRODUCT_DIRECTION propagation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.active_product_direction import (
    DIRECTION_REL,
    MARKER_END,
    MARKER_START,
    load_direction,
    render_whats_next,
    render_frontier_block,
    summarize_next_action,
    _replace_marked_block,
)

REPO = Path(__file__).resolve().parents[1]


def test_load_direction_has_pivot() -> None:
    d = load_direction(REPO)
    assert d.pivot_id == "trader-workflow-integration-v1"
    assert d.active_chapter_id == ""
    assert "trust_surface" in d.next_steward_action.lower() or "SELECTION" in d.next_steward_action
    assert d.milestone_label == "Trader Workflow Integration v1"
    prior = {m["id"]: m for m in d.raw.get("priorMilestones", [])}
    assert prior["ppe_crypto_multi_asset_v1"]["status"] == "COMPLETE"
    assert prior["ppe_equity_options_v1"]["status"] == "COMPLETE"
    assert prior["msos_workflow_asset_parity_v1"]["status"] == "COMPLETE"


def test_render_frontier_block_contains_markers() -> None:
    d = load_direction(REPO)
    block = render_frontier_block(d)
    assert block.startswith(MARKER_START)
    assert block.endswith(MARKER_END)
    assert "workstream" in block.lower()


def test_render_whats_next_has_summary_and_detail() -> None:
    d = load_direction(REPO)
    text = render_whats_next(d)
    summary = summarize_next_action(d.next_steward_action)
    assert "**Next action summary:**" in text
    assert f"**Next action summary:** {summary}" in text
    assert "**Next action detail:**" in text
    assert len(summary) <= 280


def test_replace_marked_block_on_frontier() -> None:
    src = REPO / "docs/SOP/MSOS_FRONTIER.md"
    text = src.read_text(encoding="utf-8")
    assert MARKER_START in text
    d = load_direction(REPO)
    updated, ok = _replace_marked_block(text, render_frontier_block(d))
    assert ok
    assert "ppe_crypto_multi_asset_v1" in updated


def test_sync_product_direction_alias() -> None:
    from scripts.active_product_direction import load_direction, sync_product_direction

    report = sync_product_direction(REPO)
    assert report.get("pivotId") == load_direction(REPO).pivot_id
    assert "docs/SOP/MSOS_FRONTIER.md" in (report.get("updated") or [])
