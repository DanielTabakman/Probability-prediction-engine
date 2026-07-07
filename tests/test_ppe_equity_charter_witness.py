"""Charter witness for PPE equity options v1 (Control-Slice001)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

EQUITY_PLAN = SOP / "PHASE_PLANS" / "ppe_equity_options_v1_relay.json"
EQUITY_SPRINT = SOP / "SPRINT_PPE_EQUITY_OPTIONS_V1.md"
EQUITY_SELECTION = SOP / "POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md"
EQUITY_EVIDENCE = SOP / "PPE_EQUITY_OPTIONS_V1_EVIDENCE_STATUS.md"
EQUITY_ADR = SOP / "PPE_EQUITY_OPTIONS_ADAPTER_ADR.md"
MANIFEST = SOP / "ACTIVE_PHASE_MANIFEST.json"


def test_equity_charter_artifacts_exist() -> None:
    for path in (EQUITY_PLAN, EQUITY_SPRINT, EQUITY_SELECTION, EQUITY_EVIDENCE, EQUITY_ADR):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_equity_phase_plan_valid() -> None:
    plan = json.loads(EQUITY_PLAN.read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "PPE-Equity-Control-Slice001"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "ppe_equity_options_v1"


def test_equity_adr_documents_nvda_scaffold() -> None:
    body = EQUITY_ADR.read_text(encoding="utf-8")
    assert "NVDA" in body
    assert "enabled: false" in body
    assert "venue: equity" in body


def test_equity_chapter_closed_queue_and_manifest() -> None:
    queue = json.loads((SOP / "PHASE_QUEUE.json").read_text(encoding="utf-8"))
    row = next(
        item for item in queue["items"]
        if item.get("planPath") == "docs/SOP/PHASE_PLANS/ppe_equity_options_v1_relay.json"
    )
    assert row["status"] == "DONE"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    status = str(manifest.get("status") or "").upper()
    plan = str(manifest.get("phasePlanPath") or "").strip()
    allowed = (
        "docs/SOP/PHASE_PLANS/ppe_tradeable_universe_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json",
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
        "docs/SOP/PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_trust_surface_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_production_multi_asset_witness_v1_relay.json",
        "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_trader_review_loop_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_cross_venue_strategy_lab_v1_relay.json",
        "docs/SOP/PHASE_PLANS/mvp1_distribution_timeseries_collector_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json",
        "docs/SOP/PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json",
    )
    assert status in ("READY", "RUNNING", "COMPLETE", "BLOCKED")
    if status == "COMPLETE":
        assert plan == "" or plan in allowed
    else:
        assert plan in allowed


def test_equity_sprint_complete_not_deferred() -> None:
    body = EQUITY_SPRINT.read_text(encoding="utf-8")
    assert "DEFERRED" not in body.split("## Sprint status")[0]
    assert "COMPLETE" in body
