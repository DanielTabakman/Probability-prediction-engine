"""Tests for MSOS production demo witness helpers."""

from __future__ import annotations

import json

from scripts.msos_production_demo_witness import (
    FIXTURE_PREVIEW_SPOT,
    _collect_fixture_warnings,
    _has_research_cta,
    validate_belief_overlay_api_response,
    validate_display_api_response,
    validate_strategy_lab_client_bundle,
    validate_strategy_lab_html,
)


def test_has_research_cta_positive() -> None:
    html = '<a href="mailto:a@b.com">Request research beta access</a>'
    assert _has_research_cta(html) is True


def test_has_research_cta_negative() -> None:
    assert _has_research_cta("<p>Explore the platform</p>") is False


def test_validate_display_api_response_ok() -> None:
    body = json.dumps(
        {
            "kind": "distribution_display_boundary",
            "spot_usd": 64000.0,
            "asset": {"id": "ETH", "label": "ETH options"},
            "series_by_expiry": [{"expiry_date": "2030-01-01", "prices_usd": [1, 2], "pdf_pct": [1, 2]}],
        }
    )
    ok, err, data = validate_display_api_response(200, body, expected_asset_id="ETH")
    assert ok is True
    assert err is None
    assert data is not None
    assert data["spot_usd"] == 64000.0


def test_validate_display_api_response_asset_mismatch() -> None:
    body = json.dumps(
        {
            "kind": "distribution_display_boundary",
            "spot_usd": 140.0,
            "asset": {"id": "BTC", "label": "BTC options"},
            "series_by_expiry": [{"expiry_date": "2030-01-01", "prices_usd": [1, 2], "pdf_pct": [1, 2]}],
        }
    )
    ok, err, _ = validate_display_api_response(200, body, expected_asset_id="NVDA")
    assert ok is False
    assert "NVDA" in (err or "")


def test_validate_display_api_response_ok_without_asset_probe() -> None:
    body = json.dumps(
        {
            "kind": "distribution_display_boundary",
            "spot_usd": 64000.0,
            "series_by_expiry": [{"expiry_date": "2030-01-01", "prices_usd": [1, 2], "pdf_pct": [1, 2]}],
        }
    )
    ok, err, data = validate_display_api_response(200, body)
    assert ok is True
    assert err is None
    assert data is not None
    assert data["spot_usd"] == 64000.0


def test_validate_display_api_response_http_error() -> None:
    ok, err, _ = validate_display_api_response(500, "Internal Server Error")
    assert ok is False
    assert "500" in (err or "")


def test_validate_display_api_response_display_error_kind() -> None:
    body = json.dumps({"kind": "display_error", "error": "Deribit BTC index unavailable"})
    ok, err, _ = validate_display_api_response(503, body)
    assert ok is False
    assert "Deribit" in (err or "")


def test_validate_belief_overlay_api_response_ok() -> None:
    body = json.dumps({"kind": "belief_overlay", "pdf_pct": [0.0, 12.5, 0.0]})
    ok, err = validate_belief_overlay_api_response(200, body)
    assert ok is True
    assert err is None


def test_validate_belief_overlay_api_response_not_found() -> None:
    ok, err = validate_belief_overlay_api_response(404, "not found")
    assert ok is False
    assert "404" in (err or "")


def test_validate_strategy_lab_html_native_chart() -> None:
    html = '<div class="ppe-chart-region"><span>Live via PPE</span> Native chart'
    ok, err = validate_strategy_lab_html(html)
    assert ok is True
    assert err is None


def test_validate_strategy_lab_html_sample_mode() -> None:
    html = '<div class="lab-data-banner demo">Sample mode — not live market data</div>'
    ok, err = validate_strategy_lab_html(html)
    assert ok is False
    assert "sample" in (err or "").lower()


def test_validate_strategy_lab_html_placeholder_chart() -> None:
    html = '<div class="ppe-embed-degraded"><h3>Placeholder chart</h3></div>'
    ok, err = validate_strategy_lab_html(html)
    assert ok is False
    assert "sample" in (err or "").lower() or "placeholder" in (err or "").lower()


