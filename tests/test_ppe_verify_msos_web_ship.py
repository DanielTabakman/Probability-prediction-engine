"""Tests for MSOS web ship verification (stale bundle gate)."""

from __future__ import annotations

import scripts.verify_msos_web_ship as ship


def test_verify_strategy_lab_client_bundle_rejects_stale() -> None:
    html = '<script src="/_next/static/chunks/app/strategy-lab/page-stale.js"></script>'

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("page-stale.js"):
            return 200, "Options market Reference curve", None
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_strategy_lab_client_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is False
    assert "stale" in (err or "")


def test_verify_strategy_lab_client_bundle_accepts_labeled_axes() -> None:
    html = '<script src="/_next/static/chunks/app/strategy-lab/page-new.js"></script>'

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("page-new.js"):
            return 200, "BTC price at expiry Market view", None
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_strategy_lab_client_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is True
    assert err is None


def test_verify_strategy_lab_client_bundle_accepts_generic_next_chunks() -> None:
    html = (
        '<script src="/_next/static/chunks/runtime.js"></script>'
        '<script src="/_next/static/chunks/strategy.js"></script>'
    )

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("runtime.js"):
            return 200, "shared runtime", None
        if url.endswith("strategy.js"):
            return 200, "BTC price at expiry Market view", None
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_strategy_lab_client_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is True
    assert err is None


def test_verify_msos_web_apex_rejects_streamlit() -> None:
    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("/"):
            return 200, "<html><body class='stApp'>Made with Streamlit</body></html>", None
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_msos_web_apex(base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is False
    assert "Streamlit" in (err or "")


def test_verify_msos_web_apex_accepts_nextjs() -> None:
    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("/"):
            return (
                200,
                '<html><script src="/_next/static/chunks/app/page.js"></script>'
                "<title>Market Structure OS</title></html>",
                None,
            )
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_msos_web_apex(base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is True
    assert err is None


def test_verify_mobile_context_rail_bundle_accepts_shipped_markers() -> None:
    html = (
        '<script src="/_next/static/chunks/app/strategy-lab/confirm/page.js"></script>'
        '<script src="/_next/static/chunks/shared.js"></script>'
    )

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("shared.js"):
            return (
                200,
                "context-rail-mobile context-rail-sheet-toggle Summary & next steps",
                None,
            )
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_mobile_context_rail_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is True
    assert err is None


def test_verify_mobile_context_rail_bundle_rejects_missing_markers() -> None:
    html = '<script src="/_next/static/chunks/app/strategy-lab/confirm/page.js"></script>'

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("page.js"):
            return 200, "context-rail desktop only", None
        return 404, "", "not found"

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = ship.verify_mobile_context_rail_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is False
    assert "mobile context rail" in (err or "")
