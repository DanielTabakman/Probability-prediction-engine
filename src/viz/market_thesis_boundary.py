"""Market thesis validate / apply boundary for MSOS (Python owns state)."""

from __future__ import annotations

import json
from typing import Any

from src.engine.market_thesis import (
    MarketThesisError,
    apply_event,
    new_draft,
    validate_market_thesis,
)

MARKET_THESIS_VALIDATE_HTTP_PATH = "/ppe-display-api/market-thesis/validate.json"
MARKET_THESIS_APPLY_HTTP_PATH = "/ppe-display-api/market-thesis/apply.json"
_VALIDATE_PATH = "/market-thesis/validate.json"
_APPLY_PATH = "/market-thesis/apply.json"


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _read_json_body(environ: dict[str, Any]) -> dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    raw = environ.get("wsgi.input").read(length) if length > 0 else b"{}"
    if not raw:
        return {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MarketThesisError("illegal_transition", f"body is not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise MarketThesisError("illegal_transition", "body must be a JSON object")
    return parsed


def build_validate_response(body: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    document = body.get("document")
    if not isinstance(document, dict):
        return "400 Bad Request", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": "illegal_transition",
            "error": "document is required",
        }
    try:
        state = validate_market_thesis(document)
    except MarketThesisError as exc:
        return "400 Bad Request", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": exc.code,
            "error": str(exc) or exc.code,
        }
    return "200 OK", {
        "kind": "market_thesis_validate",
        "ok": True,
        "workflow_state": state,
        "document": document,
    }


def build_apply_response(body: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    event = str(body.get("event") or "").strip()
    payload = body.get("payload")
    if payload is not None and not isinstance(payload, dict):
        return "400 Bad Request", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": "illegal_transition",
            "error": "payload must be an object",
        }
    document = body.get("document")
    try:
        if document is None and event == "new_draft":
            draft_payload = payload or {}
            document = new_draft(
                thesis_id=str(draft_payload.get("thesis_id") or ""),
                asset_id=str(draft_payload.get("asset_id") or ""),
                symbol=str(draft_payload["symbol"]) if draft_payload.get("symbol") else None,
            )
            event = ""
        if not isinstance(document, dict):
            return "400 Bad Request", {
                "kind": "market_thesis_error",
                "ok": False,
                "code": "illegal_transition",
                "error": "document is required",
            }
        if event:
            document = apply_event(document, event, payload)
        else:
            validate_market_thesis(document)
    except MarketThesisError as exc:
        return "400 Bad Request", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": exc.code,
            "error": str(exc) or exc.code,
        }
    return "200 OK", {
        "kind": "market_thesis_apply",
        "ok": True,
        "workflow_state": document.get("workflow_state"),
        "document": document,
    }


def handle_market_thesis_wsgi_path(
    path: str,
    environ: dict[str, Any],
) -> tuple[str, bytes] | None:
    if path not in {_VALIDATE_PATH, _APPLY_PATH}:
        return None
    method = str(environ.get("REQUEST_METHOD") or "GET").upper()
    if method != "POST":
        return "405 Method Not Allowed", _json_bytes(
            {
                "kind": "market_thesis_error",
                "ok": False,
                "code": "illegal_transition",
                "error": "POST required",
            }
        )
    try:
        body = _read_json_body(environ)
        if path == _VALIDATE_PATH:
            status, payload = build_validate_response(body)
        else:
            status, payload = build_apply_response(body)
    except MarketThesisError as exc:
        status, payload = "400 Bad Request", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": exc.code,
            "error": str(exc) or exc.code,
        }
    except Exception as exc:  # noqa: BLE001 — boundary surfaces unexpected failures
        status, payload = "503 Service Unavailable", {
            "kind": "market_thesis_error",
            "ok": False,
            "code": "illegal_transition",
            "error": str(exc),
        }
    return status, _json_bytes(payload)
