"""
Read-only display boundary for Strategy Lab embed (distribution chart region).

Pre-computed series and summary table come from existing Python pipelines only.
Platform slice 004 may proxy ``DISPLAY_PAYLOAD_HTTP_PATH`` to ``create_display_payload_wsgi_app``.
"""

from __future__ import annotations

import json
from typing import Any, Callable
from urllib.parse import parse_qs

from src.data.assets_registry import (
    asset_venue,
    catalog_group_order,
    default_asset_id,
    get_asset,
    is_asset_enabled,
    list_catalog_entries,
    registry_version,
)
from src.engine.implied_distribution import build_distribution_chart_data, lognormal_pdf
from src.viz.curve_display_labels import build_curve_display_labels
from src.viz.lab_asset_selection import (
    LAB_ASSET_QUERY_PARAM,
    display_asset_meta,
    lab_asset_id_from_environ,
    normalize_lab_asset_id,
)
from src.viz.distribution_summary_panel import summary_panel_contract
from src.viz.implied_lab_legibility import DIST_SUMMARY_ANCHOR_ID, DIST_SUMMARY_TITLE

DISPLAY_PAYLOAD_SCHEMA_VERSION = 1
DISPLAY_PAYLOAD_KIND = "distribution_display_boundary"
DISPLAY_PAYLOAD_HTTP_PATH = "/ppe-display-api/display.json"
CATALOG_PAYLOAD_HTTP_PATH = "/ppe-display-api/catalog.json"
BELIEF_OVERLAY_KIND = "belief_overlay"
BELIEF_OVERLAY_HTTP_PATH = "/ppe-display-api/belief-overlay.json"
STRATEGY_SUGGESTION_HTTP_PATH = "/ppe-display-api/strategy-suggestion.json"
EMBED_ONLY_QUERY_PARAM = "embed_only"
EMBED_JSON_QUERY_PARAM = "format"
EMBED_JSON_QUERY_VALUE = "json"
DISPLAY_PAYLOAD_MODE = "native_json"
CATALOG_PAYLOAD_KIND = "asset_catalog"
CATALOG_PAYLOAD_SCHEMA_VERSION = 1
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
        "curve_labels": build_curve_display_labels(),
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


def _chart_bounds_usd(forward: float, asset_id: str) -> tuple[float, float]:
    aid = str(asset_id or default_asset_id()).strip().upper()
    if asset_venue(aid) == "equity":
        return max(1.0, forward * 0.35), forward * 2.5
    return max(1000.0, forward * 0.4), forward * 2.2


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
    asset_id = str(row.get("asset") or default_asset_id()).strip().upper()
    price_min, price_max = _chart_bounds_usd(forward, asset_id)
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
        "curve_labels": build_curve_display_labels(),
    }


