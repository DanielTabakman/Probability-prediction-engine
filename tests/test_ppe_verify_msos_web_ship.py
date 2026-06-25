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
