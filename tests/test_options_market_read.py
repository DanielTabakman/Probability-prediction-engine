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
    build_interpretation,
    build_market_read_response,
    derived_metrics,
    handle_options_market_read_request,
    humanize_as_of,
    load_prepared_snapshot,
    load_snapshot_from_json,
    public_metrics,
    render_answer,
    resolve_expiry,
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
    "As of June 6, 2026 at 12:00 PM UTC, BTC spot is USD 100,000. "
    "For options expiring July 6, 2026, the middle 50% of priced terminal outcomes "
    "runs from USD 90,000 to USD 120,000 (-10.0% to +20.0% versus spot), with a "
    "median of USD 102,500. ATM implied volatility is 50.0% annualized; this "
    "measures priced uncertainty, not direction. Implied volatility rises across "
    "the previous, selected, and next expiries. This is "
    "risk-neutral options pricing, not a forecast or trade recommendation."
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
    assert payload["schema_version"] == "1.2"
    assert payload["ruleset_version"] == "options-market-read.v1.2"
    assert payload["as_of"] == "2026-06-06T12:00:00Z"
    assert payload["as_of_display"] == "June 6, 2026 at 12:00 PM UTC"
    assert payload["effective_target_date"] == "2026-07-06"
    assert payload["expiry_offset_days"] == 0
    assert payload["expiry_resolution"] == "exact"
    assert payload["max_expiry_gap_days"] == 14
    assert payload["distribution_method"] == "lognormal"
    assert payload["data_status"] == "cached"
    assert payload["snapshot_id"] == "omr-fixture-btc-2026-06-06"

    interpretation = payload["interpretation"]
    assert interpretation["days_to_expiry"] == 30
    assert interpretation["range_vs_spot_percent"] == {
        "low_percent": -10.0,
        "high_percent": 20.0,
        "width_percent": 30.0,
    }
    uncertainty = interpretation["uncertainty_context"]
    assert uncertainty["rating"] == "rising_across_expiries"
    assert uncertainty["basis"] == "atm_iv_vs_adjacent_live_expiries"
    assert uncertainty["materiality_threshold_vol_points"] == 1.0
    assert uncertainty["target_expiry"] == {
        "expiry": "2026-07-06",
        "atm_iv_percent": 50.0,
    }
    assert uncertainty["previous_expiry"] == {
        "expiry": "2026-06-27",
        "atm_iv_percent": 48.0,
        "target_minus_neighbor_vol_points": 2.0,
        "relation": "target_higher",
    }
    assert uncertainty["next_expiry"] == {
        "expiry": "2026-09-25",
        "atm_iv_percent": 52.0,
        "target_minus_neighbor_vol_points": -2.0,
        "relation": "target_lower",
    }


def test_human_as_of_keeps_clock_time_and_timezone() -> None:
    assert humanize_as_of("2026-09-13T14:00:59Z") == (
        "September 13, 2026 at 2:00 PM UTC"
    )


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
    assert payload["effective_target_date"] == "2026-12-25"
    assert payload["expiry_offset_days"] == 0
    assert payload["expiry_resolution"] == "exact"
    assert payload["answer"] == (
        "As of June 6, 2026 at 12:00 PM UTC, BTC spot is USD 100,000. "
        "For options expiring December 25, 2026, the middle 50% of priced terminal "
        "outcomes runs from USD 80,000 to USD 140,000 (-20.0% to +40.0% versus "
        "spot), with a median of USD 108,000. ATM implied volatility is 55.0% "
        "annualized; this measures priced uncertainty, not direction. This expiry "
        "prices noticeably more movement than the one available neighboring "
        "expiry. This is risk-neutral options pricing, not a forecast or trade "
        "recommendation."
    )


def test_nearest_later_expiry_has_positive_offset() -> None:
    status, payload = _request("target_date=2026-07-03")
    assert status == "200 OK"
    assert payload["effective_target_date"] == "2026-07-03"
    assert payload["resolved_expiry"] == "2026-07-06"
    assert payload["expiry_offset_days"] == 3
    assert payload["expiry_resolution"] == "nearest_after"
    assert payload["answer"].startswith(
        "The requested target date, July 3, 2026, is represented by the nearest "
        "supported options expiry, July 6, 2026, 3 days after the target. "
    )


