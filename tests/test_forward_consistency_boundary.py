"""Tests for forward consistency display boundary."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.viz.embed_display_boundary import create_display_payload_wsgi_app
from src.viz.forward_consistency_boundary import build_forward_consistency_response


def test_build_response_requires_expiry() -> None:
    out = build_forward_consistency_response({"QUERY_STRING": "asset=BTC"})
    assert out["kind"] == "forward_consistency_error"


def test_forward_consistency_wsgi_route() -> None:
    app = create_display_payload_wsgi_app(lambda _environ: {})
    status: list[str] = []

    def start_response(st: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(st)

    mock_payload = {
        "kind": "forward_consistency_boundary",
        "asset_id": "BTC",
        "status": "NO_ARB",
        "comparable": True,
    }
    with patch(
        "src.viz.forward_consistency_boundary.build_forward_consistency_live",
        return_value=mock_payload,
    ):
        body = b"".join(
            app(
                {
                    "PATH_INFO": "/forward-consistency.json",
                    "QUERY_STRING": "asset=BTC&expiry=2026-12-25",
                },
                start_response,
            )
        )
    assert status[0] == "200 OK"
    payload = json.loads(body.decode("utf-8"))
    assert payload["status"] == "NO_ARB"


def test_not_comparable_for_bybit_asset() -> None:
    with patch(
        "src.data.forward_consistency_quotes.is_asset_enabled",
        return_value=True,
    ), patch(
        "src.data.forward_consistency_quotes.asset_venue",
        return_value="bybit",
    ):
        from src.data.forward_consistency_quotes import build_forward_consistency_live as build_live

        payload = build_live(asset_id="SOL", expiry_date="2026-07-25")
    assert payload["status"] == "NOT_COMPARABLE"
    assert payload["comparable"] is False
