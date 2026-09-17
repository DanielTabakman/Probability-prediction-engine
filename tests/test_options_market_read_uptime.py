"""Unit tests for Options Market Read production uptime validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from scripts.options_market_read_uptime import (
    DEFAULT_DISPLAY_URL,
    DEFAULT_OMR_URL,
    UptimeCheckError,
    run_uptime_check,
)

CHECKED_AT = "2026-06-06T12:05:00Z"
NOW = datetime(2026, 6, 6, 12, 5, tzinfo=UTC)


def _healthy_display() -> dict:
    return {
        "kind": "distribution_display_boundary",
        "as_of_utc": "2026-06-06T12:00:00Z",
        "spot_usd": 100000.0,
        "asset": {"id": "BTC"},
        "series_by_expiry": [
            {
                "asset": "BTC",
                "expiry_date": "2026-07-06",
                "spot_usd": 100000.0,
                "forward_usd": 101000.0,
                "atm_iv_annual": 0.5,
                "quartiles_usd": {
                    "q1_usd": 90000.0,
                    "median_usd": 102500.0,
                    "q3_usd": 120000.0,
                },
            }
        ],
    }


def _healthy_omr() -> dict:
    return {
        "schema_version": "1.3",
        "ruleset_version": "options-market-read.v1.3",
        "asset": "BTC",
        "answer": "As of June 6, 2026 at 12:00 PM UTC, BTC spot is USD 100,000.",
        "as_of": "2026-06-06T12:00:00Z",
        "resolved_expiry": "2026-07-06",
        "metrics": {
            "spot_price": 100000.0,
            "implied_forward_price": 101000.0,
            "median_terminal_price": 102500.0,
            "median_vs_spot_percent": 2.5,
            "atm_iv_percent": 50.0,
            "middle_50_range": {
                "low_price": 90000.0,
                "high_price": 120000.0,
                "width": 30000.0,
            },
        },
    }


class _ScriptedFetcher:
    def __init__(self, omr_payloads: list, display_payloads: list, *, status: int = 200) -> None:
        self.omr_payloads = list(omr_payloads)
        self.display_payloads = list(display_payloads)
        self.status = status
        self.calls: list[str] = []

    def __call__(self, url: str) -> tuple[int, object, str | None]:
        self.calls.append(url)
        if url == DEFAULT_OMR_URL:
            payload = self.omr_payloads.pop(0) if len(self.omr_payloads) > 1 else self.omr_payloads[0]
            return self.status, payload, None if self.status == 200 else f"HTTP {self.status}"
        if url == DEFAULT_DISPLAY_URL:
            payload = (
                self.display_payloads.pop(0) if len(self.display_payloads) > 1 else self.display_payloads[0]
            )
            return self.status, payload, None if self.status == 200 else f"HTTP {self.status}"
        return 0, "", f"unexpected url {url}"


def _run(fetcher, *, now: datetime = NOW) -> str:
    return run_uptime_check(fetcher=fetcher, now=now, network_retries=1, cache_race_retries=1)


def test_healthy_pair_passes() -> None:
    fetcher = _ScriptedFetcher([_healthy_omr()], [_healthy_display()])
    assert _run(fetcher) == CHECKED_AT


def test_stale_as_of_fails() -> None:
    omr = _healthy_omr()
    omr["as_of"] = "2026-06-06T11:30:00Z"
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "as_of_freshness"
    assert "25 minutes" in exc.value.message
    assert DEFAULT_OMR_URL in exc.value.render()
    assert CHECKED_AT in exc.value.render()


def test_missing_answer_fails() -> None:
    omr = _healthy_omr()
    omr["answer"] = "  "
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "answer"


def test_missing_resolved_expiry_fails() -> None:
    omr = _healthy_omr()
    omr["resolved_expiry"] = ""
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "resolved_expiry"


def test_non_finite_metric_fails() -> None:
    omr = _healthy_omr()
    omr["metrics"]["atm_iv_percent"] = float("nan")
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "finite_metrics"


def test_missing_schema_fails() -> None:
    omr = _healthy_omr()
    omr["schema_version"] = ""
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "schema_ruleset"


def test_width_mismatch_fails() -> None:
    omr = _healthy_omr()
    omr["metrics"]["middle_50_range"]["width"] = 12.0
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "range_width"


def test_display_quartile_mismatch_fails() -> None:
    omr = _healthy_omr()
    omr["metrics"]["middle_50_range"]["low_price"] = 88000.0
    omr["metrics"]["middle_50_range"]["width"] = 32000.0
    fetcher = _ScriptedFetcher([omr], [_healthy_display()])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "display_agreement"
    assert "q25" in exc.value.observed


def test_cache_race_retries_then_passes() -> None:
    stale_display = _healthy_display()
    stale_display["as_of_utc"] = "2026-06-06T11:55:00Z"
    fetcher = _ScriptedFetcher(
        [_healthy_omr(), _healthy_omr()],
        [stale_display, _healthy_display()],
    )
    assert _run(fetcher) == CHECKED_AT
    assert fetcher.calls.count(DEFAULT_OMR_URL) == 2
    assert fetcher.calls.count(DEFAULT_DISPLAY_URL) == 2


def test_cache_race_fails_after_retry() -> None:
    stale_display = _healthy_display()
    stale_display["as_of_utc"] = "2026-06-06T11:55:00Z"
    fetcher = _ScriptedFetcher([_healthy_omr()], [stale_display])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "cache_race"


def test_http_failure_is_actionable() -> None:
    fetcher = _ScriptedFetcher([{"error": "down"}], [_healthy_display()], status=503)
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "omr_http_json"
    rendered = exc.value.render()
    assert "FAIL check=omr_http_json" in rendered
    assert DEFAULT_OMR_URL in rendered
    assert CHECKED_AT in rendered


def test_freshness_boundary_is_25_minutes() -> None:
    omr = _healthy_omr()
    omr["as_of"] = (NOW - timedelta(minutes=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
    display = _healthy_display()
    display["as_of_utc"] = omr["as_of"]
    fetcher = _ScriptedFetcher([omr], [display])
    assert _run(fetcher) == CHECKED_AT
    omr["as_of"] = (NOW - timedelta(minutes=25, seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    display["as_of_utc"] = omr["as_of"]
    fetcher = _ScriptedFetcher([omr], [display])
    with pytest.raises(UptimeCheckError) as exc:
        _run(fetcher)
    assert exc.value.check == "as_of_freshness"
