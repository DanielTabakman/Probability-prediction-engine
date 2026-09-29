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
    assert "secondaryNavItems" in sidebar

    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "secondaryNavItems" in content
    assert "More tools" in content
    assert "command-more-tools" in content
    assert content.count('className="btn slim primary"') == 1
    assert "resolveHeroPrimary" in content
    assert "MSOS_ROUTES.history" in content
    assert "command-hero-secondary" in content
    assert "buildCalibrationStrip" in content
    assert "friendlySnapshotFeedMessage" in content
    assert "DEMO_FOOTER" in content
    assert "module-card-grid" not in content
    assert "moduleCards" not in content
    assert "resumeItems" in content
    assert "headlines" not in content
    assert "buildReviewEvents" not in content


def test_command_center_calibration_strip_from_live_summary() -> None:
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "buildCalibrationStrip" in content
    assert "calibrationStrip.title" in content


def test_public_nav_links_to_command_center() -> None:
    nav = (MSOS_WEB / "src" / "components" / "PublicNav.tsx").read_text(encoding="utf-8")
    assert 'href="/command-center"' in nav or "MSOS_ROUTES.commandCenter" in nav
    assert "Enter Command Center" in nav or "Command Center" in nav


def test_command_center_fixtures_honest_labels() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert "moduleCards" in fixtures
    assert "secondaryNavItems" in fixtures
    assert 'href: "/exposure"' in fixtures
    assert 'href: "/options-horizon"' in fixtures
    assert 'href: "/forward-consistency"' in fixtures
    assert 'href: "/learn"' in fixtures
    assert "live: true" in fixtures
    assert "Planned" in fixtures
    assert "plannedModules" in fixtures
