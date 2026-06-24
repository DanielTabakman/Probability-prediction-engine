"""MSOS access identity v1 — product slice witness (scoped APIs + identity headers)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_msos_identity_module_exists() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosIdentity.ts").read_text(encoding="utf-8")
    core = (MSOS_WEB / "src" / "lib" / "msosIdentityCore.ts").read_text(encoding="utf-8")
    auth = (MSOS_WEB / "src" / "lib" / "msosWorkflowAuth.ts").read_text(encoding="utf-8")
    assert "requireProtectedIdentity" in lib
    assert "resolveMsosIdentityFromHeaders" in core
    assert "cf-access-authenticated-user-email" in core
    assert "authentication required" in auth


def test_protected_api_routes_require_identity() -> None:
    routes = [
        MSOS_WEB / "src" / "app" / "api" / "theses" / "route.ts",
        MSOS_WEB / "src" / "app" / "api" / "theses" / "expression" / "route.ts",
        MSOS_WEB / "src" / "app" / "api" / "theses" / "summary" / "route.ts",
        MSOS_WEB / "src" / "app" / "api" / "command-center" / "summary" / "route.ts",
    ]
    for route in routes:
        text = route.read_text(encoding="utf-8")
        assert "requireProtectedIdentity" in text
        assert "identity.ok" in text


def test_workflow_store_scopes_by_owner() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "msosWorkflowStore.ts").read_text(encoding="utf-8")
    assert "ownerEmail" in lib
    assert "currentByOwner" in lib
    assert "getCurrentThesis(ownerEmail" in lib
    assert "loadWorkflowSummary(ownerEmail" in lib
    assert "normalizeOwnerEmail" in lib


def test_command_center_summary_accepts_owner_filter() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "commandCenterSummary.ts").read_text(encoding="utf-8")
    assert "loadCommandCenterSummary(ownerEmail" in lib
    assert "owner_email" in lib
    assert "ownerFilter" in lib


def test_homepage_route_stays_public() -> None:
    page = (MSOS_WEB / "src" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "HeroSection" in page
    assert "requireProtectedIdentity" not in page
