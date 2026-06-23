"""Embed display boundary contracts (Strategy Lab distribution region)."""

from __future__ import annotations

import json

import pytest

from src.viz.distribution_export import build_distribution_export_rows
from src.viz.curve_display_labels import build_curve_display_labels
from src.viz.embed_display_boundary import (
    BELIEF_OVERLAY_KIND,
    DISPLAY_PAYLOAD_HTTP_PATH,
    DISPLAY_PAYLOAD_KIND,
    DISPLAY_PAYLOAD_MODE,
    DISPLAY_PAYLOAD_SCHEMA_VERSION,
    EMBED_ONLY_FALLBACK_MODE,
    build_belief_overlay_response,
    build_distribution_display_payload,
    build_chart_series_from_export_row,
    clamp_belief_mult,
    create_display_payload_wsgi_app,
    serialize_distribution_display_payload,
)
from src.viz.implied_lab_legibility import DIST_SUMMARY_ANCHOR_ID
from src.viz.strategy_suggestion_boundary import (
    STRATEGY_SUGGESTION_KIND,
    build_strategy_suggestion_response,
)


def _sample_export_rows() -> list[dict[str, str]]:
    exp_ts = 1893456000000

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 100_000.0, "atm_iv": 0.6}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    return build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
    )


def test_display_payload_schema_and_summary() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    assert payload["schema_version"] == DISPLAY_PAYLOAD_SCHEMA_VERSION
    assert payload["kind"] == DISPLAY_PAYLOAD_KIND
    assert payload["anchor_id"] == DIST_SUMMARY_ANCHOR_ID
    assert payload["summary"]["row_count"] == 2
    assert payload["meta"]["http_path"] == DISPLAY_PAYLOAD_HTTP_PATH
    assert payload["meta"]["display_mode"] == DISPLAY_PAYLOAD_MODE
    assert payload["meta"]["fallback_mode"] == EMBED_ONLY_FALLBACK_MODE
    assert payload["meta"]["embed_json_query"] == "?embed_only=1&format=json"
    assert len(payload["series_by_expiry"]) == 1
    assert "belief_presets" in payload
    assert set(payload["belief_presets"]) == {
        "higher",
        "lower",
        "more_volatility",
        "less_volatility",
    }
    primary = payload["series_by_expiry"][0]
    assert "belief_presets" in primary
    assert "curve_labels" in payload
    assert payload["curve_labels"]["market_legend"] == "Market view [Black–Scholes lognormal]"
    assert primary["curve_labels"]["market_legend"] == payload["curve_labels"]["market_legend"]
    belief_higher = payload["belief_presets"]["higher"]["pdf_pct"]
    assert len(belief_higher) == len(primary["pdf_pct"])
    assert max(belief_higher) > 0


def test_chart_series_from_lognormal_row() -> None:
    rows = _sample_export_rows()
    lognormal = next(r for r in rows if r["distribution"] == "lognormal_reference")
    series = build_chart_series_from_export_row(lognormal)
    assert series is not None
    assert len(series["prices_usd"]) == len(series["pdf_pct"]) == 80
    assert series["mean_usd"] == 100_000.0
    q = series["quartiles_usd"]
    assert q["q1_usd"] is not None and q["median_usd"] is not None and q["q3_usd"] is not None
    assert q["q1_usd"] <= q["median_usd"] <= q["q3_usd"]


def test_bl_skipped_row_omits_series() -> None:
    rows = _sample_export_rows()
    bl = next(r for r in rows if r["distribution"] == "market_implied_bl")
    assert build_chart_series_from_export_row(bl) is None


def test_wsgi_app_serves_json() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    app = create_display_payload_wsgi_app(lambda: payload)

    status: list[str] = []
    headers: list[tuple[str, str]] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)
        headers.extend(hdrs)

    body = b"".join(app({"PATH_INFO": "/display.json"}, start_response))
    assert status == ["200 OK"]
    assert any(h == ("Content-Type", "application/json; charset=utf-8") for h in headers)
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == DISPLAY_PAYLOAD_KIND
    assert any(h == ("Cache-Control", "no-store") for h in headers)


