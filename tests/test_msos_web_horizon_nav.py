"""MSOS trader workflow horizon nav v1 — cross-module nav witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
SOP = REPO_ROOT / "docs" / "SOP"

PROOF_ASSETS = ("BTC", "NVDA")


def test_app_nav_builds_asset_aware_horizon_and_lab_paths() -> None:
    nav = (MSOS_WEB / "src" / "components" / "AppNav.tsx").read_text(encoding="utf-8")
    assert "buildOptionsHorizonPath" in nav
    assert "buildStrategyLabPathWithAsset" in nav
    assert "assetAwareModuleHref" in nav
    assert "LAB_ASSET_QUERY_PARAM" in nav
    assert "MSOS_ROUTES.optionsHorizon" in nav
    assert "HorizonNavLink" in nav
    assert "HORIZON_REGION_TOUR_ANCHOR" in nav
    assert "HORIZON_REGION_TOUR_COPY" in nav
    assert "region" in nav.lower()


def test_command_center_links_to_options_horizon_with_asset() -> None:
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(
        encoding="utf-8"
    )
    assert "buildOptionsHorizonPath" in content
    assert "assetAwareModuleHref" in content
    assert "Options Horizon" in content
    assert "command-hero-secondary" in content


def test_strategy_lab_horizon_nav_toolbar_and_tour_hook() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(
        encoding="utf-8"
    )
    assert "HorizonNavLink" in content
    assert "lab-horizon-nav-toolbar" in content
    assert "HORIZON_REGION_TOUR_ANCHOR" in content
    assert "HORIZON_REGION_TOUR_COPY" in content
    assert "Open Options Horizon" in content


def test_horizon_nav_asset_param_witness_btc_and_nvda() -> None:
    nav = (MSOS_WEB / "src" / "components" / "AppNav.tsx").read_text(encoding="utf-8")
    for asset in PROOF_ASSETS:
        assert asset in nav or "DEFAULT_CROSS_MODULE_ASSET" in nav
    assert "encodeURIComponent" in nav
    assert "normalizeNavAssetId" in nav


def test_horizon_nav_sprint_and_phase_plan_touch_set() -> None:
    sprint = (SOP / "SPRINT_MSOS_TRADER_WORKFLOW_HORIZON_NAV_V1.md").read_text(encoding="utf-8")
    plan = (
        SOP / "PHASE_PLANS" / "msos_trader_workflow_horizon_nav_v1_relay.json"
    ).read_text(encoding="utf-8")
    assert "MSOS-HorizonNav-Product-Slice002" in sprint
    assert "Nav links" in sprint
    assert "MSOS-HorizonNav-Product-Slice002" in plan
    assert "AppNav.tsx" in plan
    assert "test_msos_web_horizon_nav.py" in plan
