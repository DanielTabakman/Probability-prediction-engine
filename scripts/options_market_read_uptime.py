#!/usr/bin/env python3
"""Production synthetic check for Options Market Read and its display payload.

Used by `.github/workflows/uptime-healthcheck.yml`. Validation is deterministic
and does not call an LLM. Failures print the check name, observed values, UTC
check time, and URL. The established alert is a failed GitHub Actions run.

Usage:
  python scripts/options_market_read_uptime.py
  python scripts/options_market_read_uptime.py --omr-url URL --display-url URL
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.viz.options_market_read import (
    derived_metrics,
    public_metrics,
    snapshot_from_display_payload,
)

DEFAULT_OMR_URL = "https://marketstructureos.com/v1/options-market-read"
DEFAULT_DISPLAY_URL = (
    "https://marketstructureos.com/ppe-display-api/display.json?asset=BTC&depth=full"
)
USER_AGENT = "ppe-options-market-read-uptime/1"
TIMEOUT_S = 30.0
NETWORK_RETRIES = 3
CACHE_RACE_RETRIES = 2
MAX_AS_OF_AGE = timedelta(minutes=25)
REQUIRED_METRIC_FIELDS = (
    "spot_price",
    "implied_forward_price",
    "median_terminal_price",
    "median_vs_spot_percent",
    "atm_iv_percent",
)
REQUIRED_RANGE_FIELDS = ("low_price", "high_price", "width")

Fetcher = Callable[[str], tuple[int, Any, str | None]]


class UptimeCheckError(Exception):
    def __init__(
        self,
        check: str,
        *,
        observed: Any,
        url: str,
        checked_at: str,
        message: str,
    ) -> None:
        super().__init__(message)
        self.check = check
        self.observed = observed
        self.url = url
        self.checked_at = checked_at
        self.message = message

    def render(self) -> str:
        observed = self.observed
        if not isinstance(observed, str):
            observed = json.dumps(observed, default=str, sort_keys=True)
        return (
            f"FAIL check={self.check} observed={observed} "
            f"checked_at_utc={self.checked_at} url={self.url} "
            f"detail={self.message}"
        )


def utc_now() -> datetime:
    return datetime.now(UTC)


def format_checked_at(moment: datetime | None = None) -> str:
    value = moment or utc_now()
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fail(
    check: str,
    *,
    observed: Any,
    url: str,
    checked_at: str,
    message: str,
) -> None:
    raise UptimeCheckError(
        check,
        observed=observed,
        url=url,
        checked_at=checked_at,
        message=message,
    )


def fetch_json(url: str, *, timeout: float = TIMEOUT_S) -> tuple[int, Any, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                return resp.status, raw[:200].decode("utf-8", "replace"), f"non_json: {exc}"
            return resp.status, payload, None
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        parsed: Any
        try:
            parsed = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            parsed = body.decode("utf-8", "replace") if body else ""
        return exc.code, parsed, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return 0, "", str(exc.reason)
    except TimeoutError as exc:
        return 0, "", str(exc)


def fetch_json_with_retries(
    url: str,
    *,
    fetcher: Fetcher = fetch_json,
    retries: int = NETWORK_RETRIES,
    timeout: float = TIMEOUT_S,
) -> tuple[int, Any, str | None]:
    last: tuple[int, Any, str | None] = (0, "", "no_attempt")
    for attempt in range(retries):
        if fetcher is fetch_json:
            last = fetch_json(url, timeout=timeout)
        else:
            last = fetcher(url)
        status, _payload, err = last
        if status == 200 and err is None:
            return last
        if status > 0:
            return last
        if attempt + 1 < retries:
            time.sleep(min(2 ** attempt, 4))
    return last


def _require_object(payload: Any, *, check: str, url: str, checked_at: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        _fail(
            check,
            observed=type(payload).__name__,
            url=url,
            checked_at=checked_at,
            message="response is not a JSON object",
        )
    return payload


def _require_http_json(
    status: int,
    payload: Any,
    err: str | None,
    *,
    check: str,
    url: str,
    checked_at: str,
) -> dict[str, Any]:
    if status != 200 or err is not None:
        _fail(
            check,
            observed={"http_status": status, "error": err, "body": payload},
            url=url,
            checked_at=checked_at,
            message="endpoint did not return HTTP 200 JSON",
        )
    return _require_object(payload, check=check, url=url, checked_at=checked_at)


def _require_finite(value: Any, field: str, *, url: str, checked_at: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(
            "finite_metrics",
            observed={field: value},
            url=url,
            checked_at=checked_at,
            message=f"{field} is missing or not numeric",
        )
    parsed = float(value)
    if not math.isfinite(parsed):
        _fail(
            "finite_metrics",
            observed={field: parsed},
            url=url,
            checked_at=checked_at,
            message=f"{field} is not finite",
        )
    return parsed


def parse_as_of(raw: Any, *, url: str, checked_at: str) -> datetime:
    text = str(raw or "").strip()
    if not text:
        _fail("as_of", observed=raw, url=url, checked_at=checked_at, message="as_of is missing")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        _fail("as_of", observed=raw, url=url, checked_at=checked_at, message="as_of is not a valid timestamp")
    raise AssertionError("unreachable")


def display_as_of(payload: dict[str, Any]) -> str:
    return str(payload.get("as_of_utc") or payload.get("as_of") or "").strip()


def expected_public_metrics(display: dict[str, Any], resolved_expiry: str) -> dict[str, Any]:
    snapshot = snapshot_from_display_payload(display)
    row = next(
        (item for item in snapshot.expiries if item.expiry_date.isoformat() == resolved_expiry),
        None,
    )
    if row is None:
        raise KeyError(resolved_expiry)
    return public_metrics(derived_metrics(row))


def validate_omr_document(
    omr: dict[str, Any],
    *,
    url: str,
    checked_at: str,
    now: datetime,
) -> None:
    schema = str(omr.get("schema_version") or "").strip()
    ruleset = str(omr.get("ruleset_version") or "").strip()
    if not schema or not ruleset:
        _fail(
            "schema_ruleset",
            observed={"schema_version": omr.get("schema_version"), "ruleset_version": omr.get("ruleset_version")},
            url=url,
            checked_at=checked_at,
            message="schema_version and ruleset_version must be present",
        )
    asset = str(omr.get("asset") or "").strip().upper()
    if asset != "BTC":
        _fail("asset", observed=omr.get("asset"), url=url, checked_at=checked_at, message="asset must be BTC")
    answer = omr.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        _fail("answer", observed=answer, url=url, checked_at=checked_at, message="answer must be nonempty")
    resolved = str(omr.get("resolved_expiry") or "").strip()
    if not resolved:
        _fail(
            "resolved_expiry",
            observed=omr.get("resolved_expiry"),
            url=url,
            checked_at=checked_at,
            message="resolved expiry is missing",
        )
    as_of = parse_as_of(omr.get("as_of"), url=url, checked_at=checked_at)
    age = now - as_of
    if age > MAX_AS_OF_AGE:
        _fail(
            "as_of_freshness",
            observed={
                "as_of": omr.get("as_of"),
                "age_seconds": int(age.total_seconds()),
                "limit_seconds": int(MAX_AS_OF_AGE.total_seconds()),
            },
            url=url,
            checked_at=checked_at,
            message="as_of is older than 25 minutes",
        )
    metrics = omr.get("metrics")
    if not isinstance(metrics, dict):
        _fail("finite_metrics", observed=metrics, url=url, checked_at=checked_at, message="metrics object missing")
    for field in REQUIRED_METRIC_FIELDS:
        _require_finite(metrics.get(field), field, url=url, checked_at=checked_at)
    middle = metrics.get("middle_50_range")
    if not isinstance(middle, dict):
        _fail(
            "finite_metrics",
            observed=middle,
            url=url,
            checked_at=checked_at,
            message="middle_50_range missing",
        )
    for field in REQUIRED_RANGE_FIELDS:
        _require_finite(middle.get(field), f"middle_50_range.{field}", url=url, checked_at=checked_at)
    low = float(middle["low_price"])
    high = float(middle["high_price"])
    width = float(middle["width"])
    expected_width = high - low
    if abs(width - expected_width) > 1e-9:
        _fail(
            "range_width",
            observed={"low_price": low, "high_price": high, "width": width},
            url=url,
            checked_at=checked_at,
            message="range width must equal rounded high minus rounded low",
        )


def validate_display_agreement(
    omr: dict[str, Any],
    display: dict[str, Any],
    *,
    omr_url: str,
    display_url: str,
    checked_at: str,
) -> None:
    resolved = str(omr["resolved_expiry"])
    try:
        expected = expected_public_metrics(display, resolved)
    except Exception as exc:  # noqa: BLE001 — convert mapping failures into the uptime contract
        _fail(
            "display_agreement",
            observed={"resolved_expiry": resolved, "error": str(exc)},
            url=display_url,
            checked_at=checked_at,
            message="could not map display.json onto the selected expiry",
        )
        return
    actual = omr["metrics"]
    compared = {
        "spot_price": (actual["spot_price"], expected["spot_price"]),
        "atm_iv_percent": (actual["atm_iv_percent"], expected["atm_iv_percent"]),
        "q25": (actual["middle_50_range"]["low_price"], expected["middle_50_range"]["low_price"]),
        "median": (actual["median_terminal_price"], expected["median_terminal_price"]),
        "q75": (actual["middle_50_range"]["high_price"], expected["middle_50_range"]["high_price"]),
    }
    mismatches = {
        name: {"omr": left, "display": right}
        for name, (left, right) in compared.items()
        if left != right
    }
    if mismatches:
        _fail(
            "display_agreement",
            observed=mismatches,
            url=omr_url,
            checked_at=checked_at,
            message="OMR public metrics disagree with display.json after documented rounding",
        )


def validate_pair(
    omr_status: int,
    omr_payload: Any,
    omr_err: str | None,
    display_status: int,
    display_payload: Any,
    display_err: str | None,
    *,
    omr_url: str,
    display_url: str,
    checked_at: str,
    now: datetime,
) -> None:
    omr = _require_http_json(
        omr_status, omr_payload, omr_err, check="omr_http_json", url=omr_url, checked_at=checked_at
    )
    display = _require_http_json(
        display_status,
        display_payload,
        display_err,
        check="display_http_json",
        url=display_url,
        checked_at=checked_at,
    )
    validate_omr_document(omr, url=omr_url, checked_at=checked_at, now=now)
    omr_as_of = str(omr.get("as_of") or "").strip()
    display_stamp = display_as_of(display)
    if omr_as_of and display_stamp:
        omr_norm = parse_as_of(omr_as_of, url=omr_url, checked_at=checked_at).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            display_norm = parse_as_of(display_stamp, url=display_url, checked_at=checked_at).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        except UptimeCheckError:
            _fail(
                "display_agreement",
                observed={"display_as_of": display_stamp},
                url=display_url,
                checked_at=checked_at,
                message="display.json as_of is not a valid timestamp",
            )
            return
        if omr_norm != display_norm:
            _fail(
                "cache_race",
                observed={"omr_as_of": omr_norm, "display_as_of": display_norm},
                url=omr_url,
                checked_at=checked_at,
                message="snapshot times differ between the two requests",
            )
    validate_display_agreement(
        omr,
        display,
        omr_url=omr_url,
        display_url=display_url,
        checked_at=checked_at,
    )


def run_uptime_check(
    *,
    omr_url: str = DEFAULT_OMR_URL,
    display_url: str = DEFAULT_DISPLAY_URL,
    fetcher: Fetcher | None = None,
    now: datetime | None = None,
    network_retries: int = NETWORK_RETRIES,
    cache_race_retries: int = CACHE_RACE_RETRIES,
) -> str:
    checked_at = format_checked_at(now)
    moment = now or utc_now()
    fetch = fetcher or fetch_json
    last_error: UptimeCheckError | None = None
    attempts = cache_race_retries + 1
    for attempt in range(attempts):
        omr_status, omr_payload, omr_err = fetch_json_with_retries(
            omr_url, fetcher=fetch, retries=network_retries
        )
        display_status, display_payload, display_err = fetch_json_with_retries(
            display_url, fetcher=fetch, retries=network_retries
        )
        try:
            validate_pair(
                omr_status,
                omr_payload,
                omr_err,
                display_status,
                display_payload,
                display_err,
                omr_url=omr_url,
                display_url=display_url,
                checked_at=checked_at,
                now=moment,
            )
            return checked_at
        except UptimeCheckError as exc:
            last_error = exc
            if exc.check == "cache_race" and attempt + 1 < attempts:
                continue
            raise
    assert last_error is not None
    raise last_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Options Market Read production uptime check")
    parser.add_argument("--omr-url", default=DEFAULT_OMR_URL)
    parser.add_argument("--display-url", default=DEFAULT_DISPLAY_URL)
    args = parser.parse_args()
    try:
        checked_at = run_uptime_check(omr_url=args.omr_url, display_url=args.display_url)
    except UptimeCheckError as exc:
        print(exc.render(), file=sys.stderr)
        return 1
    print(f"OK checked_at_utc={checked_at} omr_url={args.omr_url} display_url={args.display_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
