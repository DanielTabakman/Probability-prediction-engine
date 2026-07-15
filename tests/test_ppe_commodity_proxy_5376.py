"""Regression coverage for the issue #5376 USO witness packet."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.founder_portfolio import collect_portfolio

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"
PLAN_REL = "docs/SOP/PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json"


def _json(rel: str) -> dict:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _item_by_plan(rel: str, plan: str) -> dict:
    data = _json(rel)
    return next(item for item in data["items"] if item.get("planPath") == plan)


def _backlog(chapter_id: str) -> dict:
    data = _json("docs/SOP/PHASE_CHAPTER_BACKLOG.json")
    return next(item for item in data["items"] if item.get("chapterId") == chapter_id)


def test_issue_5376_has_exactly_one_ready_ppe_item_and_selects_uso_packet(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    snapshot = collect_portfolio(REPO)
    ppe = next(pipe for pipe in snapshot["pipelines"] if pipe["pipeline_id"] == "ppe")

    assert [item["work_item_id"] for item in ppe["ready_work"]] == ["ppe_commodity_proxy_tier1_v1"]
    work = ppe["ready_work"][0]
    assert work["source_plan"] == PLAN_REL
    assert work["selected_native_slice"] == "PPE-CommProxy-Core-Slice002"
    assert work["selected_native_dispatchable"] is True
    assert snapshot["recommended_next_action"]["work_item_id"] == "ppe_commodity_proxy_tier1_v1"


def test_issue_5376_control_complete_and_core_pending_dispatchable(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    ppe = next(pipe for pipe in collect_portfolio(REPO)["pipelines"] if pipe["pipeline_id"] == "ppe")
    packet = ppe["ready_work"][0]["native_prerequisites"]

    assert packet["source"] == "ppe_native_read_only"
    assert packet["source_plan"] == PLAN_REL
    assert packet["selected_native_slice"] == "PPE-CommProxy-Core-Slice002"
    assert packet["dispatchable"] is True
    assert packet["dispatch_blockers"] == []
    assert packet["statuses"]["PPE-CommProxy-Control-Slice001"]["status"] == "completed"
    assert packet["statuses"]["PPE-CommProxy-Core-Slice002"]["status"] == "pending"
    assert packet["allowed_product_paths"] == [
        "config/assets.yaml",
        "src/viz/embed_display_boundary.py",
        "scripts/witness_asset_catalog.py",
    ]


def test_issue_5376_scope_is_uso_only_without_gld_slv_product_leakage() -> None:
    plan = _json(PLAN_REL)
    evidence = (SOP / "PPE_COMMODITY_PROXY_TIER1_V1_EVIDENCE_STATUS.md").read_text(encoding="utf-8")
    selection = (SOP / "POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md").read_text(encoding="utf-8")
    sprint = (SOP / "SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md").read_text(encoding="utf-8")
    assets = (REPO / "config" / "assets.yaml").read_text(encoding="utf-8")

    assert plan["productScope"]["assets"] == ["USO"]
    assert plan["productScope"]["excludedAssets"] == ["GLD", "SLV"]
    assert "PPE-CommProxy-Core-Slice002" in selection
    assert "- [ ] USO" in evidence
    assert "- [ ] GLD" not in evidence
    assert "- [ ] SLV" not in evidence
    assert "Prepare the first dispatchable product slice for **USO**" in sprint
    assert "\n  USO:" not in assets
    assert "\n  GLD:" not in assets
    assert "\n  SLV:" not in assets


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


def test_issue_5376_allowed_and_forbidden_authority_are_explicit() -> None:
    authority = _json(PLAN_REL)["authority"]

    assert authority["allowedProductPaths"] == [
        "config/assets.yaml",
        "src/viz/embed_display_boundary.py",
        "scripts/witness_asset_catalog.py",
    ]
    for forbidden in (
        "product-main write",
        "merge authority",
        "publication authority",
        "DanielTabakman/msos-autobuilder",
        "Match Horizon",
    ):
        assert forbidden in authority["forbiddenPaths"]
