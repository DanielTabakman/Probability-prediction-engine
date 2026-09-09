"""Region Bet contract v1 - MSOS persistence witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_region_bet_contract_schema_guard_covers_required_fields() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "regionBet.ts").read_text(encoding="utf-8")
    assert "export type RegionBetContract" in lib
    assert "schema_version: 1" in lib
    assert "asset_id" in lib
    assert "spot_usd" in lib
    assert "timestamp_utc" in lib
    assert "selected_region" in lib
    assert "target" in lib
    assert "market_snapshot" in lib
    assert "risk_constraints" in lib
    assert "selected_expression_ref" in lib
    assert "lifecycle" in lib
    assert "isRegionBetContract" in lib
    assert "Number.isFinite" in lib


def test_region_bet_client_calls_server_api() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "regionBet.ts").read_text(encoding="utf-8")
    assert "fetchRegionBet" in lib
    assert "persistRegionBet" in lib
    assert 'fetch("/api/theses/region-bet"' in lib
    assert 'credentials: "include"' in lib
    assert "loadRegionBet" in lib
    assert "REGION_BET_STORAGE_KEY" in lib


def test_region_bet_workflow_store_supports_kind_crud_and_current_pointer() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "StoredRegionBet" in lib
    assert '"region_bet"' in lib or "'region_bet'" in lib
    assert "regionBets" in lib
    assert "regionBetId" in lib
    assert "upsertRegionBet" in lib
    assert "getCurrentRegionBet" in lib
    assert "getRegionBetById" in lib
    assert "isRegionBetContract" in lib


def test_region_bet_api_route_fails_closed_and_requires_identity() -> None:
    route = (
        MSOS_WEB / "src" / "app" / "api" / "theses" / "region-bet" / "route.ts"
    ).read_text(encoding="utf-8")
    assert "export async function GET" in route
    assert "export async function PUT" in route
    assert "requireProtectedIdentity" in route
    assert "identity.email" in route
    assert "upsertRegionBet" in route
    assert "getCurrentRegionBet" in route
    assert "getRegionBetById" in route
    assert "missing region bet" in route
    assert "invalid region bet" in route
    assert "{ status: 400 }" in route


def test_region_bet_contract_does_not_recreate_later_bridge_surfaces() -> None:
    touched = (MSOS_WEB / "src" / "lib" / "regionBet.ts").read_text(encoding="utf-8")
    assert "OptionsExpressionFitRankingPanel" not in touched
    assert "OptionsHorizonComparison" not in touched
    assert "brokerage" not in touched.lower()
    assert "order ticket" not in touched.lower()
