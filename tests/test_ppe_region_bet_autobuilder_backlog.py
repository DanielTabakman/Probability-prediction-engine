import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOP = ROOT / "docs" / "SOP"
BACKLOG = SOP / "PHASE_CHAPTER_BACKLOG.json"

RUNNABLE_ORDERS = (9, 10, 11, 12, 13, 16, 17)
DEFERRED_ORDERS = (14, 15)


def _items_by_order() -> dict[int, dict[str, object]]:
    payload = json.loads(BACKLOG.read_text(encoding="utf-8"))
    rows = [row for row in payload["items"] if "autobuilderCatalogOrder" in row]
    orders = [row["autobuilderCatalogOrder"] for row in rows]
    assert len(orders) == len(set(orders))
    return {int(row["autobuilderCatalogOrder"]): row for row in rows}


def _phase_plan(row: dict[str, object]) -> dict[str, object]:
    relative = row.get("planPath")
    assert isinstance(relative, str) and relative.startswith("docs/SOP/PHASE_PLANS/")
    path = ROOT / relative
    assert path.is_file(), relative
    return json.loads(path.read_text(encoding="utf-8"))


def test_completed_region_bet_frontier_is_recorded() -> None:
    rows = _items_by_order()
    assert rows[7]["chapterId"] == "region_bet_guided_shell_v1"
    assert rows[7]["status"] == "done"
    assert rows[8]["chapterId"] == "region_bet_market_compare_bridge_v1"
    assert rows[8]["status"] == "done"
    assert "#5444" in str(rows[8]["reason"])
    assert rows[9]["chapterId"] == "region_bet_risk_expression_bridge_v1"
    assert rows[9]["status"] == "done"
    assert "#5463" in str(rows[9]["reason"])
    assert rows[10]["chapterId"] == "region_bet_payoff_save_v1"
    assert rows[10]["status"] == "ready"


def test_order_09_resolves_stale_draft_to_merged_replacement() -> None:
    row = _items_by_order()[9]
    assert row["relatedPullRequests"] == [
        "DanielTabakman/Probability-prediction-engine#5428"
    ]
    resolutions = row["relatedPullRequestResolutions"]
    assert isinstance(resolutions, list) and len(resolutions) == 1
    resolution = resolutions[0]
    assert resolution["disposition"] == "superseded"
    assert resolution["replacement"] == (
        "DanielTabakman/Probability-prediction-engine#5454"
    )
    assert resolution["mergeCommit"] == "0e04b102a90ee311cedc6a0d673ff53fb975ebef"


def test_every_runnable_backlog_item_has_one_bounded_native_product_slice() -> None:
    rows = _items_by_order()
    for order in RUNNABLE_ORDERS:
        row = rows[order]
        assert row["packetization"] == "just_in_time"
        authority = row["autobuilderMergeAuthority"]
        assert authority["class"] == "AUTO_MERGE_WHEN_GREEN"
        assert authority["declaredAt"]

        plan = _phase_plan(row)
        assert plan["name"] == row["chapterId"]
        acceptance = plan["acceptanceCriteria"]
        assert isinstance(acceptance, list) and acceptance

        slices = plan["slices"]
        product = [
            item
            for item in slices
            if item.get("declaredPlane") == "PRODUCT-PLANE"
            and item.get("layerPreset") != "CONTROL"
            and item.get("touchSet")
        ]
        assert len(product) == 1
        selected = product[0]
        selected_index = slices.index(selected)
        assert selected_index > 0
        for prerequisite in slices[:selected_index]:
            assert prerequisite.get("implementationStatus") == "COMPLETE"
            assert prerequisite.get("nonBlocking") is True

        touch_set = selected["touchSet"]
        assert touch_set == plan["authority"]["allowedProductPaths"]
        assert len(touch_set) == len(set(touch_set))
        assert all(
            not any(token in path for token in "*?[") and not path.endswith("/")
            for path in touch_set
        )
        assert 1 <= selected["maxAttempts"] <= 3
        assert any("closeout" in item for item in slices)


def test_archive_gated_orders_stay_deferred_without_blocking_region_bet() -> None:
    rows = _items_by_order()
    assert rows[14]["eligibility"] == "deferred_until_archive_gate"
    assert rows[15]["status"] == "deferred"
    for order in DEFERRED_ORDERS:
        assert rows[order].get("packetization") != "just_in_time"
        assert "autobuilderMergeAuthority" not in rows[order]
    assert rows[16]["dependsOn"] == ["region_bet_monitor_value_v1"]
    assert rows[17]["dependsOn"] == ["region_bet_monitor_value_v1"]
