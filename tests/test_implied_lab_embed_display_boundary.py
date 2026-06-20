"""Embed display boundary contracts (Strategy Lab distribution region)."""

from __future__ import annotations

import json

from src.viz.distribution_export import build_distribution_export_rows
from src.viz.embed_display_boundary import (
    DISPLAY_PAYLOAD_HTTP_PATH,
    DISPLAY_PAYLOAD_KIND,
    DISPLAY_PAYLOAD_MODE,
    DISPLAY_PAYLOAD_SCHEMA_VERSION,
    EMBED_ONLY_FALLBACK_MODE,
    build_distribution_display_payload,
    build_chart_series_from_export_row,
    create_display_payload_wsgi_app,
    serialize_distribution_display_payload,
)
from src.viz.implied_lab_legibility import DIST_SUMMARY_ANCHOR_ID


def _sample_export_rows() -> list[dict[str, str]]:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    return build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )


def test_display_payload_schema_and_summary() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    assert payload["schema_version"] == DISPLAY_PAYLOAD_SCHEMA_VERSION
    assert payload["kind"] == DISPLAY_PAYLOAD_KIND
    assert payload["anchor_id"] == DIST_SUMMARY_ANCHOR_ID
    assert payload["summary"]["row_count"] == 2
    assert payload["meta"]["http_path"] == DISPLAY_PAYLOAD_HTTP_PATH
    assert payload["meta"]["display_mode"] == DISPLAY_PAYLOAD_MODE
    assert payload["meta"]["fallback_mode"] == EMBED_ONLY_FALLBACK_MODE
    assert payload["meta"]["embed_json_query"] == "?embed_only=1&format=json"
    assert len(payload["series_by_expiry"]) == 1


def test_chart_series_from_lognormal_row() -> None:
    rows = _sample_export_rows()
    lognormal = next(r for r in rows if r["distribution"] == "lognormal_reference")
    series = build_chart_series_from_export_row(lognormal)
    assert series is not None
    assert len(series["prices_usd"]) == len(series["pdf_pct"]) == 80
    assert series["quartiles_usd"]["mean"] == 100_000.0


def test_bl_skipped_row_omits_series() -> None:
    rows = _sample_export_rows()
    bl = next(r for r in rows if r["distribution"] == "market_implied_bl")
    assert build_chart_series_from_export_row(bl) is None


def test_wsgi_app_serves_json() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    app = create_display_payload_wsgi_app(lambda: payload)

    status: list[str] = []
    headers: list[tuple[str, str]] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)
        headers.extend(hdrs)

    body = b"".join(app({"PATH_INFO": "/display.json"}, start_response))
    assert status == ["200 OK"]
    assert any(h == ("Content-Type", "application/json; charset=utf-8") for h in headers)
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == DISPLAY_PAYLOAD_KIND


def test_payload_serializes_deterministically() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    a = serialize_distribution_display_payload(payload)
    b = serialize_distribution_display_payload(payload)
    assert a == b
    assert json.loads(a)["spot_usd"] == 99_000.0
