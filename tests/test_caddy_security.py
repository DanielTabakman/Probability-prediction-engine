"""Caddy security snippets and Phase B TLS config witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _caddy_bundle() -> str:
    root = (REPO_ROOT / "Caddyfile").read_text(encoding="utf-8")
    snippets = (REPO_ROOT / "caddy" / "snippets.caddy").read_text(encoding="utf-8")
    return root + snippets


def test_security_headers_in_snippets() -> None:
    text = _caddy_bundle()
    assert "X-Content-Type-Options" in text
    assert "Referrer-Policy" in text
    assert "Permissions-Policy" in text


def test_msos_web_csp_in_snippets() -> None:
    text = (REPO_ROOT / "caddy" / "snippets.caddy").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in text
    assert "msos_web:3000" in text
    assert "msos_web_staging:3001" in text
    assert "staging.marketstructureos.com" in text


def test_caddyfile_tls_origin_cert_paths() -> None:
    tls = (REPO_ROOT / "Caddyfile.tls").read_text(encoding="utf-8")
    assert "cloudflare-origin.pem" in tls
    assert "hsts_header" in tls
    assert ":443" in tls


def test_compose_mounts_caddy_snippets_and_certs() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "PPE_CADDYFILE" in compose
    assert "./caddy:/etc/caddy/caddy:ro" in compose
    assert "./certs:/certs:ro" in compose