def test_nearest_earlier_expiry_has_negative_offset() -> None:
    status, payload = _request("target_date=2026-10-01")
    assert status == "200 OK"
    assert payload["requested_target_date"] == "2026-10-01"
    assert payload["effective_target_date"] == "2026-10-01"
    assert payload["resolved_expiry"] == "2026-09-25"
    assert payload["expiry_offset_days"] == -6
    assert payload["expiry_resolution"] == "nearest_before"
    assert payload["answer"].startswith(
        "The requested target date, October 1, 2026, is represented by the nearest "
        "supported options expiry, September 25, 2026, 6 days before the target. "
    )


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
    raw = derived_metrics(snapshot.expiries[0])
    status, payload = _request("target_date=2030-01-01", snapshot=snapshot)
    assert status == "200 OK"
    assert raw["middle_50_range"]["low_price"] == pytest.approx(stats["q25_usd"])
    assert raw["middle_50_range"]["high_price"] == pytest.approx(stats["q75_usd"])
    assert raw["middle_50_range"]["width"] == pytest.approx(stats["q75_usd"] - stats["q25_usd"])
    assert payload["metrics"] == public_metrics(raw)


def test_exact_deterministic_answer_text() -> None:
    status, payload = _request("")
    assert status == "200 OK"
    assert payload["answer"] == DEFAULT_ANSWER
    snapshot = _fixture_snapshot()
    row = next(item for item in snapshot.expiries if item.expiry_date.isoformat() == "2026-07-06")
    metrics = derived_metrics(row)
    assert render_answer(
        as_of=snapshot.as_of,
        asset="BTC",
        quote_currency="USD",
        resolved_expiry="2026-07-06",
        metrics=metrics,
        interpretation=build_interpretation(snapshot, row, metrics),
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
    raw = derived_metrics(snapshot.expiries[0])
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
    assert raw["spot_price"] == display["spot_usd"]
    assert raw["implied_forward_price"] == series["forward_usd"]
    assert raw["atm_iv_percent"] == pytest.approx(float(series["atm_iv_annual"]) * 100.0)
    assert raw["median_terminal_price"] == q["median_usd"]
    assert raw["middle_50_range"]["low_price"] == q["q1_usd"]
    assert raw["middle_50_range"]["high_price"] == q["q3_usd"]
    assert raw["middle_50_range"]["width"] == pytest.approx(q["q3_usd"] - q["q1_usd"])
    assert payload["metrics"] == public_metrics(raw)
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
    omr_status, _omr_headers, omr_body = _call(
        app, OPTIONS_MARKET_READ_HTTP_PATH, "asset=BTC&target_date=2030-01-01"
    )
    assert display_status == "200 OK"
    assert omr_status == "200 OK"
    display_payload = json.loads(display_body.decode("utf-8"))
    omr = json.loads(omr_body.decode("utf-8"))
    assert display_payload == display
    series = display_payload["series_by_expiry"][0]
    q = series["quartiles_usd"]
    snapshot = snapshot_from_display_payload(display_payload)
    raw = derived_metrics(snapshot.expiries[0])
    assert omr["as_of"] == "2026-06-06T12:00:00Z"
    assert raw["spot_price"] == display_payload["spot_usd"]
    assert raw["implied_forward_price"] == series["forward_usd"]
    assert raw["atm_iv_percent"] == pytest.approx(float(series["atm_iv_annual"]) * 100.0)
    assert raw["median_terminal_price"] == q["median_usd"]
    assert raw["middle_50_range"]["low_price"] == q["q1_usd"]
    assert raw["middle_50_range"]["high_price"] == q["q3_usd"]
    assert omr["metrics"] == public_metrics(raw)
    clear_display_payload_cache()


def _production_example_snapshot():
    return snapshot_from_payload(
        {
            "as_of": "2026-09-12T21:39:59Z",
            "asset": "BTC",
            "quote_currency": "USD",
            "snapshot_id": "prod-display-example",
            "expiries": [
                {
                    "expiry_date": "2026-10-30",
                    "spot_usd": 77228.81,
                    "forward_usd": 77229.44,
                    "atm_iv_annual": 0.3599,
                    "q25_usd": 70168.13,
                    "q50_usd": 76582.66,
                    "q75_usd": 83583.58,
                },
                {
                    "expiry_date": "2026-12-25",
                    "spot_usd": 77228.81,
                    "forward_usd": 77229.5,
                    "atm_iv_annual": 0.384,
                    "q25_usd": 65895.88,
                    "q50_usd": 75633.81,
                    "q75_usd": 86810.79,
                },
            ],
        }
    )


def test_public_json_normalizes_numeric_precision() -> None:
    snapshot = _production_example_snapshot()
    raw = derived_metrics(snapshot.expiries[0])
    assert raw["middle_50_range"]["width"] == pytest.approx(13415.449999999997)
    assert raw["median_vs_spot_percent"] == pytest.approx(-0.8366696314497046)
    status, body = handle_options_market_read_request(
        {"QUERY_STRING": "target_date=2026-10-30"},
        snapshot_loader=lambda: snapshot,
    )
    assert status == "200 OK"
    text = body.decode("utf-8")
    payload = json.loads(text)
    rng = payload["metrics"]["middle_50_range"]
    assert rng["low_price"] == 70168.13
    assert rng["high_price"] == 83583.58
    assert rng["width"] == 13415.45
    assert rng["width"] == pytest.approx(rng["high_price"] - rng["low_price"])
    assert payload["metrics"]["median_vs_spot_percent"] == -0.8367
    assert payload["metrics"]["atm_iv_percent"] == 35.99
    assert payload["metrics"]["spot_price"] == 77228.81
    assert "13415.45" in text
    assert "13415.449999999997" not in text
    assert "-0.8367" in text
    assert "-0.8366696314497046" not in text
    assert payload["answer"] == render_answer(
        as_of=snapshot.as_of,
        asset="BTC",
        quote_currency="USD",
        resolved_expiry="2026-10-30",
        metrics=raw,
        interpretation=build_interpretation(snapshot, snapshot.expiries[0], raw),
    )


def test_public_width_is_rounded_high_minus_low() -> None:
    snapshot = _production_example_snapshot()
    status, payload = _request("target_date=2026-12-25", snapshot=snapshot)
    assert status == "200 OK"
    rng = payload["metrics"]["middle_50_range"]
    assert rng["low_price"] == 65895.88
    assert rng["high_price"] == 86810.79
    assert rng["width"] == 20914.91
    assert rng["width"] == pytest.approx(rng["high_price"] - rng["low_price"])
    assert payload["metrics"]["median_vs_spot_percent"] == -2.0653
    raw = derived_metrics(snapshot.expiries[1])
    assert raw["middle_50_range"]["width"] == pytest.approx(20914.90999999999)
    assert raw["median_vs_spot_percent"] == pytest.approx(-2.065291437224015)


def test_public_json_rejects_nan_and_infinity() -> None:
    base = {
        "spot_price": 100.0,
        "implied_forward_price": 101.0,
        "median_terminal_price": 102.0,
        "median_vs_spot_percent": 2.0,
        "atm_iv_percent": 50.0,
        "middle_50_range": {"low_price": 90.0, "high_price": 120.0, "width": 30.0},
    }
    for field, value in (
        ("spot_price", float("nan")),
        ("atm_iv_percent", float("inf")),
        ("median_vs_spot_percent", float("-inf")),
    ):
        broken = dict(base)
        broken[field] = value
        with pytest.raises(OptionsMarketReadError) as exc:
            public_metrics(broken)
        assert exc.value.status == 503
        assert exc.value.details["field"] == field
    broken_range = dict(base)
    broken_range["middle_50_range"] = {"low_price": 90.0, "high_price": float("nan"), "width": 30.0}
    with pytest.raises(OptionsMarketReadError) as exc:
        public_metrics(broken_range)
    assert exc.value.status == 503
    assert exc.value.details["field"] == "high_price"


def test_snapshot_identity_is_stable() -> None:
    first = _fixture_snapshot()
    second = _fixture_snapshot()
    assert first.snapshot_id == second.snapshot_id == "omr-fixture-btc-2026-06-06"
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
    assert json.loads(body_a.decode("utf-8"))["snapshot_id"] == first.snapshot_id


def test_default_path_does_not_select_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH", raising=False)
    seen: dict[str, str] = {}

    def _display(*, asset_id: str = "BTC"):
        seen["asset_id"] = asset_id
        return _fixture_snapshot()

    monkeypatch.setattr(
        "src.viz.options_market_read.load_display_boundary_snapshot",
        _display,
    )
    snapshot = load_prepared_snapshot("BTC")
    assert seen["asset_id"] == "BTC"
    assert snapshot.snapshot_id == "omr-fixture-btc-2026-06-06"


def _dated_snapshot(expiries: list[str], *, as_of: str = "2026-06-06T12:00:00Z"):
    return snapshot_from_payload(
        {
            "as_of": as_of,
            "asset": "BTC",
            "quote_currency": "USD",
            "snapshot_id": "omr-expiry-resolution",
            "expiries": [
                {
                    "expiry_date": expiry,
                    "spot_usd": 100000.0,
                    "forward_usd": 101000.0,
                    "atm_iv_annual": 0.5,
                    "q25_usd": 90000.0,
                    "q50_usd": 102500.0,
                    "q75_usd": 120000.0,
                }
                for expiry in expiries
            ],
        }
    )


def _term_structure_snapshot(
    previous_iv_percent: float,
    target_iv_percent: float,
    next_iv_percent: float,
):
    return snapshot_from_payload(
        {
            "as_of": "2026-06-06T12:00:00Z",
            "asset": "BTC",
            "quote_currency": "USD",
            "snapshot_id": "omr-term-structure",
            "expiries": [
                {
                    "expiry_date": expiry,
                    "spot_usd": 100000.0,
                    "forward_usd": 101000.0,
                    "atm_iv_annual": iv_percent / 100.0,
                    "q25_usd": 90000.0,
                    "q50_usd": 102500.0,
                    "q75_usd": 120000.0,
                }
                for expiry, iv_percent in (
                    ("2026-06-20", previous_iv_percent),
                    ("2026-07-01", target_iv_percent),
                    ("2026-07-20", next_iv_percent),
                )
            ],
        }
    )


@pytest.mark.parametrize(
    ("previous_iv", "target_iv", "next_iv", "expected_rating"),
    [
        (28.0, 32.0, 29.0, "higher_than_neighbors"),
        (35.0, 32.0, 37.0, "lower_than_neighbors"),
        (30.0, 32.0, 34.0, "rising_across_expiries"),
        (34.0, 32.0, 30.0, "falling_across_expiries"),
        (31.5, 32.0, 32.5, "similar_to_neighbors"),
        (31.5, 32.0, 34.0, "mixed_or_flat"),
    ],
)
def test_adjacent_expiry_uncertainty_ratings(
    previous_iv: float,
    target_iv: float,
    next_iv: float,
    expected_rating: str,
) -> None:
    snapshot = _term_structure_snapshot(previous_iv, target_iv, next_iv)
    status, payload = _request("target_date=2026-07-01", snapshot=snapshot)
    assert status == "200 OK"
    uncertainty = payload["interpretation"]["uncertainty_context"]
    assert uncertainty["rating"] == expected_rating
    assert uncertainty["target_expiry"]["atm_iv_percent"] == target_iv
    assert uncertainty["previous_expiry"]["atm_iv_percent"] == previous_iv
    assert uncertainty["next_expiry"]["atm_iv_percent"] == next_iv


def test_single_expiry_returns_honest_insufficient_context() -> None:
    snapshot = _dated_snapshot(["2026-07-01"])
    status, payload = _request("target_date=2026-07-01", snapshot=snapshot)
    assert status == "200 OK"
    uncertainty = payload["interpretation"]["uncertainty_context"]
    assert uncertainty["rating"] == "insufficient_context"
    assert uncertainty["previous_expiry"] is None
    assert uncertainty["next_expiry"] is None
    assert "not enough adjacent-expiry data" in payload["answer"]


def test_equal_distance_tie_selects_later_expiry() -> None:
    snapshot = _dated_snapshot(["2026-06-10", "2026-06-20"])
    status, payload = _request("target_date=2026-06-15", snapshot=snapshot)
    assert status == "200 OK"
    assert payload["resolved_expiry"] == "2026-06-20"
    assert payload["expiry_offset_days"] == 5
    assert payload["expiry_resolution"] == "nearest_after"


def test_expired_contracts_are_never_selected() -> None:
    snapshot = _dated_snapshot(["2026-06-05", "2026-06-10"])
    resolved = resolve_expiry(
        date(2026, 6, 8),
        [date(2026, 6, 5), date(2026, 6, 10)],
        as_of_date=date(2026, 6, 6),
        max_expiry_gap_days=14,
    )
    assert resolved.expiry_date == date(2026, 6, 10)
    status, payload = _request("target_date=2026-06-08", snapshot=snapshot)
    assert status == "200 OK"
    assert payload["resolved_expiry"] == "2026-06-10"
    assert payload["expiry_offset_days"] == 2


def test_closest_expiry_beyond_gap_returns_422() -> None:
    snapshot = _dated_snapshot(["2026-06-27", "2026-12-25"])
    status, payload = _request("target_date=2026-08-15", snapshot=snapshot)
    assert status == "422 Unprocessable Entity"
    err = payload["error"]
    assert err["code"] == "expiry_not_close_enough"
    assert err["message"] == "No supported options expiry is within 14 days of the target date."
    assert err["details"] == {
        "effective_target_date": "2026-08-15",
        "max_expiry_gap_days": 14,
        "nearest_before": "2026-06-27",
        "nearest_after": "2026-12-25",
    }


def test_fourteen_day_gap_is_permitted() -> None:
    snapshot = _dated_snapshot(["2026-07-04"])
    status, payload = _request("target_date=2026-06-20", snapshot=snapshot)
    assert status == "200 OK"
    assert payload["resolved_expiry"] == "2026-07-04"
    assert payload["expiry_offset_days"] == 14
    assert payload["expiry_resolution"] == "nearest_after"
    assert payload["max_expiry_gap_days"] == 14


def test_default_horizon_discloses_nearest_expiry() -> None:
    snapshot = _dated_snapshot(["2026-07-01"])
    status, payload = _request("", snapshot=snapshot)
    assert status == "200 OK"
    assert payload["effective_target_date"] == "2026-07-06"
    assert payload["resolved_expiry"] == "2026-07-01"
    assert payload["expiry_offset_days"] == -5
    assert payload["expiry_resolution"] == "nearest_before"
    assert payload["answer"].startswith(
        "The default 30-day target is represented by the nearest supported "
        "options expiry, July 1, 2026, 5 days before the target. "
    )
