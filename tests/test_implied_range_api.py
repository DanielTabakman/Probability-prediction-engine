"""GET /v1/implied-range contract tests (lognormal IQR, prepared snapshot)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from src.engine.implied_distribution import lognormal_distribution_stats
from src.viz.distribution_export import build_distribution_export_rows
from src.viz.embed_display_boundary import (
    DISPLAY_PAYLOAD_KIND,
    create_display_payload_wsgi_app,
)
from src.viz.implied_range_api import (
    IMPLIED_RANGE_HTTP_PATH,
    ImpliedRangeError,
    handle_implied_range_request,
    load_snapshot_from_json,
    snapshot_from_export_rows,
    snapshot_from_payload,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "implied_range" / "btc_cached_snapshot.json"
)


def _fixture_snapshot():
    return load_snapshot_from_json(FIXTURE_PATH)


def _call(app, path: str, query: str = "") -> tuple[str, dict[str, str], bytes]:
    status: list[str] = []
    headers: list[tuple[str, str]] = []

    def start_response(code: str, hdrs: list[tuple[str, str]]) -> None:
        status.append(code)
        headers.extend(hdrs)

    body = b"".join(
        app(
            {"PATH_INFO": path, "QUERY_STRING": query},
            start_response,
        )
    )
    return status[0], dict(headers), body


def _implied_app(snapshot=_fixture_snapshot()):
    return create_display_payload_wsgi_app(lambda _environ: {"kind": DISPLAY_PAYLOAD_KIND})


def _request(query: str, snapshot=_fixture_snapshot()) -> tuple[str, dict]:
    status, body = handle_implied_range_request(
        {"QUERY_STRING": query},
        snapshot_loader=lambda: snapshot,
    )
    return status, json.loads(body.decode("utf-8"))


def test_exact_expiry_success() -> None:
    status, payload = _request("asset=BTC&target_date=2026-12-25")
    assert status == "200 OK"
    assert payload["schema_version"] == "1.0"
    assert payload["asset"] == "BTC"
    assert payload["currency"] == "USD"
    assert payload["requested_target_date"] == "2026-12-25"
    assert payload["resolved_expiry"] == "2026-12-25"
    assert payload["as_of"] == "2026-06-06T12:00:00Z"
    assert payload["distribution_method"] == "lognormal_iqr"
    assert payload["data_status"] == "cached"
    rng = payload["implied_range"]
    assert rng == {
        "low_usd": 65000.0,
        "median_usd": 85000.0,
        "high_usd": 105000.0,
        "width_usd": 40000.0,
        "percentile_low": 25,
        "percentile_high": 75,
    }


def test_resolves_first_expiry_on_or_after_target() -> None:
    status, payload = _request("asset=BTC&target_date=2026-10-01")
    assert status == "200 OK"
    assert payload["requested_target_date"] == "2026-10-01"
    assert payload["resolved_expiry"] == "2026-12-25"
    assert payload["implied_range"]["low_usd"] == 65000.0


def test_lowercase_btc_normalizes() -> None:
    status, payload = _request("asset=btc&target_date=2026-09-25")
    assert status == "200 OK"
    assert payload["asset"] == "BTC"
    assert payload["resolved_expiry"] == "2026-09-25"


def test_missing_parameter() -> None:
    status, payload = _request("asset=BTC")
    assert status == "400 Bad Request"
    assert payload["error"]["code"] == "missing_parameter"
    assert payload["error"]["details"]["missing"] == ["target_date"]


def test_invalid_date() -> None:
    status, payload = _request("asset=BTC&target_date=2026-13-40")
    assert status == "400 Bad Request"
    assert payload["error"]["code"] == "invalid_date"
    assert payload["error"]["details"]["target_date"] == "2026-13-40"


def test_unsupported_asset() -> None:
    status, payload = _request("asset=ETH&target_date=2026-12-25")
    assert status == "422 Unprocessable Entity"
    assert payload["error"] == {
        "code": "unsupported_asset",
        "message": "V1 supports BTC only.",
        "details": {"asset": "ETH"},
    }


def test_past_target_date() -> None:
    status, payload = _request("asset=BTC&target_date=2026-01-01")
    assert status == "422 Unprocessable Entity"
    assert payload["error"]["code"] == "past_target_date"
    assert payload["error"]["details"]["target_date"] == "2026-01-01"


def test_no_later_expiry() -> None:
    status, payload = _request("asset=BTC&target_date=2028-01-01")
    assert status == "422 Unprocessable Entity"
    assert payload["error"]["code"] == "expiry_unavailable"


def test_missing_snapshot_returns_503() -> None:
    def _missing():
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_prepared_snapshot"},
        )

    status, body = handle_implied_range_request(
        {"QUERY_STRING": "asset=BTC&target_date=2026-12-25"},
        snapshot_loader=_missing,
    )
    payload = json.loads(body.decode("utf-8"))
    assert status == "503 Service Unavailable"
    assert payload["error"]["code"] == "snapshot_unavailable"


def test_sol_snapshot_rejected_for_btc_request() -> None:
    with pytest.raises(ImpliedRangeError) as exc:
        snapshot_from_payload(
            {
                "as_of": "2026-06-06T12:00:00Z",
                "asset": "SOL",
                "expiries": [
                    {
                        "expiry_date": "2026-12-25",
                        "q25_usd": 80.0,
                        "q50_usd": 100.0,
                        "q75_usd": 140.0,
                    }
                ],
            }
        )
    assert exc.value.status == 503
    assert exc.value.details["asset"] == "SOL"


def test_inconsistent_as_of_is_503() -> None:
    with pytest.raises(ImpliedRangeError) as exc:
        snapshot_from_export_rows(
            [
                {
                    "distribution": "lognormal_reference",
                    "as_of_utc": "2026-06-06T12:00:00+00:00",
                    "asset": "BTC",
                    "expiry_date": "2026-12-25",
                    "q25_usd": "65000.00",
                    "q50_usd": "85000.00",
                    "q75_usd": "105000.00",
                },
                {
                    "distribution": "lognormal_reference",
                    "as_of_utc": "2026-06-07T12:00:00+00:00",
                    "asset": "BTC",
                    "expiry_date": "2027-03-26",
                    "q25_usd": "60000.00",
                    "q50_usd": "90000.00",
                    "q75_usd": "120000.00",
                },
            ]
        )
    assert exc.value.status == 503
    assert exc.value.code == "inconsistent_snapshot"


def test_missing_quartile_is_503() -> None:
    with pytest.raises(ImpliedRangeError) as exc:
        snapshot_from_payload(
            {
                "as_of": "2026-06-06T12:00:00Z",
                "asset": "BTC",
                "expiries": [
                    {
                        "expiry_date": "2026-12-25",
                        "q25_usd": 65000.0,
                        "q50_usd": 85000.0,
                    }
                ],
            }
        )
    assert exc.value.status == 503
    assert exc.value.details["field"] == "q75_usd"


def test_iqr_width_matches_exported_lognormal_quartiles() -> None:
    stats = lognormal_distribution_stats(100_000.0, 0.5, 0.25)
    expected_width = stats["q75_usd"] - stats["q25_usd"]
    snapshot = snapshot_from_payload(
        {
            "as_of": "2026-06-06T12:00:00Z",
            "asset": "BTC",
            "expiries": [
                {
                    "expiry_date": "2026-12-25",
                    "q25_usd": stats["q25_usd"],
                    "q50_usd": stats["q50_usd"],
                    "q75_usd": stats["q75_usd"],
                }
            ],
        }
    )
    status, payload = _request("asset=BTC&target_date=2026-12-25", snapshot=snapshot)
    assert status == "200 OK"
    rng = payload["implied_range"]
    assert rng["low_usd"] == stats["q25_usd"]
    assert rng["median_usd"] == stats["q50_usd"]
    assert rng["high_usd"] == stats["q75_usd"]
    assert rng["width_usd"] == expected_width


def test_reuses_distribution_export_lognormal_rows() -> None:
    exp_ts = 1893456000000
    rows = build_distribution_export_rows(
        as_of_utc="2026-06-06T12:00:00+00:00",
        spot_usd=99_000.0,
        expiries=[{"expiry_date_str": "2030-01-01", "expiry_ts": exp_ts}],
        forward_iv_fn=lambda _exp, _spot: {"forward": 100_000.0, "atm_iv": 0.6},
        marks_full_fn=lambda _exp: {"calls": []},
        now_ms=exp_ts - 86400000 * 30,
        asset_id="BTC",
    )
    snapshot = snapshot_from_export_rows(rows)
    status, payload = _request("asset=BTC&target_date=2030-01-01", snapshot=snapshot)
    assert status == "200 OK"
    assert payload["resolved_expiry"] == "2030-01-01"
    assert payload["as_of"] == "2026-06-06T12:00:00Z"
    rng = payload["implied_range"]
    assert rng["width_usd"] == rng["high_usd"] - rng["low_usd"]
    assert rng["percentile_low"] == 25
    assert rng["percentile_high"] == 75


def test_existing_display_routes_unchanged() -> None:
    app = create_display_payload_wsgi_app(
        lambda _environ: {"kind": DISPLAY_PAYLOAD_KIND, "schema_version": 1}
    )
    status, headers, body = _call(app, "/display.json")
    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    parsed = json.loads(body.decode("utf-8"))
    assert parsed["kind"] == DISPLAY_PAYLOAD_KIND

    status, _headers, body = _call(app, "/full-app")
    assert status == "404 Not Found"
    assert body == b"not found"


def test_wsgi_serves_implied_range_json() -> None:
    app = _implied_app()
    # The production app loads prepared snapshots; inject via env in this unit
    # by calling the handler through PATH_INFO with a patched loader is covered
    # above. Here we only assert the route is mounted and returns JSON errors
    # with the public path (no snapshot in default artifacts).
    status, headers, body = _call(app, IMPLIED_RANGE_HTTP_PATH, "asset=BTC")
    assert status == "400 Bad Request"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert json.loads(body.decode("utf-8"))["error"]["code"] == "missing_parameter"


def test_wsgi_success_with_env_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPE_IMPLIED_RANGE_SNAPSHOT_PATH", str(FIXTURE_PATH))
    app = create_display_payload_wsgi_app(lambda _environ: {"kind": DISPLAY_PAYLOAD_KIND})
    status, headers, body = _call(
        app, IMPLIED_RANGE_HTTP_PATH, "asset=BTC&target_date=2026-12-25"
    )
    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    payload = json.loads(body.decode("utf-8"))
    assert payload["resolved_expiry"] == "2026-12-25"
    assert payload["implied_range"]["width_usd"] == 40000.0
    assert date.fromisoformat(payload["resolved_expiry"]) >= date.fromisoformat(
        payload["requested_target_date"]
    )
