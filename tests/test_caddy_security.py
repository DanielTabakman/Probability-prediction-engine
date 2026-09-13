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


def _options_market_read_handle(snippets: str) -> str:
    start = snippets.index("@options_market_read path /v1/options-market-read")
    rest = snippets[start:]
    handle_at = rest.index("handle @options_market_read")
    block = rest[handle_at:]
    end = block.index("\n\t}")
    return block[: end + 3]


def test_options_market_read_exact_proxy_preserves_path() -> None:
    snippets = (REPO_ROOT / "caddy" / "snippets.caddy").read_text(encoding="utf-8")
    assert "@options_market_read path /v1/options-market-read" in snippets
    assert "path /v1/*" not in snippets
    assert "path /v1/options-market-read/*" not in snippets
    handle = _options_market_read_handle(snippets)
    assert "reverse_proxy ppe_display_api:8765" in handle
    assert "strip_prefix" not in handle
    display_start = snippets.index("@ppe_display_api path /ppe-display-api /ppe-display-api/*")
    display_block = snippets[display_start : snippets.index("@options_market_read")]
    assert "uri strip_prefix /ppe-display-api" in display_block
    assert "reverse_proxy ppe_display_api:8765" in display_block
