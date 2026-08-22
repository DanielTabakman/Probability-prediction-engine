"""MSOS Market Structure Workstation: human-facing research evidence and engine cutover."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
MISSION_CONTROL = MSOS_WEB / "src" / "app" / "operator" / "mission-control" / "page.tsx"
CAPTURE_PROBE = MSOS_WEB / "src" / "lib" / "signalCaptureProbe.ts"
STRUCTURE_PROBE = MSOS_WEB / "src" / "lib" / "marketStructureProbe.ts"
STRUCTURE_COMPONENT = MSOS_WEB / "src" / "components" / "MultiScaleStructureProbe.tsx"
ACTIVE_EXPERIMENT_COMPONENT = MSOS_WEB / "src" / "components" / "ActiveExperimentStatus.tsx"
ACTIVE_EXPERIMENT_ROUTE = MSOS_WEB / "src" / "app" / "api" / "market-structure" / "exp001a" / "status" / "route.ts"
SANDBOX_COMPONENT = MSOS_WEB / "src" / "components" / "MarketStructureSandbox.tsx"
SANDBOX_DATA = MSOS_WEB / "src" / "data" / "marketStructureSandboxData.ts"
SANDBOX_ROUTE = MSOS_WEB / "src" / "app" / "api" / "market-structure" / "sandbox-replay" / "route.ts"
EVIDENCE_COMPONENT = MSOS_WEB / "src" / "components" / "ResearchEvidenceSummary.tsx"
EXPERIMENT_COMPONENT = MSOS_WEB / "src" / "components" / "ResearchExperimentPanel.tsx"
RESEARCH_STATE = MSOS_WEB / "src" / "data" / "operatingLoopProbe.ts"
V0_REPORT = MSOS_WEB / "public" / "docs" / "market-structure-v0-report.md"
COMPOSE = REPO_ROOT / "docker-compose.yml"
STAGING_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-vps-staging.yml"


def test_mission_control_loads_capture_and_engine_separately() -> None:
    text = MISSION_CONTROL.read_text(encoding="utf-8")
    assert "loadSignalCaptureProbeState" in text
    assert "loadMarketStructureProbeState" in text
    assert "structure.payload" in text
    assert "ndax?.multiscale" not in text
    assert "ndax15m.multiscale" not in text
    assert "ndax_15m.multiscale" not in text


def test_mission_control_is_workstation_not_wall_of_telemetry() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    assert "Market Structure / Workstation" in page
    assert "Market Structure Workstation" in page
    assert 'href="#desk"' in page
    assert 'href="#live"' in page
    assert 'href="#experiments"' in page
    assert 'href="#sandbox"' in page
    assert 'href="#infrastructure"' in page
    assert 'href="#evidence"' in page
    assert "DESK · WHAT MATTERS NOW" in page
    assert "LIVE MARKET" in page
    assert "EXPERIMENTS" in page
    assert "SANDBOX · EXPLORATION" in page
    assert "INFRASTRUCTURE" in page
    assert "EVIDENCE & HISTORY" in page
    assert "Current mission: collect clean forward evidence." in page
    assert "What does the engine see right now?" in page
    assert "Turn the dials and see what changes." in page
    assert "ActiveExperimentStatus" in page
    assert "MarketStructureSandbox" in page
    assert "MultiScaleStructureProbe" in page
    assert "ResearchExperimentPanel" in page
    assert page.index('id="desk"') < page.index('id="live"')
    assert page.index('id="live"') < page.index('id="experiments"')
    assert page.index('id="experiments"') < page.index('id="sandbox"')
    assert page.index('id="sandbox"') < page.index('id="infrastructure"')
    assert page.index('id="infrastructure"') < page.index('id="evidence"')
    assert "LANE 6 · PRODUCTIZATION" not in page
    assert "THE WHOLE PROJECT" not in page


def test_active_exp001a_status_is_visible_without_exposing_engine_token() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    component = ACTIVE_EXPERIMENT_COMPONENT.read_text(encoding="utf-8")
    route = ACTIVE_EXPERIMENT_ROUTE.read_text(encoding="utf-8")
    assert "ActiveExperimentStatus" in page
    assert "ACTIVE EXPERIMENT · EXP-001A" in component
    assert "Frozen-zone forward validation" in component
    assert 'fetch("/api/market-structure/exp001a/status"' in component
    assert "15m / 1h / 4h / 1d" in component
    assert "WAIT FOR EVIDENCE" in component
    assert '"/v1/research/exp001a/status"' in route
    assert "MARKET_STRUCTURE_ENGINE_TOKEN" in route
    assert "Authorization" in route
    assert "Bearer ${config.token}" in route
    assert "MARKET_STRUCTURE_ENGINE_TOKEN" not in component


def test_capture_probe_strips_legacy_multiscale() -> None:
    text = CAPTURE_PROBE.read_text(encoding="utf-8")
    assert "function captureHealthFromNdax" in text
    assert "multiscale: _ignored" in text
    assert "OCT_SIGNAL_CAPTURE_STATUS_URL" in text
    assert "analyze_multiscale" not in text
    assert "MARKET_STRUCTURE_ENGINE_URL" not in text


def test_engine_client_consumes_v1_contract() -> None:
    text = STRUCTURE_PROBE.read_text(encoding="utf-8")
    assert 'SCHEMA_VERSION = "market-structure.v1"' in text
    assert "/v1/structure/latest" in text
    assert "application/vnd.market-structure.v1+json" in text
    assert "MARKET_STRUCTURE_ENGINE_URL" in text
    assert "MARKET_STRUCTURE_ENGINE_TOKEN" in text
    assert "parseMarketStructureV1" in text
    assert "INSUFFICIENT" in text
    assert "UNAVAILABLE" in text
    assert "NOT CONFIGURED" in text
    assert "127.0.0.1:8767" not in text
    assert "threshold" not in text.lower()


def test_structure_component_separates_live_detection_from_validation() -> None:
    text = STRUCTURE_COMPONENT.read_text(encoding="utf-8")
    assert "Market structure engine unavailable" in text
    assert "fit_reason" in text
    assert "detected structure is not the same thing as validated predictive value" in text
    assert "candidate levels" in text.lower()
    assert "ndax_15m.multiscale" not in text
    assert "ndax15m.multiscale" not in text


def test_sandbox_is_interactive_without_reopening_v0() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    sandbox = SANDBOX_COMPONENT.read_text(encoding="utf-8")
    assert "MarketStructureSandbox" in page
    assert "SANDBOX · EXPLORATORY ONLY · V0 STAYS LOCKED" in sandbox
    assert "Move the dials, then replay the actual price paths" in sandbox
    assert "Reset to V0" in sandbox
    assert "Copy candidate hypothesis" in sandbox
    assert "Replay raw paths" in sandbox
    assert "useState(25)" in sandbox
    assert "useState(2)" in sandbox
    assert "freeze" in sandbox.lower() and "fresh evaluation sample" in sandbox


def test_sandbox_exposes_real_touch_horizon_and_directionality_controls() -> None:
    sandbox = SANDBOX_COMPONENT.read_text(encoding="utf-8")
    route = SANDBOX_ROUTE.read_text(encoding="utf-8")
    assert "Touch distance" in sandbox
    assert "Outcome horizon" in sandbox
    assert "Forward window" in sandbox
    assert 'value="reaction"' in sandbox
    assert 'value="rejection"' in sandbox
    assert 'value="breakout"' in sandbox
    assert 'value="continuation"' in sandbox
    assert "RawPathChart" in sandbox
    assert "whipsaw" in sandbox.lower()
    assert 'fetch("/api/market-structure/sandbox-replay"' in sandbox
    assert "touch_bps" in sandbox
    assert "outcome_horizon_seconds" in sandbox
    assert "outcome_mode" in sandbox
    assert '"/v1/research/sandbox-replay"' in route
    assert "MARKET_STRUCTURE_ENGINE_TOKEN" in route
    assert "Authorization" in route
    assert "Bearer ${config.token}" in route


def test_sandbox_default_reproduces_locked_v0_counts() -> None:
    raw = SANDBOX_DATA.read_text(encoding="utf-8")
    marker = "export const SANDBOX_ROWS: MarketStructureSandboxRow[] = "
    rows_text = raw.split(marker, maxsplit=1)[1].strip().removesuffix(";")
    rows = ast.literal_eval(rows_text)
    assert len(rows) == 225
    detector_touched = [row for row in rows if row[6] == 1]
    baseline_touched = [row for row in rows if row[8] == 1]
    assert len(detector_touched) == 144
    assert len(baseline_touched) == 137
    assert sum(row[7] >= 25 for row in detector_touched) == 24
    assert sum(row[9] >= 25 for row in baseline_touched) == 26


def test_research_summary_remains_available_as_collapsed_audit_detail() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    evidence = EVIDENCE_COMPONENT.read_text(encoding="utf-8")
    state = RESEARCH_STATE.read_text(encoding="utf-8")
    assert "ResearchEvidenceSummary" in page
    assert "Full V0 evidence / audit details" in page
    assert "Primary V0 result" in page
    assert "RESEARCH DECISION" in evidence
    assert "Do not promote v0 to Hummingbot" in evidence
    assert "PRIMARY EVIDENCE" in evidence
    assert "The ZIP is for audit/reproduction" in evidence
    assert "V0 did not demonstrate an edge" in state
    assert "NOT VALIDATED" in state
    assert "0.1667" in state
    assert "0.1898" in state
    assert "-0.0231" in state
    assert "-0.105642" in state
    assert "0.058834" in state
    assert "168" in state


def test_v0_full_report_is_shareable_from_control_panel() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    report = V0_REPORT.read_text(encoding="utf-8")
    assert 'href="/docs/market-structure-v0-report.md"' in page
    assert "Open full V0 report" in page
    assert "# Market Structure V0 — Full Project Report" in report
    assert "NOT VALIDATED / NO EDGE DEMONSTRATED" in report
    assert "168 / 168" in report
    assert "16.67%" in report
    assert "18.98%" in report
    assert "−2.31 percentage points" in report
    assert "HUMMINGBOT" in report.upper()


def test_v0_experiment_loop_is_closed_not_rerunnable_from_ui() -> None:
    panel = EXPERIMENT_COMPONENT.read_text(encoding="utf-8")
    assert "V0 TESTING · COMPLETE" in panel
    assert "We are not running more v0 tests from this page" in panel
    assert "result-chasing" in panel
    assert "Run prospective holdout v0" not in panel
    assert "method: \"POST\"" not in panel
    assert "ndax-1786818000-d6f199ca8ba2" in panel
    assert "not evidence for or against the hypothesis" in panel


def test_strategy_and_hummingbot_remain_blocked_after_v0() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    state = RESEARCH_STATE.read_text(encoding="utf-8")
    assert "HUMMINGBOT" in page
    assert "DOWNSTREAM" in page
    assert "STRATEGY / HUMMINGBOT" in page
    assert "BLOCKED" in page
    assert "LIVE TRADING" in page
    assert "OFF" in page
    assert 'status: "blocked"' in state
    assert "BLOCKED FOR V0" in state
    assert "Archive v0 as NOT VALIDATED / NO EDGE DEMONSTRATED" in state


def test_staging_compose_and_workflow_wire_engine_env() -> None:
    compose = COMPOSE.read_text(encoding="utf-8")
    workflow = STAGING_WORKFLOW.read_text(encoding="utf-8")
    assert "MARKET_STRUCTURE_ENGINE_URL=${MARKET_STRUCTURE_ENGINE_URL:-}" in compose
    assert "MARKET_STRUCTURE_ENGINE_TOKEN=${MARKET_STRUCTURE_ENGINE_TOKEN:-}" in compose
    assert "secrets.MARKET_STRUCTURE_ENGINE_URL" in workflow
    assert "secrets.MARKET_STRUCTURE_ENGINE_TOKEN" in workflow
    assert "deploy-vps.yml" not in workflow
    assert "msos_web:" in compose
    assert "msos_web_staging:" in compose


def test_no_active_mission_control_multiscale_dependency() -> None:
    files = [
        MISSION_CONTROL,
        CAPTURE_PROBE,
        STRUCTURE_PROBE,
        STRUCTURE_COMPONENT,
        RESEARCH_STATE,
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert "ndax_15m.multiscale" not in blob
    assert "ndax15m.multiscale" not in blob
    assert "ndax?.multiscale" not in blob
