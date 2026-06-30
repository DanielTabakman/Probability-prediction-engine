"""MSOS Strategy Lab distribution CSV download — product slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
SOP = REPO_ROOT / "docs" / "SOP"

PROOF_ASSETS = ("BTC", "NVDA")


def test_distribution_export_route_proxies_upstream() -> None:
    route = (
        MSOS_WEB / "src" / "app" / "api" / "ppe-display-api" / "distribution-export" / "route.ts"
    )
    lib = MSOS_WEB / "src" / "lib" / "distributionExportUpstream.ts"
    assert route.is_file()
    assert lib.is_file()
    route_text = route.read_text(encoding="utf-8")
    lib_text = lib.read_text(encoding="utf-8")
    assert "buildDistributionExportUpstreamUrl" in route_text
    assert "buildDistributionExportUpstreamUrl" in lib_text
    assert "PPE_DISPLAY_API_SERVER_URL" in lib_text
    assert "distribution-export.csv" in lib_text
    assert "text/csv" in route_text
    assert "Content-Disposition" in route_text
    assert "distribution_export_error" in route_text
    assert "Math." not in route_text


def test_strategy_lab_content_download_button_and_honest_copy() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    assert "Download distribution stats (CSV)" in content
    assert "/api/ppe-display-api/distribution-export" in content
    assert "LAB_ASSET_QUERY_PARAM" in content
    assert "StrategyLabClientShell" in content
    assert "Simulation and paper workflows only" in content
    assert "Sample mode" in content
    assert "aria-disabled" in content
    assert "lab-export-toolbar" in content


def test_distribution_export_asset_param_witness_btc_and_nvda() -> None:
    content = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    lib = (MSOS_WEB / "src" / "lib" / "distributionExportUpstream.ts").read_text(encoding="utf-8")
    for asset in PROOF_ASSETS:
        assert asset in content or "asset" in content.lower()
    assert "encodeURIComponent" in lib
    assert "LAB_ASSET_QUERY_PARAM" in lib


def test_distribution_download_sprint_and_phase_plan_touch_set() -> None:
    sprint = (SOP / "SPRINT_MSOS_STRATEGY_LAB_DIST_DOWNLOAD_V1.md").read_text(encoding="utf-8")
    plan = (SOP / "PHASE_PLANS" / "msos_strategy_lab_dist_download_v1_relay.json").read_text(
        encoding="utf-8"
    )
    assert "MSOS-DistDl-Product-Slice002" in sprint
    assert "Download button" in sprint
    assert "MSOS-DistDl-Product-Slice002" in plan
    assert "distribution-export/route.ts" in plan
    assert "test_msos_web_distribution_download.py" in plan


def test_distribution_export_public_api_path_contract() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "distributionExportUpstream.ts").read_text(encoding="utf-8")
    assert "/ppe-display-api/distribution-export.csv" in lib
