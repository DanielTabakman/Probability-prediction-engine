"""Charter / closeout witness for MSOS P4 Strategy Lab."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

P4_PLAN_REL = "docs/SOP/PHASE_PLANS/msos_p4_strategy_lab_relay.json"
P4_PLAN = SOP / "PHASE_PLANS" / "msos_p4_strategy_lab_relay.json"
P4_SPRINT = SOP / "SPRINT_MSOS_P4_STRATEGY_LAB.md"
P4_SELECTION = SOP / "POST_MSOS_P4_STRATEGY_LAB_SELECTION.md"
P4_EVIDENCE = SOP / "MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
BACKLOG = SOP / "PHASE_CHAPTER_BACKLOG.json"
MANIFEST = SOP / "ACTIVE_PHASE_MANIFEST.json"
HOUSEKEEPING_PLAN = "docs/SOP/PHASE_PLANS/repo_housekeeping_v1_relay.json"
MVP1_LEGIBILITY_PLAN = "docs/SOP/PHASE_PLANS/mvp1_probability_method_legibility_relay.json"
MVP1_DIST_STATS_PLAN = "docs/SOP/PHASE_PLANS/mvp1_distribution_stats_legibility_relay.json"
MSOS_DIST_DEMO_PLAN = "docs/SOP/PHASE_PLANS/msos_strategy_lab_distribution_demo_relay.json"
MSOS_P5_THESIS_PLAN = "docs/SOP/PHASE_PLANS/msos_p5_thesis_confirm_relay.json"
MSOS_P6_EXPRESSION_PLAN = "docs/SOP/PHASE_PLANS/msos_p6_expression_sim_relay.json"
MSOS_P7_MONITORING_PLAN = "docs/SOP/PHASE_PLANS/msos_p7_monitoring_relay.json"
MSOS_P8_TESTER_PLAN = "docs/SOP/PHASE_PLANS/msos_p8_tester_release_relay.json"
MSOS_PROD_WIRE_PLAN = "docs/SOP/PHASE_PLANS/msos_production_wiring_v1_relay.json"
MSOS_USER_STATE_PLAN = "docs/SOP/PHASE_PLANS/msos_user_state_v1_relay.json"
MSOS_WORKFLOW_PLAN = "docs/SOP/PHASE_PLANS/msos_workflow_persistence_v1_relay.json"
MVP1_SNAPSHOT_OWNER_PLAN = "docs/SOP/PHASE_PLANS/mvp1_snapshot_owner_v1_relay.json"
MSOS_ACCESS_IDENTITY_PLAN = "docs/SOP/PHASE_PLANS/msos_access_identity_v1_relay.json"
MSOS_MONITOR_HISTORY_PLAN = "docs/SOP/PHASE_PLANS/msos_monitor_history_live_v1_relay.json"
MSOS_ENTITLEMENTS_PLAN = "docs/SOP/PHASE_PLANS/msos_entitlements_v1_relay.json"
MSOS_EMBED_SHELL_PLAN = (
    "docs/SOP/PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json"
)
MSOS_MCD_WITNESS_PLAN = (
    "docs/SOP/PHASE_PLANS/msos_mcd_production_witness_v1_relay.json"
)
MSOS_E2E_WITNESS_PLAN = (
    "docs/SOP/PHASE_PLANS/msos_e2e_product_witness_v1_relay.json"
)
MSOS_USABLE_DEMO_PLAN = (
    "docs/SOP/PHASE_PLANS/msos_usable_demo_v1_relay.json"
)
PPE_CRYPTO_MA_PLAN = (
    "docs/SOP/PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json"
)
MSOS_SELF_SERVE_PLAN = (
    "docs/SOP/PHASE_PLANS/msos_self_serve_onboarding_v1_relay.json"
)
PPE_EQUITY_PLAN = (
    "docs/SOP/PHASE_PLANS/ppe_equity_options_v1_relay.json"
)
PPE_TRADEABLE_UNIVERSE_PLAN = (
    "docs/SOP/PHASE_PLANS/ppe_tradeable_universe_v1_relay.json"
)
PPE_COMMODITY_PROXY_PLAN = (
    "docs/SOP/PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json"
)
MVP1_DIST_QUANT_V2_PLAN = (
    "docs/SOP/PHASE_PLANS/mvp1_distribution_quant_research_v2_relay.json"
)
ALLOWED_READY_PLANS = (
    HOUSEKEEPING_PLAN,
    MVP1_LEGIBILITY_PLAN,
    MVP1_DIST_STATS_PLAN,
    MVP1_DIST_QUANT_V2_PLAN,
    MSOS_DIST_DEMO_PLAN,
    MSOS_P5_THESIS_PLAN,
    MSOS_P6_EXPRESSION_PLAN,
    MSOS_P7_MONITORING_PLAN,
    MSOS_P8_TESTER_PLAN,
    MSOS_PROD_WIRE_PLAN,
    MSOS_USER_STATE_PLAN,
    MSOS_WORKFLOW_PLAN,
    MVP1_SNAPSHOT_OWNER_PLAN,
    MSOS_ACCESS_IDENTITY_PLAN,
    MSOS_MONITOR_HISTORY_PLAN,
    MSOS_ENTITLEMENTS_PLAN,
    MSOS_EMBED_SHELL_PLAN,
    MSOS_MCD_WITNESS_PLAN,
    MSOS_E2E_WITNESS_PLAN,
    MSOS_USABLE_DEMO_PLAN,
    PPE_CRYPTO_MA_PLAN,
    MSOS_SELF_SERVE_PLAN,
    PPE_EQUITY_PLAN,
    PPE_TRADEABLE_UNIVERSE_PLAN,
    PPE_COMMODITY_PROXY_PLAN,
)


def test_p4_charter_artifacts_exist() -> None:
    for path in (P4_PLAN, P4_SPRINT, P4_SELECTION, P4_EVIDENCE):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_p4_phase_plan_valid() -> None:
    plan = json.loads(P4_PLAN.read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "MSOS-P4-Control-Slice001"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "msos_p4_strategy_lab"


def test_phase_queue_msos_p4_done() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == P4_PLAN_REL)
    assert row["status"] == "DONE"


def test_backlog_p4_done() -> None:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    by_id = {item["chapterId"]: item for item in backlog["items"]}
    p4 = by_id["msos_p4_strategy_lab"]
    assert p4["status"] == "done"
    assert p4["planPath"] == P4_PLAN_REL


def test_manifest_ready_for_next_chapter() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] in ("READY", "RUNNING", "COMPLETE")
    if manifest["status"] == "COMPLETE":
        assert manifest.get("phasePlanPath") in ("", None)
    if manifest["status"] == "READY":
        assert manifest.get("phasePlanPath") in ALLOWED_READY_PLANS


def test_next_chapter_ready_or_queued() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    hk_queue = next((i for i in queue["items"] if i.get("planPath") == HOUSEKEEPING_PLAN), None)
    hk_backlog = next(i for i in backlog["items"] if i.get("chapterId") == "repo_housekeeping_v1")
    if hk_queue is not None:
        assert hk_queue["status"] in ("READY", "PLANNED", "RUNNING", "DONE")
    else:
        assert hk_backlog["status"] in ("queued", "chartered", "blocked", "done")


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"
