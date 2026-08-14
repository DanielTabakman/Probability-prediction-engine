"""MSOS Mission Control cutover: capture health vs market-structure.v1."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
MISSION_CONTROL = MSOS_WEB / "src" / "app" / "operator" / "mission-control" / "page.tsx"
CAPTURE_PROBE = MSOS_WEB / "src" / "lib" / "signalCaptureProbe.ts"
STRUCTURE_PROBE = MSOS_WEB / "src" / "lib" / "marketStructureProbe.ts"
STRUCTURE_COMPONENT = MSOS_WEB / "src" / "components" / "MultiScaleStructureProbe.tsx"
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


def test_structure_component_separates_unavailable_from_insufficient() -> None:
    text = STRUCTURE_COMPONENT.read_text(encoding="utf-8")
    assert "Market structure engine unavailable" in text
    assert "fit_reason" in text
    assert "INSUFFICIENT" not in text or "scale.fit" in text
    assert "ndax_15m.multiscale" not in text
    assert "ndax15m.multiscale" not in text


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
        MSOS_WEB / "src" / "data" / "operatingLoopProbe.ts",
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert "ndax_15m.multiscale" not in blob
    assert "ndax15m.multiscale" not in blob
    assert "ndax?.multiscale" not in blob
