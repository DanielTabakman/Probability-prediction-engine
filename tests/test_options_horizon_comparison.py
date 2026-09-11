"""Tests for deterministic option horizon comparison rows."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from src.engine.options_horizon_comparison import build_options_horizon_comparison
from src.viz.options_horizon_comparison_boundary import (
    COMPARISON_HTTP_PATH,
    build_options_horizon_comparison_response,
    build_options_horizon_comparison_wsgi_body,
)


AS_OF = datetime(2026, 1, 1, tzinfo=UTC)


def _expiry(days: int, name: str | None = None) -> dict[str, object]:
    ts = int((AS_OF.timestamp() + days * 24 * 60 * 60) * 1000)
    return {
        "expiry_ts": ts,
        "expiry_date_str": name or datetime.fromtimestamp(ts / 1000, tz=UTC).strftime("%Y-%m-%d"),
    }


def test_bucket_selection_tie_breaks_dedupe_and_orders_by_expiry() -> None:
    expiries = [_expiry(25), _expiry(35), _expiry(63), _expiry(94), _expiry(181), _expiry(367)]

    out = build_options_horizon_comparison(
        listed_expiries=expiries,
        evaluation_time_utc=AS_OF,
        spot_usd=100_000.0,
        forward_iv_fn=lambda _ts, _spot: {
            "forward": 101_000.0,
            "atm_iv": 0.5,
            "quote_time_utc": AS_OF.isoformat(),
        },
        marks_full_fn=lambda _ts: {"calls": [{"open_interest": 80}], "puts": [{"open_interest": 40}]},
    )

    rows = out["rows"]
    assert [row["days_out"] for row in rows] == [35, 63, 94, 181, 367]
    assert rows[0]["target_bucket_days"] == [30]
    assert rows[0]["target_bucket_label"] == "30d"
    assert rows[0]["data_flags"] == []
    assert rows[0]["one_sigma_move_usd"] > 0
    assert out["limitations"][1].startswith("Educational comparison only")


def test_deduplicates_multiple_buckets_to_one_listed_expiry() -> None:
    out = build_options_horizon_comparison(
        listed_expiries=[_expiry(45), _expiry(365)],
        evaluation_time_utc=AS_OF.isoformat(),
        spot_usd=100_000.0,
    )

    assert len(out["rows"]) == 2
    assert out["rows"][0]["target_bucket_days"] == [30, 60, 90, 180]
    assert out["rows"][0]["target_bucket_label"] == "30d / 60d / 90d / 180d"


def test_missing_stale_and_thin_data_degrades_honestly() -> None:
    stale = datetime(2025, 12, 31, 23, 0, tzinfo=UTC).isoformat()
    out = build_options_horizon_comparison(
        listed_expiries=[_expiry(30)],
        evaluation_time_utc=AS_OF,
        spot_usd=100_000.0,
        forward_iv_fn=lambda _ts, _spot: {"quote_time_utc": stale},
        marks_full_fn=lambda _ts: {"calls": [{"open_interest": 1}], "puts": []},
    )

    row = out["rows"][0]
    assert "stale_quote" in row["data_flags"]
    assert "missing_forward" in row["data_flags"]
    assert "missing_atm_iv" in row["data_flags"]
    assert "thin_liquidity" in row["data_flags"]
    assert row["one_sigma_move_usd"] is None
    assert "incomplete" in row["time_decay_language"]


def test_boundary_response_shape_and_no_advice_copy() -> None:
    payload = build_options_horizon_comparison_response(
        {"QUERY_STRING": "as_of=2026-01-01T00:00:00Z"},
        spot_fn=lambda: 100_000.0,
        expiries_fn=lambda: [_expiry(30)],
        forward_iv_fn=lambda _ts, _spot: {
            "forward": 100_500.0,
            "atm_iv": 0.4,
            "quote_time_utc": AS_OF.isoformat(),
        },
        marks_full_fn=lambda _ts: {"calls": [{"open_interest": 100}], "puts": [{"open_interest": 50}]},
    )

    assert payload["kind"] == "options_horizon_comparison"
    assert payload["meta"]["http_path"] == COMPARISON_HTTP_PATH
    assert "not financial advice" in " ".join(payload["limitations"])


def test_boundary_wsgi_body_is_stable_json() -> None:
    from unittest.mock import patch

    with patch(
        "src.viz.options_horizon_comparison_boundary.build_options_horizon_comparison_response",
        return_value={"kind": "options_horizon_comparison", "rows": [], "limitations": []},
    ):
        status, body = build_options_horizon_comparison_wsgi_body({"QUERY_STRING": ""})

    assert status == "200 OK"
    assert json.loads(body.decode("utf-8"))["kind"] == "options_horizon_comparison"