def test_validate_strategy_lab_client_bundle_rejects_stale_legend() -> None:
    html = '<script src="/_next/static/chunks/app/strategy-lab/page-stale.js"></script>'

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("page-stale.js"):
            return 200, "Options market Reference curve", None
        return 404, "", "not found"

    import scripts.verify_msos_web_ship as ship

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = validate_strategy_lab_client_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is False
    assert "stale" in (err or "")


def test_validate_strategy_lab_client_bundle_accepts_labeled_axes() -> None:
    html = '<script src="/_next/static/chunks/app/strategy-lab/page-new.js"></script>'

    def fake_fetch(url: str, *, timeout: float = 30.0):
        if url.endswith("page-new.js"):
            return 200, "BTC price at expiry Market view", None
        return 404, "", "not found"

    import scripts.verify_msos_web_ship as ship

    original = ship.fetch_url
    ship.fetch_url = fake_fetch
    try:
        ok, err = validate_strategy_lab_client_bundle(html, base_url="https://example.com")
    finally:
        ship.fetch_url = original
    assert ok is True
    assert err is None


def test_collect_fixture_warnings() -> None:
    html = "Spot Sample only Illustrative product storyboard Preview data healthy"
    warnings = _collect_fixture_warnings(html)
    ids = {w["id"] for w in warnings}
    assert "fixture_preview_metrics" in ids
    assert "fixture_footer" in ids
    assert "fixture_preview_pill" in ids


def test_playwright_live_pill_spot_assets_cover_nvda_and_non_btc_crypto() -> None:
    from scripts.msos_production_playwright_witness import LIVE_PILL_SPOT_ASSETS
    from scripts.msos_production_demo_witness import MULTI_ASSET_DISPLAY_PROBE_IDS

    assert "NVDA" in LIVE_PILL_SPOT_ASSETS
    assert "ETH" in LIVE_PILL_SPOT_ASSETS
    assert "BTC" not in LIVE_PILL_SPOT_ASSETS
    assert set(LIVE_PILL_SPOT_ASSETS).issubset(set(MULTI_ASSET_DISPLAY_PROBE_IDS))


def test_playwright_validate_strategy_lab_live_pill_html_nvda_ok() -> None:
    from scripts.msos_production_playwright_witness import (
        LIVE_PILL_EXPECTED,
        validate_strategy_lab_live_pill_html,
    )

    html = (
        '<header><div class="crumb">Strategy Lab · NVDA options</div>'
        '<span class="pill live" role="status"><span class="dot"></span>'
        "Live · equity options chain</span></header>"
        '<div data-asset="NVDA"></div>'
    )
    ok, err = validate_strategy_lab_live_pill_html(
        html,
        asset_id="NVDA",
        expected_pill=LIVE_PILL_EXPECTED["NVDA"],
    )
    assert ok is True
    assert err is None


def test_playwright_validate_strategy_lab_live_pill_html_eth_ok() -> None:
    from scripts.msos_production_playwright_witness import (
        LIVE_PILL_EXPECTED,
        validate_strategy_lab_live_pill_html,
    )

    html = (
        '<span class="pill live" role="status">Live · Deribit options</span>'
        "Strategy Lab · ETH options ETH"
    )
    ok, err = validate_strategy_lab_live_pill_html(
        html,
        asset_id="ETH",
        expected_pill=LIVE_PILL_EXPECTED["ETH"],
    )
    assert ok is True
    assert err is None


def test_playwright_validate_strategy_lab_live_pill_html_sample_mode() -> None:
    from scripts.msos_production_playwright_witness import (
        LIVE_PILL_EXPECTED,
        validate_strategy_lab_live_pill_html,
    )

    html = '<div class="lab-data-banner demo">Sample mode — not live market data</div>'
    ok, err = validate_strategy_lab_live_pill_html(
        html,
        asset_id="NVDA",
        expected_pill=LIVE_PILL_EXPECTED["NVDA"],
    )
    assert ok is False
    assert err is not None
    assert "sample" in err.lower()

