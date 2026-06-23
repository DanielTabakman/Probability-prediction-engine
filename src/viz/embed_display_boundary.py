"""
Read-only display boundary for Strategy Lab embed (distribution chart region).

Pre-computed series and summary table come from existing Python pipelines only.
Platform slice 004 may proxy ``DISPLAY_PAYLOAD_HTTP_PATH`` to ``create_display_payload_wsgi_app``.
"""

from __future__ import annotations

import json
from typing import Any, Callable
from urllib.parse import parse_qs

from src.engine.implied_distribution import build_distribution_chart_data, lognormal_pdf
from src.viz.distribution_summary_panel import summary_panel_contract
from src.viz.implied_lab_legibility import DIST_SUMMARY_ANCHOR_ID, DIST_SUMMARY_TITLE

DISPLAY_PAYLOAD_SCHEMA_VERSION = 1
DISPLAY_PAYLOAD_KIND = "distribution_display_boundary"
DISPLAY_PAYLOAD_HTTP_PATH = "/ppe-display-api/display.json"
BELIEF_OVERLAY_KIND = "belief_overlay"
BELIEF_OVERLAY_HTTP_PATH = "/ppe-display-api/belief-overlay.json"
EMBED_ONLY_QUERY_PARAM = "embed_only"
EMBED_JSON_QUERY_PARAM = "format"
EMBED_JSON_QUERY_VALUE = "json"
DISPLAY_PAYLOAD_MODE = "native_json"
EMBED_ONLY_FALLBACK_MODE = "streamlit_embed_only"

# MSOS Strategy Lab belief presets — illustrative lognormal shifts vs market reference (display only).
BELIEF_TUNING_BOUNDS: dict[str, dict[str, float]] = {
    "forward_mult": {"min": 0.88, "max": 1.12, "market": 1.0},
    "vol_mult": {"min": 0.55, "max": 1.45, "market": 1.0},
}

BELIEF_PRESET_DISPLAY_SHIFTS: dict[str, dict[str, float]] = {
    "higher": {"forward_mult": 1.06, "vol_mult": 1.0},
    "lower": {"forward_mult": 0.94, "vol_mult": 1.0},
    "more_volatility": {"forward_mult": 1.0, "vol_mult": 1.35},
    "less_volatility": {"forward_mult": 1.0, "vol_mult": 0.65},
}


def _peak_scaled_pdf_pct(pdf: list[float]) -> list[float]:
    """Match ``build_distribution_chart_data`` y-axis scaling (peak ≈ 25%)."""
    max_pdf = max(pdf) if pdf else 0.0
    if max_pdf <= 0:
        return [0.0] * len(pdf)
    return [float(d) / max_pdf * 25.0 for d in pdf]


def clamp_belief_mult(name: str, value: float) -> float:
    bounds = BELIEF_TUNING_BOUNDS[name]
    return max(float(bounds["min"]), min(float(bounds["max"]), float(value)))


def build_belief_overlay_from_mults(
    series: dict[str, Any],
    *,
    forward_mult: float,
    vol_mult: float,
) -> dict[str, Any] | None:
    """Belief lognormal curve on the market price grid (display-only shift vs reference)."""
    forward = float(series.get("forward_usd") or 0.0)
    vol = float(series.get("atm_iv_annual") or 0.0)
    t_years = float(series.get("T_years") or 0.0)
    prices = series.get("prices_usd") or []
    if forward <= 0 or vol <= 0 or t_years <= 0 or not prices:
        return None

    fwd_m = clamp_belief_mult("forward_mult", forward_mult)
    vol_m = clamp_belief_mult("vol_mult", vol_mult)
    belief_forward = forward * fwd_m
    belief_vol = vol * vol_m
    pdf = lognormal_pdf(belief_forward, belief_vol, t_years, prices)
    return {
        "pdf_pct": _peak_scaled_pdf_pct(pdf),
        "forward_usd": belief_forward,
        "atm_iv_annual": belief_vol,
        "forward_mult": fwd_m,
        "vol_mult": vol_m,
    }


