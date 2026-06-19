"""MSOS end-to-end product witness v1 — journey route and wiring smoke."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
LIB = MSOS_WEB / "src" / "lib"
COMPONENTS = MSOS_WEB / "src" / "components"
APP = MSOS_WEB / "src" / "app"


def test_e2e_journey_routes_exist() -> None:
    routes = (
        APP / "page.tsx",
        APP / "strategy-lab" / "page.tsx",
        APP / "strategy-lab" / "confirm" / "page.tsx",
        APP / "strategy-lab" / "expression" / "page.tsx",
        APP / "command-center" / "page.tsx",
        APP / "monitor" / "page.tsx",
        APP / "history" / "page.tsx",
        APP / "learn" / "page.tsx",
    )
    for path in routes:
        assert path.is_file(), f"missing journey route: {path.relative_to(REPO_ROOT)}"


def test_e2e_public_nav_covers_journey_entry_points() -> None:
    nav = (COMPONENTS / "PublicNav.tsx").read_text(encoding="utf-8")
    routes = (LIB / "msosPublicUrls.ts").read_text(encoding="utf-8")
    assert "MSOS_ROUTES.strategyLab" in nav
    assert "MSOS_ROUTES.commandCenter" in nav
    assert "MSOS_ROUTES.monitor" in nav
    assert "MSOS_ROUTES.learn" in nav
    assert "resolveSignInUrl" in nav
    for segment in ("/strategy-lab", "/command-center", "/monitor", "/history", "/learn"):
        assert segment in routes


def test_e2e_homepage_research_and_lab_ctas() -> None:
    hero = (COMPONENTS / "HeroSection.tsx").read_text(encoding="utf-8")
    assert "resolveResearchOfferCta" in hero
    assert "MSOS_ROUTES.strategyLab" in hero
    assert "MSOS_ROUTES.commandCenter" in hero


def test_e2e_strategy_lab_embed_and_workflow_paths() -> None:
    lab = (COMPONENTS / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    embed = (COMPONENTS / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    confirm = (APP / "strategy-lab" / "confirm" / "page.tsx").read_text(encoding="utf-8")
    expression = (APP / "strategy-lab" / "expression" / "page.tsx").read_text(encoding="utf-8")
    assert "PpeEmbedBoundary" in lab
    assert "chromeless" in embed.lower() or "embed" in embed.lower()
    assert "confirm" in confirm.lower()
    assert "expression" in expression.lower()


def test_e2e_command_center_monitor_history_use_live_feeds() -> None:
    cc = (COMPONENTS / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    monitor = (COMPONENTS / "MonitorContent.tsx").read_text(encoding="utf-8")
    history = (COMPONENTS / "HistoryContent.tsx").read_text(encoding="utf-8")
    assert "buildCalibrationStrip" in cc or "loadCommandCenterSummary" in cc
    assert "monitoringFixtures" not in monitor
    assert "historyFixtures" not in history
    assert "feed." in monitor
    assert "feed." in history


def test_e2e_learn_page_reachable() -> None:
    learn = (APP / "learn" / "page.tsx").read_text(encoding="utf-8")
    assert "Learn" in learn or "learn" in learn
