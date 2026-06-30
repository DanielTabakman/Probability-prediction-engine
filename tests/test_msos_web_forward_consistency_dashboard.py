"""MSOS forward consistency dashboard witness (MSOS-FCR-Product-Slice002)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_forward_consistency_route_and_shell() -> None:
    page = MSOS_WEB / "src" / "app" / "forward-consistency" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "AppShell" in text
    assert 'activeNavId="forward-consistency"' in text
    assert "ForwardConsistencyDashboardContent" in text


def test_forward_consistency_dashboard_content() -> None:
    content = (
        MSOS_WEB / "src" / "components" / "ForwardConsistencyDashboardContent.tsx"
    ).read_text(encoding="utf-8")
    assert "fetchForwardConsistencyDashboard" in content
    assert "fcr-heatmap" in content
    assert "kpi-row" in content
    assert "ForwardConsistencyPanel" in content
    assert "buildStrategyLabPathWithAssetAndExpiry" in content
    assert "Raw JSON" in content


def test_forward_consistency_lib_dashboard_types() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "forwardConsistency.ts").read_text(encoding="utf-8")
    assert "ForwardConsistencyDashboardPayload" in lib
    assert "fetchForwardConsistencyDashboard" in lib
    assert "DEMO_FORWARD_CONSISTENCY_DASHBOARD" in lib
    assert "forward-consistency/dashboard.json" in lib


def test_forward_consistency_nav_fixture() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(
        encoding="utf-8"
    )
    assert "forward-consistency" in fixtures
    assert "/forward-consistency" in fixtures


def test_forward_consistency_public_route_constant() -> None:
    routes = (MSOS_WEB / "src" / "lib" / "msosPublicUrls.ts").read_text(encoding="utf-8")
    assert "forwardConsistency" in routes
    assert '"/forward-consistency"' in routes
