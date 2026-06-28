"""Forward consistency display API (Strategy Lab / MSOS read-only boundary)."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from src.data.forward_consistency_quotes import build_forward_consistency_live
from src.viz.lab_asset_selection import LAB_ASSET_QUERY_PARAM, normalize_lab_asset_id

FORWARD_CONSISTENCY_KIND = "forward_consistency_boundary"
FORWARD_CONSISTENCY_HTTP_PATH = "/ppe-display-api/forward-consistency.json"
FORWARD_CONSISTENCY_HTTP_PATH_ALT = "/forward-consistency.json"


def _qs_str(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    text = str(raw[0]).strip()
    return text or None


def build_forward_consistency_response(environ: dict[str, Any]) -> dict[str, Any]:
    asset = normalize_lab_asset_id(_qs_str(environ, "asset") or _qs_str(environ, LAB_ASSET_QUERY_PARAM))
    expiry = _qs_str(environ, "expiry") or _qs_str(environ, "expiry_date") or ""
    if not expiry:
        return {
            "kind": "forward_consistency_error",
            "error": "expiry query param required (YYYY-MM-DD or display payload expiry string)",
        }
    return build_forward_consistency_live(asset_id=asset, expiry_date=expiry)


def handle_forward_consistency_wsgi_path(
    path: str,
    environ: dict[str, Any],
) -> tuple[str, bytes] | None:
    normalized = path.rstrip("/") or "/"
    if normalized not in (
        FORWARD_CONSISTENCY_HTTP_PATH,
        FORWARD_CONSISTENCY_HTTP_PATH_ALT,
    ):
        return None
    try:
        payload = build_forward_consistency_response(environ)
    except Exception as exc:  # noqa: BLE001 — surface fetch failures as JSON
        payload = {"kind": "forward_consistency_error", "error": str(exc)}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    kind = payload.get("kind")
    if kind == "forward_consistency_error":
        status = "400 Bad Request" if payload.get("error", "").startswith("expiry") else "503 Service Unavailable"
    else:
        status = "200 OK"
    return status, body
