"""MSOS P2 homepage scaffold witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def _caddy_text() -> str:
    return (REPO_ROOT / "Caddyfile").read_text(encoding="utf-8") + (
        REPO_ROOT / "caddy" / "snippets.caddy"
    ).read_text(encoding="utf-8")


def test_msos_web_package_and_homepage_copy() -> None:
    assert (MSOS_WEB / "package.json").is_file()
    assert (MSOS_WEB / "src" / "app" / "page.tsx").is_file()
    page = (MSOS_WEB / "src" / "app" / "page.tsx").read_text(encoding="utf-8")
    hero = (MSOS_WEB / "src" / "components" / "HeroSection.tsx").read_text(encoding="utf-8")
    assert "HeroSection" in page
    assert "Turn your market thesis" in hero
    assert "strategyLabForcedTourHref" in hero or "strategyLabTutorialHref" in hero
    assert "ResearchBetaModal" in hero
    assert 'data-self-serve-entry="homepage"' in page


def test_msos_web_docker_and_compose_wiring() -> None:
    assert (MSOS_WEB / "Dockerfile").is_file()
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    caddy = _caddy_text()
    assert "msos_web:" in compose
    assert "msos_web:3000" in caddy


def test_hero_self_serve_ctas() -> None:
    hero = (MSOS_WEB / "src" / "components" / "HeroSection.tsx").read_text(encoding="utf-8")
    assert "Start guided tour" in hero
    assert "strategyLabForcedTourHref" in hero
    assert "BTC and ETH" in hero
    assert "BTC + ETH options live" in hero


def test_public_nav_restart_tour() -> None:
    nav = (MSOS_WEB / "src" / "components" / "PublicNav.tsx").read_text(encoding="utf-8")
    restart = (MSOS_WEB / "src" / "components" / "RestartTourButton.tsx").read_text(encoding="utf-8")
    assert "Restart tour" in nav
    assert "RestartTourButton" in nav
    assert "strategyLabForcedTourHref" in restart


def test_platform_tutorial_wiring() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "platformTutorial.ts").read_text(encoding="utf-8")
    assert "lab-asset" in lib
    assert "BTC or ETH" in lib
    shell = (MSOS_WEB / "src" / "components" / "StrategyLabClientShell.tsx").read_text(encoding="utf-8")
    picker = (MSOS_WEB / "src" / "components" / "LabAssetPicker.tsx").read_text(encoding="utf-8")
    assert "PlatformTutorial" in shell
    assert "LabAssetPicker" in shell
    assert 'data-tour="lab-asset"' in picker


def test_features_row_self_serve_entry() -> None:
    features = (MSOS_WEB / "src" / "components" / "FeaturesRow.tsx").read_text(encoding="utf-8")
    assert 'data-self-serve-entry="features"' in features
    assert "BTC and ETH" in features
    assert "beginner" in features


def test_expiry_context_strip_uses_asset_ticker() -> None:
    strip = (MSOS_WEB / "src" / "components" / "ExpiryMarketContextStrip.tsx").read_text(encoding="utf-8")
    assert "assetTicker" in strip


def test_belief_bounds_copy_explains_limits() -> None:
    copy = (MSOS_WEB / "src" / "lib" / "beliefTuningCopy.ts").read_text(encoding="utf-8")
    assert "BELIEF_TUNING_BOUNDS_NOTE" in copy
    assert "BELIEF_TAIL_LIMIT_NOTE" in copy
