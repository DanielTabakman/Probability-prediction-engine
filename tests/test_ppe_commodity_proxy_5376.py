"""Regression coverage for retiring the issue #5376 USO witness packet."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.founder_portfolio import collect_portfolio

REPO = Path(__file__).resolve().parents[1]
COMMODITY_PLAN = "docs/SOP/PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json"


def _json(rel: str) -> dict:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _item_by_plan(rel: str, plan: str) -> dict:
    data = _json(rel)
    return next(item for item in data["items"] if item.get("planPath") == plan)


def _backlog(chapter_id: str) -> dict:
    data = _json("docs/SOP/PHASE_CHAPTER_BACKLOG.json")
    return next(item for item in data["items"] if item.get("chapterId") == chapter_id)


def test_issue_50_no_longer_selects_uso_acceptance_witness(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    snapshot = collect_portfolio(REPO)
    ppe = next(pipe for pipe in snapshot["pipelines"] if pipe["pipeline_id"] == "ppe")

    assert "ppe_commodity_proxy_tier1_v1" not in [item["work_item_id"] for item in ppe["ready_work"]]
    assert snapshot["recommended_next_action"]["work_item_id"] == "options_horizon_comparison_v1"


def test_uso_packet_remains_bounded_but_not_ready() -> None:
    queue_item = _item_by_plan("docs/SOP/PHASE_QUEUE.json", COMMODITY_PLAN)
    roadmap_item = _item_by_plan("docs/SOP/PHASE_SELECTION_ROADMAP.json", COMMODITY_PLAN)
    backlog_item = _backlog("ppe_commodity_proxy_tier1_v1")
    plan = _json(COMMODITY_PLAN)

    assert queue_item["status"] == "PLANNED"
    assert "must not be reused" in queue_item["holdReason"]
    assert roadmap_item["status"] == "skipped"
    assert backlog_item["status"] == "blocked"
    assert plan["productScope"]["assets"] == ["USO"]
    assert plan["authority"]["allowedProductPaths"] == [
        "config/assets.yaml",
        "src/viz/embed_display_boundary.py",
        "scripts/witness_asset_catalog.py",
    ]


def test_issue_5376_batches_2_and_3_are_not_falsely_closed() -> None:
    queue_b2 = _item_by_plan("docs/SOP/PHASE_QUEUE.json", "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1b_v1_relay.json")
    queue_b3 = _item_by_plan("docs/SOP/PHASE_QUEUE.json", "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1c_v1_relay.json")
    roadmap_b2 = _item_by_plan(
        "docs/SOP/PHASE_SELECTION_ROADMAP.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1b_v1_relay.json",
    )
    roadmap_b3 = _item_by_plan(
        "docs/SOP/PHASE_SELECTION_ROADMAP.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1c_v1_relay.json",
    )

    assert queue_b2["status"] != "DONE"
    assert queue_b3["status"] != "DONE"
    assert _backlog("ppe_equity_universe_tier1b_v1")["status"] == "blocked"
    assert _backlog("ppe_equity_universe_tier1c_v1")["status"] == "queued"
    assert roadmap_b2["status"] == "skipped"
    assert roadmap_b3["status"] == "skipped"
