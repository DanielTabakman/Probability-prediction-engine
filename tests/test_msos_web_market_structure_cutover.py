"""MSOS Market Structure Lab: human-facing research evidence and engine cutover."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
MISSION_CONTROL = MSOS_WEB / "src" / "app" / "operator" / "mission-control" / "page.tsx"
CAPTURE_PROBE = MSOS_WEB / "src" / "lib" / "signalCaptureProbe.ts"
STRUCTURE_PROBE = MSOS_WEB / "src" / "lib" / "marketStructureProbe.ts"
STRUCTURE_COMPONENT = MSOS_WEB / "src" / "components" / "MultiScaleStructureProbe.tsx"
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


def test_mission_control_leads_with_founder_research_loop() -> None:
    text = MISSION_CONTROL.read_text(encoding="utf-8")
    assert "Research / Founder View" in text
    assert "WHERE ARE WE?" in text
    assert "Searching for an edge" in text
    assert "WHAT ARE WE DOING NOW?" in text
    assert "WHAT SHOULD I DO?" in text
    assert "Detector minus control is the number that matters" in text
    assert "SEE PATTERN → PLAY WITH RULE → FIND SOMETHING INTERESTING → FREEZE IT → TEST ON NEW DATA" in text
    assert "Advanced / project details" in text
    assert text.index("<MarketStructureSandbox />") < text.index("Advanced / project details")


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


def test_research_summary_leads_with_primary_decision() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    evidence = EVIDENCE_COMPONENT.read_text(encoding="utf-8")
    state = RESEARCH_STATE.read_text(encoding="utf-8")
    assert "ResearchEvidenceSummary" in page
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
    assert "Read / share full V0 report (.md)" in page
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


def test_v0_lifecycle_blocks_strategy_and_hummingbot() -> None:
    page = MISSION_CONTROL.read_text(encoding="utf-8")
    state = RESEARCH_STATE.read_text(encoding="utf-8")
    assert "V0 LIFECYCLE" in page
    assert "V0 stops before strategy backtesting" in page
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
