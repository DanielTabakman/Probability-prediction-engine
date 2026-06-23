"""Strategy suggestion boundary for MSOS expression planning."""

from __future__ import annotations

import json

import pytest

from src.viz.embed_display_boundary import create_display_payload_wsgi_app
from src.viz.strategy_suggestion_boundary import (
    STRATEGY_SUGGESTION_KIND,
    build_strategy_suggestion_response,
)


def _sample_marks() -> dict:
    strikes = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
    calls = [{"strike": k, "mark_btc": 0.04} for k in strikes]
    puts = [{"strike": k, "mark_btc": 0.04} for k in strikes]
    return {"calls": calls, "puts": puts}


@pytest.fixture()
def strategy_mocks(monkeypatch: pytest.MonkeyPatch) -> str:
    expiry_ts = 1893456000000
    expiry_str = "2030-01-01"
    monkeypatch.setattr(
        "src.viz.strategy_suggestion_boundary._load_export_rows",
        lambda: ("2026-06-06T12:00:00+00:00", 99_000.0, []),
    )
    monkeypatch.setattr(
        "src.viz.strategy_suggestion_boundary.cached_option_expiries",
        lambda _n: (
            [{"expiry_date_str": expiry_str, "expiry_ts": expiry_ts}],
            {},
        ),
    )
    monkeypatch.setattr(
        "src.viz.strategy_suggestion_boundary.cached_forward_iv",
        lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.6},
    )
    monkeypatch.setattr(
        "src.viz.strategy_suggestion_boundary.cached_marks_full",
        lambda _exp: _sample_marks(),
    )
    return expiry_str


def test_build_strategy_suggestion_response(strategy_mocks: str) -> None:
    payload = build_strategy_suggestion_response(
        expiry_date=strategy_mocks,
        forward_mult=1.0,
        vol_mult=0.7,
    )
    assert payload["kind"] == STRATEGY_SUGGESTION_KIND
    assert payload["expiry_date"] == strategy_mocks
    suggested = payload["suggested"]
    assert suggested["legs"]
    assert len(suggested["overlay"]["payoff_pct"]) == len(suggested["overlay"]["prices_usd"])
    assert len(payload["market"]["pdf_pct"]) > 0
    assert suggested["summary"]["max_gain_usd"] is not None


def test_strategy_suggestion_wsgi(strategy_mocks: str) -> None:
    app = create_display_payload_wsgi_app(lambda: {})
    status: list[str] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)

    body = b"".join(
        app(
            {
                "PATH_INFO": "/strategy-suggestion.json",
                "QUERY_STRING": f"expiry={strategy_mocks}&forward_mult=1&vol_mult=0.7",
            },
            start_response,
        )
    )
    assert status == ["200 OK"]
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == STRATEGY_SUGGESTION_KIND


def test_strategy_suggestion_wsgi_requires_expiry() -> None:
    app = create_display_payload_wsgi_app(lambda: {})
    status: list[str] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)

    body = b"".join(
        app({"PATH_INFO": "/strategy-suggestion.json", "QUERY_STRING": ""}, start_response)
    )
    assert status == ["400 Bad Request"]
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == "strategy_suggestion_error"