def test_wsgi_app_rejects_unknown_paths() -> None:
    app = create_display_payload_wsgi_app(lambda: {})

    status: list[str] = []
    headers: list[tuple[str, str]] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)
        headers.extend(hdrs)

    body = b"".join(app({"PATH_INFO": "/full-app"}, start_response))
    assert status == ["404 Not Found"]
    assert any(h == ("Content-Type", "text/plain; charset=utf-8") for h in headers)
    assert body == b"not found"


def test_wsgi_app_upstream_failure_returns_503_json() -> None:
    def _boom() -> dict:
        raise RuntimeError("Deribit BTC index unavailable for embed display boundary.")

    app = create_display_payload_wsgi_app(_boom)
    status: list[str] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)

    body = b"".join(app({"PATH_INFO": "/display.json"}, start_response))
    assert status == ["503 Service Unavailable"]
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == "display_error"
    assert "Deribit" in parsed["error"]


def test_spot_from_cached_deribit_index_accepts_float(monkeypatch) -> None:
    from src.viz import embed_only_lab as lab

    monkeypatch.setattr(lab, "cached_deribit_index", lambda: 104_320.5)
    assert lab._spot_from_cached_deribit_index() == 104_320.5


def test_belief_overlay_response_and_wsgi() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    expiry = payload["series_by_expiry"][0]["expiry_date"]
    overlay = build_belief_overlay_response(
        payload,
        expiry_date=expiry,
        forward_mult=1.08,
        vol_mult=1.2,
    )
    assert overlay["kind"] == BELIEF_OVERLAY_KIND
    assert overlay["expiry_date"] == expiry
    assert len(overlay["pdf_pct"]) == len(payload["series_by_expiry"][0]["pdf_pct"])
    assert overlay["forward_mult"] == clamp_belief_mult("forward_mult", 1.08)
    assert overlay["vol_mult"] == clamp_belief_mult("vol_mult", 1.2)
    assert overlay["curve_labels"]["belief_legend"] == "Your view [Belief lognormal]"

    app = create_display_payload_wsgi_app(lambda: payload)
    status: list[str] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)

    body = b"".join(
        app(
            {
                "PATH_INFO": "/belief-overlay.json",
                "QUERY_STRING": f"expiry={expiry}&forward_mult=1.08&vol_mult=1.2",
            },
            start_response,
        )
    )
    assert status == ["200 OK"]
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == BELIEF_OVERLAY_KIND
    assert parsed["expiry_date"] == expiry


def test_wsgi_belief_overlay_requires_expiry() -> None:
    app = create_display_payload_wsgi_app(lambda: {})
    status: list[str] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)

    body = b"".join(app({"PATH_INFO": "/belief-overlay.json", "QUERY_STRING": ""}, start_response))
    assert status == ["400 Bad Request"]
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == "belief_overlay_error"


def test_payload_serializes_deterministically() -> None:
    rows = _sample_export_rows()
    payload = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
    )
    a = serialize_distribution_display_payload(payload)
    b = serialize_distribution_display_payload(payload)
    assert a == b
    assert json.loads(a)["spot_usd"] == 99_000.0


def _strategy_sample_marks() -> dict:
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
        lambda _exp: _strategy_sample_marks(),
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
    assert len(suggested["overlay"]["payoff_usd"]) == len(suggested["overlay"]["prices_usd"])
    assert len(payload["market"]["pdf_pct"]) > 0
    assert payload["market"]["curve_labels"]["market_legend"] == "Market view [Black–Scholes lognormal]"
    assert suggested["summary"]["max_gain_usd"] is not None


def test_curve_display_labels_ssot() -> None:
    labels = build_curve_display_labels()
    assert labels["market_legend"] == "Market view [Black–Scholes lognormal]"
    assert labels["belief_legend"] == "Your view [Belief lognormal]"
    assert labels["payoff_legend"] == "Payoff at expiry [Structure P&L]"


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
