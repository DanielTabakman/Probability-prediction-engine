"""MSOS P3 Command Center scaffold witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_command_center_route_and_shell() -> None:
    page = MSOS_WEB / "src" / "app" / "command-center" / "page.tsx"
    assert page.is_file()
    text = page.read_text(encoding="utf-8")
    assert "AppShell" in text
    assert "CommandCenterContent" in text

    sidebar = (MSOS_WEB / "src" / "components" / "AppSidebar.tsx").read_text(encoding="utf-8")
    assert "navItems" in sidebar
    assert "connectedMarkets" in sidebar

    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "friendlySnapshotFeedMessage" in content
    assert "DEMO_FOOTER" in content
    assert "labTiles" in content
    assert "summary.kpis" in content


def test_public_nav_links_to_command_center() -> None:
    nav = (MSOS_WEB / "src" / "components" / "PublicNav.tsx").read_text(encoding="utf-8")
    nav_copy = (MSOS_WEB / "src" / "content" / "publicNav.ts").read_text(encoding="utf-8")
    assert 'href="/command-center"' in nav or "MSOS_ROUTES.commandCenter" in nav
    assert (
        "Enter Command Center" in nav
        or "Command Center" in nav
        or "Enter Command Center" in nav_copy
        or "enterCommandCenterCta" in nav
    )


def test_command_center_fixtures_honest_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert "Live" in fixtures or "Live" in fixtures.lower()
    assert "Planned" in fixtures
    assert "Soon" in fixtures
    assert "disabled: true" in fixtures
