"""MSOS P2 homepage scaffold witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_msos_web_package_and_homepage_copy() -> None:
    assert (MSOS_WEB / "package.json").is_file()
    assert (MSOS_WEB / "src" / "app" / "page.tsx").is_file()
    page = (MSOS_WEB / "src" / "app" / "page.tsx").read_text(encoding="utf-8")
    hero = (MSOS_WEB / "src" / "components" / "HeroSection.tsx").read_text(encoding="utf-8")
    assert "HeroSection" in page
    assert "Market Structure OS" in hero
    assert "Strategy Lab" in hero
    assert "PPE" in hero
    assert "Planned" in hero


def test_msos_web_docker_and_compose_wiring() -> None:
    assert (MSOS_WEB / "Dockerfile").is_file()
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    caddy = (REPO_ROOT / "Caddyfile").read_text(encoding="utf-8")
    assert "msos_web:" in compose
    assert "msos_web:3000" in caddy


def test_msos_web_research_beta_cta_wiring() -> None:
    """PublicLaunchV1 Product Slice003 — env-driven research beta CTA on homepage."""
    lib = (MSOS_WEB / "src" / "lib" / "researchOfferCta.ts").read_text(encoding="utf-8")
    page = (MSOS_WEB / "src" / "app" / "page.tsx").read_text(encoding="utf-8")
    hero = (MSOS_WEB / "src" / "components" / "HeroSection.tsx").read_text(encoding="utf-8")
    nav = (MSOS_WEB / "src" / "components" / "PublicNav.tsx").read_text(encoding="utf-8")
    readme = (MSOS_WEB / "README.md").read_text(encoding="utf-8")

    assert "PPE_RESEARCH_OFFER_URL" in lib
    assert "PPE_RESEARCH_OFFER_LABEL" in lib
    assert "mailto:" in lib
    assert "resolveResearchOfferCta" in page
    assert "researchOffer" in hero
    assert "researchOffer" in nav
    assert "decision support only" in lib
    assert "PPE_RESEARCH_OFFER_URL" in readme