def build_distribution_display_payload(
    *,
    as_of_utc: str,
    spot_usd: float,
    export_rows: list[dict[str, str]],
    asset_id: str | None = None,
) -> dict[str, Any]:
    """JSON-serializable read-only payload for MSOS chart shell (no new math)."""
    aid = normalize_lab_asset_id(asset_id)
    if asset_id is None and export_rows and export_rows[0].get("asset"):
        aid = normalize_lab_asset_id(str(export_rows[0]["asset"]))
    asset_block = display_asset_meta(aid)
    summary = summary_panel_contract(export_rows)
    series = []
    for row in export_rows:
        if (s := build_chart_series_from_export_row(row)) is not None:
            s["belief_presets"] = build_belief_preset_overlays(s)
            series.append(s)
    belief_presets = series[0].get("belief_presets", {}) if series else {}
    curve_labels = build_curve_display_labels()
    return {
        "schema_version": DISPLAY_PAYLOAD_SCHEMA_VERSION,
        "kind": DISPLAY_PAYLOAD_KIND,
        "as_of_utc": as_of_utc,
        "spot_usd": spot_usd,
        "asset": asset_block,
        "anchor_id": DIST_SUMMARY_ANCHOR_ID,
        "title": DIST_SUMMARY_TITLE,
        "summary": summary,
        "series_by_expiry": series,
        "belief_presets": belief_presets,
        "curve_labels": curve_labels,
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


def build_asset_catalog_response() -> dict[str, Any]:
    """Grouped enabled assets for MSOS / Streamlit pickers (metadata only — no prices)."""
    entries = list_catalog_entries(enabled_only=True)
    by_group: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        gid = str(entry.get("catalog_group") or "other")
        by_group.setdefault(gid, []).append(entry)

    groups: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in catalog_group_order():
        gid = str(row.get("id") or "").strip()
        if not gid or gid not in by_group:
            continue
        groups.append(
            {
                "id": gid,
                "label": str(row.get("label") or gid),
                "assets": by_group[gid],
            }
        )
        seen.add(gid)
    for gid in sorted(by_group):
        if gid in seen:
            continue
        groups.append(
            {
                "id": gid,
                "label": gid.replace("_", " ").title(),
                "assets": by_group[gid],
            }
        )

    return {
        "schema_version": CATALOG_PAYLOAD_SCHEMA_VERSION,
        "kind": CATALOG_PAYLOAD_KIND,
        "default_asset_id": default_asset_id(),
        "groups": groups,
        "meta": {
            "read_only": True,
            "http_path": CATALOG_PAYLOAD_HTTP_PATH,
            "registry_version": registry_version(),
        },
    }


def serialize_asset_catalog_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def validate_asset_catalog_payload(payload: dict[str, Any]) -> tuple[bool, str | None]:
    if payload.get("kind") != CATALOG_PAYLOAD_KIND:
        return False, f"expected kind {CATALOG_PAYLOAD_KIND!r}"
    if not payload.get("default_asset_id"):
        return False, "missing default_asset_id"
    groups = payload.get("groups")
    if not isinstance(groups, list) or not groups:
        return False, "groups must be a non-empty list"
    asset_ids: list[str] = []
    for group in groups:
        if not isinstance(group, dict):
            return False, "group must be object"
        assets = group.get("assets")
        if not isinstance(assets, list) or not assets:
            return False, f"group {group.get('id')!r} has no assets"
        for asset in assets:
            if not isinstance(asset, dict) or not asset.get("id"):
                return False, "asset entry missing id"
            asset_ids.append(str(asset["id"]))
    if payload["default_asset_id"] not in asset_ids:
        return False, "default_asset_id not present in grouped assets"
    return True, None


def _sample_export_row(asset_id: str) -> list[dict[str, str]]:
    """Minimal export row for mocked display-boundary witness (no vendor I/O)."""
    return [
        {
            "asset": asset_id,
            "distribution": "market_implied_bl",
            "expiry_date": "2030-01-01",
            "forward_usd": "100000",
            "atm_iv": "0.5",
            "spot_usd": "99000",
            "trust_state": "ok",
        },
        {
            "asset": asset_id,
            "distribution": "lognormal_reference",
            "expiry_date": "2030-01-01",
            "forward_usd": "100000",
            "atm_iv": "0.5",
            "spot_usd": "99000",
            "trust_state": "ok",
        },
    ]


def witness_display_boundary_for_asset(asset_id: str, *, live: bool = False) -> tuple[bool, str]:
    """Registry + display payload witness for one asset (mocked or live)."""
    aid = str(asset_id or "").strip().upper()
    if not is_asset_enabled(aid):
        return True, "skipped (disabled)"
    try:
        get_asset(aid)
    except KeyError:
        return False, "unknown asset_id"

    catalog_ids = {e["id"] for e in list_catalog_entries(enabled_only=True)}
    if aid not in catalog_ids:
        return False, "missing from enabled catalog entries"

    if live:
        try:
            payload = build_live_distribution_display_payload(asset_id=aid)
        except Exception as exc:  # noqa: BLE001
            return False, f"live display boundary failed: {exc}"
    else:
        payload = build_distribution_display_payload(
            as_of_utc="2026-01-01T00:00:00Z",
            spot_usd=100_000.0 if asset_venue(aid) == "deribit" else 140.0,
            export_rows=_sample_export_row(aid),
            asset_id=aid,
        )

    if payload.get("kind") != DISPLAY_PAYLOAD_KIND:
        return False, f"unexpected payload kind {payload.get('kind')!r}"
    if str((payload.get("asset") or {}).get("id")) != aid:
        return False, "payload asset id mismatch"
    return True, "display boundary ok"


def build_live_distribution_display_payload(
    *,
    asset_id: str | None = None,
    environ: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Live options-backed payload for platform WSGI / MSOS display API proxy."""
    from src.viz.embed_only_lab import _load_export_rows

    aid = normalize_lab_asset_id(asset_id)
    if environ is not None and asset_id is None:
        aid = lab_asset_id_from_environ(environ)
    as_of_utc, spot_usd, export_rows = _load_export_rows(asset_id=aid)
    return build_distribution_display_payload(
        as_of_utc=as_of_utc,
        spot_usd=spot_usd,
        export_rows=export_rows,
        asset_id=aid,
    )


def create_display_payload_wsgi_app(
    payload_provider: Callable[..., dict[str, Any]],
) -> Callable[..., Any]:
    """Minimal WSGI app for platform proxy (display, belief overlay, strategy suggestion)."""

    def app(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        path = (environ.get("PATH_INFO") or "").rstrip("/") or "/"
        if path in ("/", "/display.json"):
            try:
                payload = payload_provider(environ)
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

        if path == "/catalog.json":
            catalog = build_asset_catalog_response()
            body = serialize_asset_catalog_payload(catalog).encode("utf-8")
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
                payload = payload_provider(environ)
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

        if path == "/strategy-suggestion.json":
            from src.viz.strategy_suggestion_boundary import (
                STRATEGY_SUGGESTION_KIND,
                build_strategy_suggestion_response,
            )

            qs = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False)
            expiry = (qs.get("expiry") or [""])[0].strip()
            forward_mult = _query_float(environ, "forward_mult", 1.0)
            vol_mult = _query_float(environ, "vol_mult", 1.0)
            if not expiry:
                err = json.dumps(
                    {"kind": "strategy_suggestion_error", "error": "expiry query param required"},
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
                suggestion = build_strategy_suggestion_response(
                    expiry_date=expiry,
                    forward_mult=forward_mult,
                    vol_mult=vol_mult,
                )
            except Exception as exc:  # noqa: BLE001
                err = json.dumps(
                    {"kind": "strategy_suggestion_error", "error": str(exc)},
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
            body = json.dumps(suggestion, separators=(",", ":"), sort_keys=True).encode("utf-8")
            status = (
                "200 OK"
                if suggestion.get("kind") == STRATEGY_SUGGESTION_KIND
                else "404 Not Found"
            )
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
