"""Regression coverage for the issue #50 Options Made Simple A -> B witness charter."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.founder_portfolio import collect_portfolio

REPO = Path(__file__).resolve().parents[1]
A_ID = "options_horizon_comparison_v1"
RB_ID = "region_bet_monitor_value_v1"
A_PLAN = "docs/SOP/PHASE_PLANS/options_horizon_comparison_v1_relay.json"
B_PLAN = "docs/SOP/PHASE_PLANS/options_expression_fit_ranking_v1_relay.json"
RB_PLAN = "docs/SOP/PHASE_PLANS/region_bet_monitor_value_v1_relay.json"
RB09_PLAN = "docs/SOP/PHASE_PLANS/region_bet_risk_expression_bridge_v1_relay.json"
RB10_PLAN = "docs/SOP/PHASE_PLANS/region_bet_payoff_save_v1_relay.json"


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


def test_horizon_comparison_queue_row_is_done_after_reuse() -> None:
    queue = _json("docs/SOP/PHASE_QUEUE.json")
    a = next(item for item in queue["items"] if item.get("planPath") == A_PLAN)
    assert a["status"] == "DONE"
    assert "terminal backlog" in a["doneReason"]


def test_expression_fit_queue_row_is_done_after_closeout() -> None:
    queue = _json("docs/SOP/PHASE_QUEUE.json")
    b = next(item for item in queue["items"] if item.get("planPath") == B_PLAN)
    assert b["status"] == "DONE"


def test_order_09_queue_row_is_done_after_closeout() -> None:
    queue = _json("docs/SOP/PHASE_QUEUE.json")
    closed = next(item for item in queue["items"] if item.get("planPath") == RB09_PLAN)
    assert closed["status"] == "DONE"
    assert "#5463" in closed["doneReason"]


def test_order_10_queue_row_is_done_after_closeout() -> None:
    queue = _json("docs/SOP/PHASE_QUEUE.json")
    closed = next(item for item in queue["items"] if item.get("planPath") == RB10_PLAN)
    assert closed["status"] == "DONE"
    assert "#5475" in closed["doneReason"]


def test_order_11_queue_row_is_done_after_closeout() -> None:
    queue = _json("docs/SOP/PHASE_QUEUE.json")
    closed = next(item for item in queue["items"] if item.get("planPath") == RB_PLAN)
    assert closed["status"] == "DONE"
    assert "#5478" in closed["doneReason"]


def test_ready_frontier_is_empty_after_order_11_closeout(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    ready = _ready_queue_items()
    assert ready == []


def test_founder_portfolio_does_not_rebuild_region_bet_monitor_value(monkeypatch) -> None:
    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)

    snapshot = collect_portfolio(REPO)
    ppe = _pipeline(snapshot)
    ready_ids = [item["work_item_id"] for item in ppe["ready_work"]]

    assert RB_ID not in ready_ids
    rec = snapshot["recommended_next_action"] or {}
    assert rec.get("work_item_id") != RB_ID
    assert rec.get("work_item_id") != "ppe_commodity_proxy_tier1_v1"


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
