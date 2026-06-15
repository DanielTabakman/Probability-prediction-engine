"""MSOS production wiring v1 — platform slice witness (compose, Caddy, Dockerfile)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_msos_web_dockerfile_next_public_build_args() -> None:
    dockerfile = (REPO_ROOT / "apps" / "msos-web" / "Dockerfile").read_text(encoding="utf-8")
    for key in (
        "NEXT_PUBLIC_MSOS_SIGN_IN_URL",
        "NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL",
        "NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL",
        "NEXT_PUBLIC_PPE_EMBED_URL",
    ):
        assert key in dockerfile


def test_compose_msos_web_build_args_and_embed_default() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_MSOS_SIGN_IN_URL" in compose
    assert "NEXT_PUBLIC_PPE_EMBED_URL" in compose
    assert "/ppe-embed" in compose
    assert "PPE_RESEARCH_OFFER_URL" in compose


def test_caddy_ppe_embed_proxy_to_app_demo() -> None:
    caddy = (REPO_ROOT / "Caddyfile").read_text(encoding="utf-8")
    assert "/ppe-embed" in caddy
    assert "app_demo:8501" in caddy
    assert "strip_prefix /ppe-embed" in caddy
