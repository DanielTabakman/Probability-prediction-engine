"""Display boundary for deterministic Options Horizon comparison rows."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs

from src.engine.options_horizon_comparison import build_options_horizon_comparison

COMPARISON_HTTP_PATH = "/ppe-display-api/horizon/comparison.json"


def _qs_str(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    text = str(raw[0]).strip()
    return text or None


def build_options_horizon_comparison_response(
    environ: dict[str, Any],
    *,
    spot_fn: Any | None = None,
    expiries_fn: Any | None = None,
    forward_iv_fn: Any | None = None,
    marks_full_fn: Any | None = None,
) -> dict[str, Any]:
    if spot_fn is None or expiries_fn is None or forward_iv_fn is None or marks_full_fn is None:
        from src.data.fetch_deribit import (
            fetch_deribit_btc_index,
            fetch_deribit_btc_option_expiries,
            fetch_deribit_btc_option_marks_by_expiry_full,
            fetch_deribit_forward_and_iv_for_expiry,
        )

        spot_fn = spot_fn or fetch_deribit_btc_index
        expiries_fn = expiries_fn or fetch_deribit_btc_option_expiries
        forward_iv_fn = forward_iv_fn or fetch_deribit_forward_and_iv_for_expiry
        marks_full_fn = marks_full_fn or fetch_deribit_btc_option_marks_by_expiry_full

    as_of = _qs_str(environ, "as_of")
    evaluation_time = as_of or datetime.now(tz=UTC).isoformat()
    spot = spot_fn()
    expiries = expiries_fn()
    payload = build_options_horizon_comparison(
        listed_expiries=expiries,
        evaluation_time_utc=evaluation_time,
        spot_usd=float(spot) if spot is not None else None,
        forward_iv_fn=forward_iv_fn,
        marks_full_fn=marks_full_fn,
    )
    payload["meta"] = {
        **payload.get("meta", {}),
        "http_path": COMPARISON_HTTP_PATH,
    }
    return payload


def build_options_horizon_comparison_wsgi_body(environ: dict[str, Any]) -> tuple[str, bytes]:
    try:
        payload = build_options_horizon_comparison_response(environ)
    except Exception as exc:  # noqa: BLE001
        body = json.dumps(
            {"kind": "options_horizon_comparison_error", "error": str(exc)},
            separators=(",", ":"),
            sort_keys=True,
        )
        return "503 Service Unavailable", body.encode("utf-8")
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return "200 OK", body.encode("utf-8")
