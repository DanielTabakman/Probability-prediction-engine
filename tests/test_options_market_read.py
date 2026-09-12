"""GET /v1/options-market-read contract tests."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from src.engine.implied_distribution import lognormal_distribution_stats
from src.viz.distribution_export import build_distribution_export_rows
from src.viz.display_payload_cache import clear_display_payload_cache, get_cached_display_payload
from src.viz.embed_display_boundary import (
    DISPLAY_DEPTH_FULL,
    DISPLAY_PAYLOAD_KIND,
    build_cached_live_distribution_display_payload,
    build_distribution_display_payload,
    create_display_payload_wsgi_app,
)
from src.viz.options_market_read import (
    OPTIONS_MARKET_READ_HTTP_PATH,
    OptionsMarketReadError,
    build_market_read_response,
    derived_metrics,
    handle_options_market_read_request,
    load_snapshot_from_json,
    render_answer,
    snapshot_from_display_payload,
    snapshot_from_export_rows,
    snapshot_from_payload,
)
from src.viz.options_market_read_assets import resolve_market_read_asset

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "options_market_read"
    / "btc_cached_snapshot.json"
)

DEFAULT_ANSWER = (
    "As of 2026-06-06T12:00:00Z, BTC spot is USD 100,000. "
    "For options expiring 2026-07-06, the options-implied terminal distribution "
    "is centred near USD 102,500, which is +2.5% versus spot. The middle 50% of "
    "priced outcomes runs from USD 90,000 to USD 120,000, and ATM implied "
    "volatility is 50.0%. This is risk-neutral options pricing, not a forecast."
)


def _fixture_snapshot():
    return load_snapshot_from_json(FIXTURE_PATH)


def _request(query: str = "", snapshot=_fixture_snapshot()) -> tuple[str, dict]:
    status, body = handle_options_market_read_request(
        {"QUERY_STRING": query},
        snapshot_loader=lambda: snapshot,
    )
    return status, json.loads(body.decode("utf-8"))


def _call(app, path: str, query: str = "") -> tuple[str, dict[str, str], bytes]:
    status: list[str] = []
    headers: list[tuple[str, str]] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)
        headers.extend(hdrs)

    body = b"".join(app({"PATH_INFO": path, "QUERY_STRING": query}, start_response))
    return status[0], dict(headers), body


def test_no_argument_defaults_to_btc_and_30_days() -> None:
    status, payload = _request("")
    assert status == "200 OK"
    assert payload["asset"] == "BTC"
    assert payload["requested_target_date"] is None
    assert payload["default_horizon_days"] == 30
    assert payload["resolved_expiry"] == "2026-07-06"
    assert payload["ruleset_version"] == "options-market-read.v1"
    assert payload["distribution_method"] == "lognormal"
    assert payload["data_status"] == "cached"
    assert payload["snapshot_id"] == "omr-fixture-btc-2026-06-06"


def test_explicit_target_date() -> None:
    status, payload = _request("asset=BTC&target_date=2026-09-25")
    assert status == "200 OK"
    assert payload["requested_target_date"] == "2026-09-25"
    assert payload["resolved_expiry"] == "2026-09-25"
    assert payload["metrics"]["median_terminal_price"] == 104000.0


def test_exact_expiry_resolution() -> None:
    status, payload = _request("target_date=2026-12-25")
    assert status == "200 OK"
    assert payload["resolved_expiry"] == "2026-12-25"


def test_first_expiry_after_target_date() -> None:
    status, payload = _request("target_date=2026-10-01")
    assert status == "200 OK"
    assert payload["requested_target_date"] == "2026-10-01"
    assert payload["resolved_expiry"] == "2026-12-25"


def test_lowercase_asset_normalization() -> None:
    status, payload = _request("asset=btc")
    assert status == "200 OK"
    assert payload["asset"] == "BTC"
    assert payload["resolved_expiry"] == "2026-07-06"


def test_unsupported_asset() -> None:
    status, payload = _request("asset=ETH")
    assert status == "422 Unprocessable Entity"
    assert payload["error"]["code"] == "unsupported_asset"
    assert payload["error"]["details"]["asset"] == "ETH"


def test_invalid_date() -> None:
    status, payload = _request("target_date=2026-13-40")
    assert status == "400 Bad Request"
    assert payload["error"]["code"] == "invalid_date"


def test_past_date() -> None:
    status, payload = _request("target_date=2026-01-01")
    assert status == "422 Unprocessable Entity"
    assert payload["error"]["code"] == "past_target_date"


def test_missing_snapshot_returns_503() -> None:
    def _missing():
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_prepared_snapshot"},
        )

    status, body = handle_options_market_read_request(
        {"QUERY_STRING": ""},
        snapshot_loader=_missing,
    )
    payload = json.loads(body.decode("utf-8"))
    assert status == "503 Service Unavailable"
    assert payload["error"]["code"] == "snapshot_unavailable"


def test_sol_snapshot_rejected() -> None:
    with pytest.raises(OptionsMarketReadError) as exc:
        snapshot_from_payload(
            {
                "as_of": "2026-06-06T12:00:00Z",
                "asset": "SOL",
                "quote_currency": "USD",
                "expiries": [
                    {
                        "expiry_date": "2026-07-06",
                        "spot_usd": 100.0,
                        "forward_usd": 101.0,
                        "atm_iv_annual": 0.5,
                        "q25_usd": 80.0,
                        "q50_usd": 100.0,
                        "q75_usd": 140.0,
                    }
                ],
            }
        )
    assert exc.value.status == 503


def test_missing_quartile_is_503() -> None:
    with pytest.raises(OptionsMarketReadError) as exc:
        snapshot_from_payload(
            {
                "as_of": "2026-06-06T12:00:00Z",
                "asset": "BTC",
                "quote_currency": "USD",
                "expiries": [
                    {
                        "expiry_date": "2026-07-06",
                        "spot_usd": 100000.0,
                        "forward_usd": 101000.0,
                        "atm_iv_annual": 0.5,
                        "q25_usd": 90000.0,
                        "q50_usd": 102500.0,
                    }
                ],
            }
        )
    assert exc.value.status == 503
    assert exc.value.details["field"] == "q75"


def test_derived_calculations() -> None:
    snapshot = _fixture_snapshot()
    row = next(item for item in snapshot.expiries if item.expiry_date.isoformat() == "2026-07-06")
    metrics = derived_metrics(row)
    assert metrics["middle_50_range"]["low_price"] == 90000.0
    assert metrics["middle_50_range"]["high_price"] == 120000.0
    assert metrics["middle_50_range"]["width"] == 30000.0
    assert metrics["median_vs_spot_percent"] == pytest.approx(((102500.0 / 100000.0) - 1.0) * 100.0)
    assert metrics["atm_iv_percent"] == pytest.approx(50.0)


def test_derived_from_export_lognormal_rows() -> None:
    exp_ts = 1893456000000
    now_ms = exp_ts - 86400000 * 30
    t_years = max(0.02, (exp_ts - now_ms) / 1000 / (365.25 * 24 * 3600))
    stats = lognormal_distribution_stats(100_000.0, 0.5, t_years)
    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.5},
        marks_full_fn=lambda _exp: {"calls": []},
        now_ms=now_ms,
        asset_id="BTC",
    )
    snapshot = snapshot_from_export_rows(rows)
    status, payload = _request("target_date=2030-01-01", snapshot=snapshot)
    assert status == "200 OK"
    rng = payload["metrics"]["middle_50_range"]
    assert rng["low_price"] == pytest.approx(stats["q25_usd"])
    assert rng["high_price"] == pytest.approx(stats["q75_usd"])
    assert rng["width"] == pytest.approx(stats["q75_usd"] - stats["q25_usd"])


def test_exact_deterministic_answer_text() -> None:
    status, payload = _request("")
    assert status == "200 OK"
    assert payload["answer"] == DEFAULT_ANSWER
    snapshot = _fixture_snapshot()
    row = next(item for item in snapshot.expiries if item.expiry_date.isoformat() == "2026-07-06")
    assert render_answer(
        as_of=snapshot.as_of,
        asset="BTC",
        quote_currency="USD",
        resolved_expiry="2026-07-06",
        metrics=derived_metrics(row),
    ) == DEFAULT_ANSWER


def test_identical_repeated_calls() -> None:
    first = _request("")
    second = _request("")
    assert first == second
    status_a, body_a = handle_options_market_read_request(
        {"QUERY_STRING": ""},
        snapshot_loader=_fixture_snapshot,
    )
    status_b, body_b = handle_options_market_read_request(
        {"QUERY_STRING": ""},
        snapshot_loader=_fixture_snapshot,
    )
    assert status_a == status_b == "200 OK"
    assert body_a == body_b


def test_existing_display_routes_unchanged() -> None:
    app = create_display_payload_wsgi_app(
        lambda _environ: {"kind": DISPLAY_PAYLOAD_KIND, "schema_version": 1}
    )
    status, headers, body = _call(app, "/display.json")
    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert json.loads(body.decode("utf-8"))["kind"] == DISPLAY_PAYLOAD_KIND
    status, _headers, body = _call(app, "/full-app")
    assert status == "404 Not Found"
    assert body == b"not found"


def test_wsgi_success_with_env_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH", str(FIXTURE_PATH))
    app = create_display_payload_wsgi_app(lambda _environ: {"kind": DISPLAY_PAYLOAD_KIND})
    status, headers, body = _call(app, OPTIONS_MARKET_READ_HTTP_PATH, "")
    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    payload = json.loads(body.decode("utf-8"))
    assert payload["resolved_expiry"] == "2026-07-06"
    assert payload["answer"] == DEFAULT_ANSWER


def test_display_payload_is_canonical_snapshot_source() -> None:
    exp_ts = 1893456000000
    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.5},
        marks_full_fn=lambda _exp: {"calls": []},
        now_ms=exp_ts - 86400000 * 30,
        asset_id="BTC",
    )
    display = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
        asset_id="BTC",
    )
    snapshot = snapshot_from_display_payload(display)
    spec = resolve_market_read_asset("BTC")
    payload = build_market_read_response(
        spec=spec,
        requested_target_date="2030-01-01",
        target_date=date(2030, 1, 1),
        snapshot=snapshot,
    )
    series = display["series_by_expiry"][0]
    q = series["quartiles_usd"]
    assert payload["as_of"] == "2026-06-06T12:00:00Z"
    assert payload["asset"] == display["asset"]["id"]
    assert payload["metrics"]["spot_price"] == display["spot_usd"]
    assert payload["metrics"]["implied_forward_price"] == series["forward_usd"]
    assert payload["metrics"]["atm_iv_percent"] == pytest.approx(float(series["atm_iv_annual"]) * 100.0)
    assert payload["metrics"]["median_terminal_price"] == q["median_usd"]
    assert payload["metrics"]["middle_50_range"]["low_price"] == q["q1_usd"]
    assert payload["metrics"]["middle_50_range"]["high_price"] == q["q3_usd"]
    assert payload["metrics"]["middle_50_range"]["width"] == pytest.approx(q["q3_usd"] - q["q1_usd"])
    assert payload["resolved_expiry"] == series["expiry_date"]


def test_wsgi_display_and_market_read_share_cached_payload() -> None:
    exp_ts = 1893456000000
    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.5},
        marks_full_fn=lambda _exp: {"calls": []},
        now_ms=exp_ts - 86400000 * 30,
        asset_id="BTC",
    )
    display = build_distribution_display_payload(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        export_rows=rows,
        asset_id="BTC",
    )
    clear_display_payload_cache()
    get_cached_display_payload("BTC", DISPLAY_DEPTH_FULL, lambda: display)
    app = create_display_payload_wsgi_app(build_cached_live_distribution_display_payload)
    display_status, _headers, display_body = _call(app, "/display.json", "asset=BTC&depth=full")
    omr_status, _omr_headers, omr_body = _call(app, OPTIONS_MARKET_READ_HTTP_PATH, "asset=BTC")
    assert display_status == "200 OK"
    assert omr_status == "200 OK"
    display_payload = json.loads(display_body.decode("utf-8"))
    omr = json.loads(omr_body.decode("utf-8"))
    series = display_payload["series_by_expiry"][0]
    q = series["quartiles_usd"]
    assert omr["as_of"] == "2026-06-06T12:00:00Z"
    assert omr["metrics"]["spot_price"] == display_payload["spot_usd"]
    assert omr["metrics"]["implied_forward_price"] == series["forward_usd"]
    assert omr["metrics"]["atm_iv_percent"] == pytest.approx(float(series["atm_iv_annual"]) * 100.0)
    assert omr["metrics"]["median_terminal_price"] == q["median_usd"]
    assert omr["metrics"]["middle_50_range"]["low_price"] == q["q1_usd"]
    assert omr["metrics"]["middle_50_range"]["high_price"] == q["q3_usd"]
    clear_display_payload_cache()
