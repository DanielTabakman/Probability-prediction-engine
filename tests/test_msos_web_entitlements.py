"""MSOS entitlements v1 — product slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_msos_entitlements_lib_exists() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosEntitlements.ts").read_text(encoding="utf-8")
    assert "getOrCreateEntitlement" in lib
    assert "checkEntitlementGate" in lib
    assert "msos_entitlements" in lib
    assert "stripe_customer_id" in lib
    assert "appendUpgradeRequest" in lib
    assert "MSOS_UPGRADE_OFFER_URL" in lib


def test_entitlements_api_routes_require_identity() -> None:
    me = (MSOS_WEB / "src" / "app" / "api" / "entitlements" / "me" / "route.ts").read_text(
        encoding="utf-8"
    )
    upgrade = (
        MSOS_WEB / "src" / "app" / "api" / "entitlements" / "upgrade-request" / "route.ts"
    ).read_text(encoding="utf-8")
    for route in (me, upgrade):
        assert "requireProtectedIdentity" in route
        assert "identity.ok" in route


def test_app_sidebar_shows_tier_badge() -> None:
    sidebar = (MSOS_WEB / "src" / "components" / "AppSidebar.tsx").read_text(encoding="utf-8")
    shell = (MSOS_WEB / "src" / "components" / "AppShell.tsx").read_text(encoding="utf-8")
    assert "tierLabel" in sidebar
    assert "entitlement-badge" in sidebar
    assert "Upgrade" in sidebar
    assert "getOrCreateEntitlement" in shell


def test_entitlement_tiers_documented_in_adr() -> None:
    adr = (REPO_ROOT / "docs" / "SOP" / "MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md").read_text(
        encoding="utf-8"
    )
    assert "`free`" in adr
    assert "`research_beta`" in adr
    assert "`paid`" in adr
