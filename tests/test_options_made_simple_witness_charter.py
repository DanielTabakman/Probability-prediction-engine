"""Regression coverage for the issue #50 Options Made Simple A -> B witness charter."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.founder_portfolio import collect_portfolio

REPO = Path(__file__).resolve().parents[1]
A_ID = "options_horizon_comparison_v1"
B_ID = "options_expression_fit_ranking_v1"
A_PLAN = "docs/SOP/PHASE_PLANS/options_horizon_comparison_v1_relay.json"
B_PLAN = "docs/SOP/PHASE_PLANS/options_expression_fit_ranking_v1_relay.json"


def _json(rel: str) -> dict:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _ready_queue_items() -> list[dict]:
    return [item for item in _json("docs/SOP/PHASE_QUEUE.json")["items"] if item.get("status") == "READY"]


def _product_touch_set(plan: dict) -> set[str]:
    for item in plan["slices"]:
        if item.get("declaredPlane") == "PRODUCT-PLANE" and item.get("touchSet"):
            return set(item["touchSet"])
    raise AssertionError(f"no product touchSet in {plan.get('name')}")


def _pipeline(snapshot: dict) -> dict:
    return next(pipe for pipe in snapshot["pipelines"] if pipe["pipeline_id"] == "ppe")


def test_ready_frontier_contains_only_options_made_simple_pair(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    ready = _ready_queue_items()
    assert [item["planPath"] for item in ready] == [A_PLAN, B_PLAN]
    assert [item["founderPriority"] for item in ready] == ["HIGH", "HIGH"]
    assert ready[0]["dependencyUnblockValue"] > ready[1]["dependencyUnblockValue"]
    assert all("issue #50" in item["reason"] for item in ready)
    joined = "\n".join(item["planPath"] + " " + item["reason"] for item in ready).lower()
    for stale in ("commodity_proxy", "uso", "hyperliquid", "replay_scrubber", "tier1b", "tier1c"):
        assert stale not in joined


def test_founder_portfolio_ranks_a_before_b_and_b_dispatches_from_current_main(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    snapshot = collect_portfolio(REPO)
    ppe = _pipeline(snapshot)
    ready_ids = [item["work_item_id"] for item in ppe["ready_work"]]

    assert ready_ids[:2] == [A_ID, B_ID]
    assert snapshot["recommended_next_action"]["work_item_id"] == A_ID
    b_work = next(item for item in ppe["ready_work"] if item["work_item_id"] == B_ID)
    assert b_work["source_plan"] == B_PLAN
    assert b_work["selected_native_slice"] == "Options-ExpressionFit-Product-Slice002"
    assert b_work["selected_native_dispatchable"] is True
    assert b_work["native_prerequisites"]["dispatch_blockers"] == []
    assert b_work["allowed_product_paths"] == [
        "src/engine/options_expression_fit_ranking.py",
        "src/viz/options_expression_fit_ranking_boundary.py",
        "scripts/rank_options_expression_fit.py",
        "apps/msos-web/src/lib/optionsExpressionFitRanking.ts",
        "apps/msos-web/src/components/OptionsExpressionFitRankingPanel.tsx",
        "apps/msos-web/src/components/ExpressionPlanningPanel.tsx",
        "tests/test_options_expression_fit_ranking.py",
        "tests/test_msos_web_options_expression_fit_ranking.py",
    ]


def test_a_and_b_touch_sets_are_disjoint_and_b_forbids_a_paths() -> None:
    a_plan = _json(A_PLAN)
    b_plan = _json(B_PLAN)
    a_touch = _product_touch_set(a_plan)
    b_touch = _product_touch_set(b_plan)

    assert a_touch.isdisjoint(b_touch)
    assert set(a_plan["authority"]["allowedProductPaths"]) == a_touch
    assert set(b_plan["authority"]["allowedProductPaths"]) == b_touch
    assert a_touch.issubset(set(b_plan["authority"]["forbiddenPaths"]))
    assert b_plan["independenceContract"]["buildsFromFrozenCurrentMain"] is True
    assert b_plan["independenceContract"]["doesNotImportJobA"] is True
    assert b_plan["independenceContract"]["nativePrerequisiteOnJobA"] is False


def test_jobs_are_bounded_and_do_not_reuse_completed_witness_work() -> None:
    for rel in (A_PLAN, B_PLAN):
        plan = _json(rel)
        touch = _product_touch_set(plan)
        assert 1 <= len(touch) <= 8
        assert all(not path.endswith("/") for path in touch)
        assert "USO commodity proxy witness reuse" in plan["authority"]["forbiddenPaths"]
        assert "DanielTabakman/msos-autobuilder" in plan["authority"]["forbiddenPaths"]

    queue = _json("docs/SOP/PHASE_QUEUE.json")
    commodity = next(
        item
        for item in queue["items"]
        if item.get("planPath") == "docs/SOP/PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json"
    )
    assert commodity["status"] == "PLANNED"
    assert commodity.get("explicitRequeue") is not True
    assert "must not be reused" in commodity["holdReason"]


def test_charter_docs_preserve_product_order_without_native_prerequisite() -> None:
    a_selection = (REPO / "docs/SOP/POST_OPTIONS_HORIZON_COMPARISON_V1_SELECTION.md").read_text(encoding="utf-8")
    b_selection = (REPO / "docs/SOP/POST_OPTIONS_EXPRESSION_FIT_RANKING_V1_SELECTION.md").read_text(
        encoding="utf-8"
    )
    b_sprint = (REPO / "docs/SOP/SPRINT_OPTIONS_EXPRESSION_FIT_RANKING_V1.md").read_text(encoding="utf-8")

    assert "Job A is first" in a_selection
    assert "product story" in b_selection
    assert "no native prerequisite requiring A completion" in b_selection
    assert "No technical prerequisite" in b_sprint
