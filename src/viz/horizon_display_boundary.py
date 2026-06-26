"""Options Horizon display API handlers (surface + chart + region preview)."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from src.data.horizon_surface_archive import (
    build_surface_api_response,
    default_archive_root,
    load_latest_snapshot,
    load_nearest_snapshot,
)
from src.engine.horizon_region import compute_region_implied_mass
from src.viz.horizon_chart_payload import build_horizon_chart_payload

SURFACE_HTTP_PATH = "/ppe-display-api/horizon/surface.json"
CHART_HTTP_PATH = "/ppe-display-api/horizon/chart.json"
REGION_PREVIEW_HTTP_PATH = "/ppe-display-api/horizon/region-preview.json"


def _qs_int(environ: dict[str, Any], key: str) -> int | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    try:
        return int(raw[0])
    except (TypeError, ValueError):
        return None


def _qs_float(environ: dict[str, Any], key: str) -> float | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    try:
        return float(raw[0])
    except (TypeError, ValueError):
        return None


def _qs_str(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    text = str(raw[0]).strip()
    return text or None


def build_horizon_surface_response(environ: dict[str, Any]) -> dict[str, Any]:
    root = default_archive_root()
    qs = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False)
    asset = (_qs_str(environ, "asset") or "BTC").upper()
    as_of = _qs_str(environ, "as_of")
    latest = (qs.get("latest") or ["0"])[0].strip() in ("1", "true", "yes")

    snapshot = None
    if latest or not as_of:
        snapshot = load_latest_snapshot(root, asset_id=asset)
    elif as_of:
        snapshot = load_nearest_snapshot(root, as_of=as_of, asset_id=asset)
    return build_surface_api_response(snapshot, archive_root=root)


def build_horizon_chart_response(environ: dict[str, Any]) -> dict[str, Any]:
    asset = (_qs_str(environ, "asset") or "BTC").upper()
    expiry_ts = _qs_int(environ, "expiry_ts")
    as_of = _qs_str(environ, "as_of")
    days = _qs_int(environ, "chart_days")
    return build_horizon_chart_payload(
        asset_id=asset,
        expiry_ts=expiry_ts,
        as_of=as_of,
        chart_days=days or 90,
    )


def build_horizon_region_preview_response(environ: dict[str, Any]) -> dict[str, Any]:
    price_min = _qs_float(environ, "price_min_usd")
    price_max = _qs_float(environ, "price_max_usd")
    time_end = _qs_str(environ, "time_end_utc")
    expiry_ts = _qs_int(environ, "expiry_ts")
    forward = _qs_float(environ, "forward_usd")
    vol = _qs_float(environ, "atm_iv_annual")
    t_years = _qs_float(environ, "T_years")

    missing = [
        name
        for name, val in [
            ("price_min_usd", price_min),
            ("price_max_usd", price_max),
            ("time_end_utc", time_end),
            ("expiry_ts", expiry_ts),
            ("forward_usd", forward),
            ("atm_iv_annual", vol),
            ("T_years", t_years),
        ]
        if val is None
    ]
    if missing:
        return {
            "kind": "horizon_region_preview_error",
            "error": f"missing query params: {', '.join(missing)}",
        }

    computed = compute_region_implied_mass(
        price_min_usd=float(price_min),  # type: ignore[arg-type]
        price_max_usd=float(price_max),  # type: ignore[arg-type]
        time_end_utc=str(time_end),
        expiry_ts=int(expiry_ts),  # type: ignore[arg-type]
        forward_usd=float(forward),  # type: ignore[arg-type]
        atm_iv_annual=float(vol),  # type: ignore[arg-type]
        T_years=float(t_years),  # type: ignore[arg-type]
    )
    return {
        "kind": "horizon_region_preview",
        "computed": computed,
        "meta": {
            "read_only": True,
            "simulation_only": True,
            "http_path": REGION_PREVIEW_HTTP_PATH,
        },
    }


def handle_horizon_wsgi_path(
    path: str,
    environ: dict[str, Any],
) -> tuple[str, bytes] | None:
    """
    Handle /horizon/* paths. Returns (status, body) or None if not a horizon path.
    """
    if path == "/horizon/surface.json":
        try:
            payload = build_horizon_surface_response(environ)
        except Exception as exc:  # noqa: BLE001
            err = json.dumps({"kind": "horizon_surface_error", "error": str(exc)}, separators=(",", ":"))
            return "503 Service Unavailable", err.encode("utf-8")
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return "200 OK", body.encode("utf-8")

    if path == "/horizon/chart.json":
        try:
            payload = build_horizon_chart_response(environ)
        except Exception as exc:  # noqa: BLE001
            err = json.dumps({"kind": "horizon_chart_error", "error": str(exc)}, separators=(",", ":"))
            return "503 Service Unavailable", err.encode("utf-8")
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return "200 OK", body.encode("utf-8")

    if path == "/horizon/region-preview.json":
        payload = build_horizon_region_preview_response(environ)
        status = "200 OK" if payload.get("kind") == "horizon_region_preview" else "400 Bad Request"
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return status, body.encode("utf-8")

    return None
