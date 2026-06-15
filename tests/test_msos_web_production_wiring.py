"""MSOS production wiring v1 — product slice witness (sign-in, CTA, nav)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"
LIB = MSOS_WEB / "src" / "lib"


def _load_ts_module(path: Path, module_name: str):
    """Load a small TS module by transpiling via exec of extracted logic — use file content checks."""
    return path.read_text(encoding="utf-8")


def test_msos_public_urls_default_sign_in() -> None:
    text = _load_ts_module(LIB / "msosPublicUrls.ts", "msosPublicUrls")
    assert "DEFAULT_SIGN_IN_URL" in text
    assert "https://app.marketstructureos.com" in text
    assert "NEXT_PUBLIC_MSOS_SIGN_IN_URL" in text


def test_research_offer_cta_env_pattern() -> None:
    text = _load_ts_module(LIB / "researchOfferCta.ts", "researchOfferCta")
    assert "NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL" in text
    assert "mailto:" in text
    assert "Request research beta access" in text


def test_public_nav_wired_sign_in_and_routes() -> None:
    nav = (MSOS_WEB / "src" / "components" / "PublicNav.tsx").read_text(encoding="utf-8")
    assert "resolveSignInUrl" in nav
    assert 'href={signInUrl}' in nav or "href={signInUrl}" in nav
    assert 'href="/strategy-lab"' in nav or "MSOS_ROUTES.strategyLab" in nav
    assert "<span className=\"btn slim dark\">Sign in</span>" not in nav


def test_hero_research_offer_and_links() -> None:
    hero = (MSOS_WEB / "src" / "components" / "HeroSection.tsx").read_text(encoding="utf-8")
    assert "resolveResearchOfferCta" in hero
    assert "MSOS_ROUTES.strategyLab" in hero
    assert "MSOS_ROUTES.commandCenter" in hero
    assert '<span className="btn primary">' not in hero


def test_strategy_lab_embed_boundary_present() -> None:
    lab = (MSOS_WEB / "src" / "components" / "StrategyLabContent.tsx").read_text(encoding="utf-8")
    embed = (MSOS_WEB / "src" / "components" / "PpeEmbedBoundary.tsx").read_text(encoding="utf-8")
    assert "PpeEmbedBoundary" in lab
    assert "NEXT_PUBLIC_PPE_EMBED_URL" in embed


def test_app_sidebar_nav_routes() -> None:
    fixtures = (MSOS_WEB / "src" / "data" / "commandCenterFixtures.ts").read_text(encoding="utf-8")
    assert 'href: "/command-center"' in fixtures
    assert 'href: "/strategy-lab"' in fixtures
    assert 'href: "/monitor"' in fixtures
    assert 'href: "/history"' in fixtures
    assert 'href: "/learn"' in fixtures
