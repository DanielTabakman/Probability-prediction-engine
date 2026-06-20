"""
Read-only display boundary for Strategy Lab embed (distribution chart region).

Pre-computed series and summary table come from existing Python pipelines only.
Platform slice 004 may proxy ``DISPLAY_PAYLOAD_HTTP_PATH`` to ``create_display_payload_wsgi_app``.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from src.engine.implied_distribution import build_distribution_chart_data
from src.viz.distribution_summary_panel import summary_panel_contract
from src.viz.implied_lab_legibility import DIST_SUMMARY_ANCHOR_ID, DIST_SUMMARY_TITLE

DISPLAY_PAYLOAD_SCHEMA_VERSION = 1
DISPLAY_PAYLOAD_KIND = "distribution_display_boundary"
DISPLAY_PAYLOAD_HTTP_PATH = "/ppe-display-api/display.json"
EMBED_ONLY_QUERY_PARAM = "embed_only"
EMBED_JSON_QUERY_PARAM = "format"
EMBED_JSON_QUERY_VALUE = "json"
DISPLAY_PAYLOAD_MODE = "native_json"
EMBED_ONLY_FALLBACK_MODE = "streamlit_embed_only"


def _parse_float(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def build_chart_series_from_export_row(row: dict[str, str]) -> dict[str, Any] | None:
    """Lognormal reference curve for one expiry export row (skipped BL rows omitted)."""
    distribution = str(row.get("distribution") or "")
    if distribution != "lognormal_reference":
        return None
    forward = _parse_float(row.get("forward_usd"))
    vol = _parse_float(row.get("atm_iv_annual"))
    t_years = _parse_float(row.get("T_years"))
    if forward is None or vol is None or t_years is None or forward <= 0 or vol <= 0:
        return None
    price_min = max(1000.0, forward * 0.4)
    price_max = forward * 2.2
    chart = build_distribution_chart_data(
        forward=forward,
        vol_annual=vol,
        T_years=max(t_years, 0.02),
        price_min=price_min,
        price_max=price_max,
        num_points=80,
    )
    return {
        "expiry_date": str(row.get("expiry_date") or ""),
        "distribution": distribution,
        "forward_usd": forward,
        "atm_iv_annual": vol,
        "T_years": t_years,
        "price_min_usd": price_min,
        "price_max_usd": price_max,
        "prices_usd": chart["prices"],
        "pdf_pct": chart["pdf_pct"],
        "cumulative_at": [
            {"price_usd": price, "cdf_pct": cdf_pct}
            for price, cdf_pct in chart.get("cumulative_at") or []
        ],
        "quartiles_usd": {
            "mean": _parse_float(row.get("mean_usd")),
            "q25": _parse_float(row.get("q25_usd")),
            "q50": _parse_float(row.get("q50_usd")),
            "q75": _parse_float(row.get("q75_usd")),
        },
    }


def build_distribution_display_payload(
    *,
    as_of_utc: str,
    spot_usd: float,
    export_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """JSON-serializable read-only payload for MSOS chart shell (no new math)."""
    summary = summary_panel_contract(export_rows)
    series = [
        s
        for row in export_rows
        if (s := build_chart_series_from_export_row(row)) is not None
    ]
    return {
        "schema_version": DISPLAY_PAYLOAD_SCHEMA_VERSION,
        "kind": DISPLAY_PAYLOAD_KIND,
        "as_of_utc": as_of_utc,
        "spot_usd": spot_usd,
        "anchor_id": DIST_SUMMARY_ANCHOR_ID,
        "title": DIST_SUMMARY_TITLE,
        "summary": summary,
        "series_by_expiry": series,
        "meta": {
            "read_only": True,
            "display_mode": DISPLAY_PAYLOAD_MODE,
            "fallback_mode": EMBED_ONLY_FALLBACK_MODE,
            "embed_query": f"?{EMBED_ONLY_QUERY_PARAM}=1",
            "json_query": f"?{EMBED_JSON_QUERY_PARAM}={EMBED_JSON_QUERY_VALUE}",
            "embed_json_query": (
                f"?{EMBED_ONLY_QUERY_PARAM}=1&"
                f"{EMBED_JSON_QUERY_PARAM}={EMBED_JSON_QUERY_VALUE}"
            ),
            "http_path": DISPLAY_PAYLOAD_HTTP_PATH,
        },
    }


def serialize_distribution_display_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def create_display_payload_wsgi_app(
    payload_provider: Callable[[], dict[str, Any]],
) -> Callable[..., Any]:
    """Minimal WSGI app for platform proxy (GET display.json only)."""

    def app(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        path = (environ.get("PATH_INFO") or "").rstrip("/") or "/"
        if path not in ("/", "/display.json"):
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"not found"]
        body = serialize_distribution_display_payload(payload_provider()).encode("utf-8")
        start_response(
            "200 OK",
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-store"),
            ],
        )
        return [body]

    return app
