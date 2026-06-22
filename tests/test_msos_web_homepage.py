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
    content = (MSOS_WEB / "src" / "content" / "homepage.ts").read_text(encoding="utf-8")
    assert "HeroSection" in page
    assert "homepageHero" in hero
    assert "Market Structure OS" in content
    assert "Turn your market thesis" in content
    assert "Probability Engine" in content
    assert "Strategy Lab" in content
    assert "Coming" in content


def test_msos_web_docker_and_compose_wiring() -> None:
    assert (MSOS_WEB / "Dockerfile").is_file()
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    caddy = (REPO_ROOT / "Caddyfile").read_text(encoding="utf-8")
    assert "msos_web:" in compose
    assert "msos_web:3000" in caddy
