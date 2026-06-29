"""Options Horizon region workflow v1 — MSOS persistence witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_horizon_region_api_route_exists() -> None:
    route = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "horizon-region" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "export async function GET" in route
    assert "export async function PUT" in route
    assert "requireProtectedIdentity" in route
    assert "upsertHorizonRegion" in route
    assert "getCurrentHorizonRegion" in route
    assert "getHorizonRegionById" in route


def test_horizon_region_client_calls_server_api() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "horizonRegion.ts").read_text(encoding="utf-8")
    assert "fetchHorizonRegion" in lib
    assert "persistHorizonRegion" in lib
    assert 'fetch("/api/theses/horizon-region"' in lib
    assert 'credentials: "include"' in lib
    assert "loadHorizonRegion" in lib


def test_horizon_region_workflow_store_supports_kind() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "upsertHorizonRegion" in lib
    assert "getCurrentHorizonRegion" in lib
    assert "horizonRegions" in lib
    assert '"horizon_region"' in lib or "'horizon_region'" in lib
    assert "horizonRegionId" in lib


def test_options_horizon_client_uses_server_persistence() -> None:
    client = (MSOS_WEB / "src" / "components" / "OptionsHorizonClient.tsx").read_text(
        encoding="utf-8"
    )
    assert "fetchHorizonRegion" in client
    assert "persistHorizonRegion" in client


def test_strategy_lab_deep_link_includes_region_id() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "horizonChartPayload.ts").read_text(encoding="utf-8")
    assert "region_id" in lib
    assert "regionId" in lib
