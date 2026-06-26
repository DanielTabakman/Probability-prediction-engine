"""Tests for Options Horizon display API boundary."""

from __future__ import annotations

import json

from src.viz.embed_display_boundary import create_display_payload_wsgi_app
from src.viz.horizon_display_boundary import build_horizon_region_preview_response


def test_region_preview_missing_params() -> None:
    out = build_horizon_region_preview_response({"QUERY_STRING": ""})
    assert out["kind"] == "horizon_region_preview_error"


def test_horizon_surface_wsgi_route() -> None:
    app = create_display_payload_wsgi_app(lambda _environ: {})
    status: list[str] = []
    headers: dict[str, str] = {}

    def start_response(st: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(st)
        headers.update(dict(hdrs))

    body = b"".join(app({"PATH_INFO": "/horizon/surface.json", "QUERY_STRING": "latest=1"}, start_response))
    assert status[0] == "200 OK"
    payload = json.loads(body.decode("utf-8"))
    assert payload["kind"] == "horizon_surface"


def test_horizon_region_preview_wsgi_route() -> None:
    app = create_display_payload_wsgi_app(lambda _environ: {})
    status: list[str] = []

    def start_response(st: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(st)

    qs = (
        "price_min_usd=90000&price_max_usd=110000"
        "&time_end_utc=2026-12-31T00:00:00Z"
        "&expiry_ts=1893456000000"
        "&forward_usd=100000&atm_iv_annual=0.5&T_years=0.25"
    )
    body = b"".join(
        app({"PATH_INFO": "/horizon/region-preview.json", "QUERY_STRING": qs}, start_response)
    )
    assert status[0] == "200 OK"
    payload = json.loads(body.decode("utf-8"))
    assert payload["kind"] == "horizon_region_preview"