def build_belief_preset_overlays(series: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Pre-computed belief curves on the market price grid for MSOS chart overlay."""
    overlays: dict[str, dict[str, Any]] = {}
    for preset_id, mults in BELIEF_PRESET_DISPLAY_SHIFTS.items():
        overlay = build_belief_overlay_from_mults(
            series,
            forward_mult=float(mults["forward_mult"]),
            vol_mult=float(mults["vol_mult"]),
        )
        if overlay is not None:
            overlays[preset_id] = overlay
    return overlays


def _find_series_by_expiry(payload: dict[str, Any], expiry_date: str) -> dict[str, Any] | None:
    target = str(expiry_date or "").strip()
    if not target:
        return None
    for row in payload.get("series_by_expiry") or []:
        if str(row.get("expiry_date") or "") == target:
            return row
    return None


def build_belief_overlay_response(
    payload: dict[str, Any],
    *,
    expiry_date: str,
    forward_mult: float,
    vol_mult: float,
) -> dict[str, Any]:
    series = _find_series_by_expiry(payload, expiry_date)
    if series is None:
        return {
            "kind": "belief_overlay_error",
            "error": f"expiry not found: {expiry_date}",
        }
    overlay = build_belief_overlay_from_mults(
        series,
        forward_mult=forward_mult,
        vol_mult=vol_mult,
    )
    if overlay is None:
        return {
            "kind": "belief_overlay_error",
            "error": "belief overlay unavailable for expiry series",
        }
    return {
        "kind": BELIEF_OVERLAY_KIND,
        "expiry_date": expiry_date,
        "pdf_pct": overlay["pdf_pct"],
        "forward_usd": overlay["forward_usd"],
        "atm_iv_annual": overlay["atm_iv_annual"],
        "forward_mult": overlay["forward_mult"],
        "vol_mult": overlay["vol_mult"],
        "tuning_bounds": BELIEF_TUNING_BOUNDS,
    }


def _query_float(environ: dict[str, Any], key: str, default: float) -> float:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return default
    try:
        return float(raw[0])
    except (TypeError, ValueError):
        return default


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
        "mean_usd": _parse_float(row.get("mean_usd")),
        "quartiles_usd": {
            "q1_usd": _parse_float(row.get("q25_usd")),
            "median_usd": _parse_float(row.get("q50_usd")),
            "q3_usd": _parse_float(row.get("q75_usd")),
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
    series = []
    for row in export_rows:
        if (s := build_chart_series_from_export_row(row)) is not None:
            s["belief_presets"] = build_belief_preset_overlays(s)
            series.append(s)
    belief_presets = series[0].get("belief_presets", {}) if series else {}
    return {
        "schema_version": DISPLAY_PAYLOAD_SCHEMA_VERSION,
        "kind": DISPLAY_PAYLOAD_KIND,
        "as_of_utc": as_of_utc,
        "spot_usd": spot_usd,
        "anchor_id": DIST_SUMMARY_ANCHOR_ID,
        "title": DIST_SUMMARY_TITLE,
        "summary": summary,
        "series_by_expiry": series,
        "belief_presets": belief_presets,
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


def build_live_distribution_display_payload() -> dict[str, Any]:
    """Live Deribit-backed payload for platform WSGI / MSOS display API proxy."""
    from src.viz.embed_only_lab import _load_export_rows

    as_of_utc, spot_usd, export_rows = _load_export_rows()
    return build_distribution_display_payload(
        as_of_utc=as_of_utc,
        spot_usd=spot_usd,
        export_rows=export_rows,
    )


def create_display_payload_wsgi_app(
    payload_provider: Callable[[], dict[str, Any]],
) -> Callable[..., Any]:
    """Minimal WSGI app for platform proxy (display.json + belief-overlay.json)."""

    def app(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        path = (environ.get("PATH_INFO") or "").rstrip("/") or "/"
        if path in ("/", "/display.json"):
            try:
                payload = payload_provider()
            except Exception as exc:  # noqa: BLE001 — surface upstream fetch failures as JSON
                err = json.dumps(
                    {"kind": "display_error", "error": str(exc)},
                    separators=(",", ":"),
                ).encode("utf-8")
                start_response(
                    "503 Service Unavailable",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err))),
                        ("Cache-Control", "no-store"),
                    ],
                )
                return [err]
            body = serialize_distribution_display_payload(payload).encode("utf-8")
            start_response(
                "200 OK",
                [
                    ("Content-Type", "application/json; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                    ("Cache-Control", "no-store"),
                ],
            )
            return [body]

        if path == "/belief-overlay.json":
            qs = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False)
            expiry = (qs.get("expiry") or [""])[0].strip()
            forward_mult = _query_float(environ, "forward_mult", 1.0)
            vol_mult = _query_float(environ, "vol_mult", 1.0)
            if not expiry:
                err = json.dumps(
                    {"kind": "belief_overlay_error", "error": "expiry query param required"},
                    separators=(",", ":"),
                ).encode("utf-8")
                start_response(
                    "400 Bad Request",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err))),
                        ("Cache-Control", "no-store"),
                    ],
                )
                return [err]
            try:
                payload = payload_provider()
            except Exception as exc:  # noqa: BLE001
                err = json.dumps(
                    {"kind": "belief_overlay_error", "error": str(exc)},
                    separators=(",", ":"),
                ).encode("utf-8")
                start_response(
                    "503 Service Unavailable",
                    [
                        ("Content-Type", "application/json; charset=utf-8"),
                        ("Content-Length", str(len(err))),
                        ("Cache-Control", "no-store"),
                    ],
                )
                return [err]
            overlay = build_belief_overlay_response(
                payload,
                expiry_date=expiry,
                forward_mult=forward_mult,
                vol_mult=vol_mult,
            )
            body = json.dumps(overlay, separators=(",", ":"), sort_keys=True).encode("utf-8")
            status = "200 OK" if overlay.get("kind") == BELIEF_OVERLAY_KIND else "404 Not Found"
            start_response(
                status,
                [
                    ("Content-Type", "application/json; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                    ("Cache-Control", "no-store"),
                ],
            )
            return [body]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"not found"]

    return app
