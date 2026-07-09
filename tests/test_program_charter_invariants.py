"""Consolidated charter invariants for closed chapters (witness tier).

Replaces per-chapter closeout/charter witness modules that only checked historical
COMPLETE markers and shared queue/manifest shape.
"""

from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from scripts.implied_lab_ui_smoke_harness import ScenarioResult
from scripts.ppe_manifest import load_manifest, resolve_summary, validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"

SPRINT003_PLAN = "docs/SOP/PHASE_PLANS/mvp1_sprint003_evidence_plane_relay.json"
POST_PHASE3_PLAN = "docs/SOP/PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json"


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"


def test_scenario_result_has_commercial_wrapper_field() -> None:
    names = {f.name for f in fields(ScenarioResult)}
    assert "commercial_wrapper_found" in names


def test_commercial_wrapper_defaults_false() -> None:
    row = ScenarioResult(scenario="MVP1_compact_verification")
    assert row.commercial_wrapper_found is False


def test_sprint003_chapter_complete_witness() -> None:
    sprint_spec = SOP / "SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
    evidence = SOP / "MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md"
    assert sprint_spec.is_file() and evidence.is_file()
    spec_text = sprint_spec.read_text(encoding="utf-8")
    for slice_id in (
        "MVP1-Sprint003-Evidence-Slice002",
        "MVP1-Sprint003-Witness-Slice003",
        "MVP1-Sprint003-Closeout-Slice004",
    ):
        assert slice_id in spec_text
        assert "**CLOSED**" in spec_text
    assert "**COMPLETE**" in spec_text
    ev_text = evidence.read_text(encoding="utf-8")
    assert "**COMPLETE**" in ev_text
    assert "run_pushable_gate.py" in ev_text


def test_sprint003_plan_valid() -> None:
    plan = json.loads((REPO / SPRINT003_PLAN).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "MVP1-Sprint003-Control-Slice001"


def test_post_phase3_chapter_complete_witness() -> None:
    evidence = SOP / "MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md"
    assert evidence.is_file()
    text = evidence.read_text(encoding="utf-8")
    assert "MVP1-PostPhase3-Control-Slice001" in text
    assert "**COMPLETE**" in text


def test_phase3_commercial_wrapper_chapter_complete_witness() -> None:
    evidence = SOP / "PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md"
    assert evidence.is_file()
    text = evidence.read_text(encoding="utf-8")
    assert "**Status:** **COMPLETE**" in text
    assert "Phase3-CommercialWrapper-Product-Slice002" in text


def test_manifest_points_at_known_active_or_closed_plan() -> None:
    manifest = load_manifest(REPO)
    msos_p3_plan = "docs/SOP/PHASE_PLANS/msos_p3_command_center_relay.json"
    allowed = {
        "",
        SPRINT003_PLAN,
        POST_PHASE3_PLAN,
        "docs/SOP/PHASE_PLANS/mvp1_phase5_review_hardening_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_steering_sync_evidence_relay.json",
        "docs/SOP/PHASE_PLANS/msos_website_program_p0_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p1_stack_routing_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p2_homepage_relay.json",
        msos_p3_plan,
        "docs/SOP/PHASE_PLANS/msos_p4_strategy_lab_relay.json",
        "docs/SOP/PHASE_PLANS/repo_housekeeping_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_probability_method_legibility_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_distribution_stats_legibility_relay.json",
        "docs/SOP/PHASE_PLANS/msos_strategy_lab_distribution_demo_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p5_thesis_confirm_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p6_expression_sim_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p7_monitoring_relay.json",
        "docs/SOP/PHASE_PLANS/msos_p8_tester_release_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_distribution_quant_research_v2_relay.json",
        "docs/SOP/PHASE_PLANS/msos_production_wiring_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_user_state_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_workflow_persistence_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_snapshot_owner_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_access_identity_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_monitor_history_live_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_entitlements_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_mcd_production_witness_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_e2e_product_witness_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_usable_demo_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_self_serve_onboarding_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_options_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_tradeable_universe_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_sol_bybit_ship_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1a_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1b_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_equity_universe_tier1c_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_asset_display_parity_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_cross_venue_backtest_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_asset_enablement_pipeline_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json",
        "docs/SOP/PHASE_PLANS/horizon_chart_polish_v1_relay.json",
        "docs/SOP/PHASE_PLANS/horizon_region_workflow_v1_relay.json",
        "docs/SOP/PHASE_PLANS/horizon_replay_scrubber_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_trader_review_loop_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_cross_venue_strategy_lab_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_distribution_timeseries_collector_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_trust_surface_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_production_multi_asset_witness_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json",
    }
    assert manifest.get("phasePlanPath") in allowed
    assert manifest["status"] in ("COMPLETE", "READY", "RUNNING", "BLOCKED")
    if manifest["status"] == "RUNNING" and manifest.get("phasePlanPath") == SPRINT003_PLAN:
        summary = resolve_summary(REPO)
        assert summary["errors"] == []


def test_closed_chapter_queue_rows_done_or_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    for plan_path in (SPRINT003_PLAN, POST_PHASE3_PLAN):
        row = next(item for item in queue["items"] if item["planPath"] == plan_path)
        assert row["status"] in ("READY", "DONE")
