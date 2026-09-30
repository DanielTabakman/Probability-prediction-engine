"""WSGI boundary for market-thesis.v1 validate / apply."""

from __future__ import annotations

import json

from src.viz.market_thesis_boundary import (
    MARKET_THESIS_APPLY_HTTP_PATH,
    build_apply_response,
    build_validate_response,
    handle_market_thesis_wsgi_path,
)


def test_apply_new_draft_and_belief() -> None:
    status, payload = build_apply_response(
        {
            "document": None,
            "event": "new_draft",
            "payload": {"thesis_id": "mt-btc-1", "asset_id": "BTC", "symbol": "BTC"},
        }
    )
    assert status == "200 OK"
    assert payload["ok"] is True
    assert payload["workflow_state"] == "draft"

    status, believed = build_apply_response(
        {
            "document": payload["document"],
            "event": "set_belief",
            "payload": {
                "source": "user",
                "direction": "long",
                "statement": "BTC higher into the listed expiry.",
                "magnitude": {"kind": "percent_move", "percent_move": 12},
                "uncertainty": {"kind": "wider_than_market"},
                "assumptions": [],
            },
        }
    )
    assert status == "200 OK"
    assert believed["workflow_state"] == "belief_captured"

    status, validated = build_validate_response({"document": believed["document"]})
    assert status == "200 OK"
    assert validated["ok"] is True


def test_handle_rejects_get() -> None:
    result = handle_market_thesis_wsgi_path(
        "/market-thesis/apply.json",
        {"REQUEST_METHOD": "GET", "CONTENT_LENGTH": "0", "wsgi.input": __import__("io").BytesIO(b"")},
    )
    assert result is not None
    status, body = result
    assert status.startswith("405")
    assert json.loads(body.decode("utf-8"))["ok"] is False


def test_public_paths_documented() -> None:
    assert MARKET_THESIS_APPLY_HTTP_PATH.endswith("/market-thesis/apply.json")
