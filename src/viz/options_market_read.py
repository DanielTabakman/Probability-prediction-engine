"""Options Market Read — GET /v1/options-market-read.

HTTP validation and snapshot orchestration live here. Quartiles, spot, forward,
and ATM IV come from prepared PPE export rows. This module does not recompute
option-implied densities.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs

from src.viz.options_market_read_assets import (
    DEFAULT_ASSET_ID,
    MarketReadAsset,
    resolve_market_read_asset,
)

OPTIONS_MARKET_READ_HTTP_PATH = "/v1/options-market-read"
SCHEMA_VERSION = "1.2"
RULESET_VERSION = "options-market-read.v1.2"
RESOLUTION_EXACT = "exact"
RESOLUTION_NEAREST_BEFORE = "nearest_before"
RESOLUTION_NEAREST_AFTER = "nearest_after"
DISTRIBUTION_METHOD = "lognormal"
LOGNORMAL_DISTRIBUTION = "lognormal_reference"
DATA_STATUS_CACHED = "cached"
DEFAULT_HORIZON_DAYS = 30
PUBLIC_PRICE_DECIMALS = 2
PUBLIC_IV_DECIMALS = 2
PUBLIC_MEDIAN_VS_SPOT_DECIMALS = 4
PUBLIC_CONTEXT_PERCENT_DECIMALS = 2
TERM_STRUCTURE_MATERIALITY_VOL_POINTS = 1.0

RELATION_TARGET_HIGHER = "target_higher"
RELATION_TARGET_LOWER = "target_lower"
RELATION_SIMILAR = "similar"

UNCERTAINTY_HIGHER_THAN_NEIGHBORS = "higher_than_neighbors"
UNCERTAINTY_LOWER_THAN_NEIGHBORS = "lower_than_neighbors"
UNCERTAINTY_RISING = "rising_across_expiries"
UNCERTAINTY_FALLING = "falling_across_expiries"
UNCERTAINTY_SIMILAR = "similar_to_neighbors"
UNCERTAINTY_MIXED = "mixed_or_flat"
UNCERTAINTY_HIGHER_THAN_AVAILABLE = "higher_than_available_neighbor"
UNCERTAINTY_LOWER_THAN_AVAILABLE = "lower_than_available_neighbor"
UNCERTAINTY_SIMILAR_TO_AVAILABLE = "similar_to_available_neighbor"
UNCERTAINTY_UNAVAILABLE = "insufficient_context"

_SNAPSHOT_ENV = "PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH"

ANSWER_TEMPLATE = (
    "As of {as_of_display}, {asset} spot is {quote_currency} {spot}. "
    "For options expiring {resolved_expiry_display}, the middle 50% of priced "
    "terminal outcomes runs from {low} to {high} ({low_percent}% to "
    "{high_percent}% versus spot), with a median of {median}. ATM implied "
    "volatility is {iv}% annualized; this measures priced uncertainty, not "
    "direction. {uncertainty_description} This is "
    "risk-neutral options pricing, not a forecast or trade recommendation."
)
EXPLICIT_BEFORE_PREFIX = (
    "The requested target date, {effective_target_date_display}, is represented "
    "by the nearest supported options expiry, {resolved_expiry_display}, "
    "{absolute_offset} days before the target. "
)
EXPLICIT_AFTER_PREFIX = (
    "The requested target date, {effective_target_date_display}, is represented "
    "by the nearest supported options expiry, {resolved_expiry_display}, "
    "{absolute_offset} days after the target. "
)
DEFAULT_BEFORE_PREFIX = (
    "The default 30-day target is represented by the nearest supported options "
    "expiry, {resolved_expiry_display}, {absolute_offset} days before the target. "
)
DEFAULT_AFTER_PREFIX = (
    "The default 30-day target is represented by the nearest supported options "
    "expiry, {resolved_expiry_display}, {absolute_offset} days after the target. "
)


class OptionsMarketReadError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}

    @property
    def status_line(self) -> str:
        return {
            400: "400 Bad Request",
            422: "422 Unprocessable Entity",
            500: "500 Internal Server Error",
            503: "503 Service Unavailable",
        }.get(self.status, f"{self.status} Error")


@dataclass(frozen=True)
class MarketReadExpiry:
    expiry_date: date
    spot_price: float
    implied_forward_price: float
    atm_iv_annual: float
    q25: float
    median: float
    q75: float


@dataclass(frozen=True)
class MarketReadSnapshot:
    as_of: str
    as_of_date: date
    asset: str
    quote_currency: str
    snapshot_id: str
    expiries: tuple[MarketReadExpiry, ...]


SnapshotLoader = Callable[[], MarketReadSnapshot]


def error_body(exc: OptionsMarketReadError) -> dict[str, Any]:
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        }
    }


def _first_query(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=True).get(key)
    if not raw:
        return None
    return str(raw[0])


def _require_finite(value: float, field: str) -> float:
    if not math.isfinite(value) or value <= 0:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": value},
        )
    return value


def _parse_usd(value: Any, field: str) -> float:
    if value is None or value == "":
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field},
        )
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": value},
        ) from exc
    return _require_finite(parsed, field)


def format_as_of(raw: str) -> tuple[str, date]:
    text = str(raw or "").strip()
    if not text:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "as_of"},
        )
    try:
        if len(text) == 10:
            parsed = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=UTC)
        else:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            parsed = parsed.astimezone(UTC)
    except ValueError as exc:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "as_of", "as_of": text},
        ) from exc
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ"), parsed.date()


def _human_date(value: date) -> str:
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def humanize_as_of(as_of: str) -> str:
    parsed = datetime.fromisoformat(as_of.replace("Z", "+00:00")).astimezone(UTC)
    hour = parsed.hour % 12 or 12
    meridiem = "AM" if parsed.hour < 12 else "PM"
    return (
        f"{_human_date(parsed.date())} at {hour}:{parsed.minute:02d} "
        f"{meridiem} UTC"
    )


def parse_market_read_request(
    environ: dict[str, Any],
) -> tuple[MarketReadAsset, date | None, str | None]:
    asset_raw = _first_query(environ, "asset")
    target_raw = _first_query(environ, "target_date")
    try:
        spec = resolve_market_read_asset(asset_raw)
    except KeyError as exc:
        raise OptionsMarketReadError(
            422,
            "unsupported_asset",
            "V1 supports BTC only.",
            {"asset": str(exc.args[0])},
        ) from exc

    if target_raw is None:
        return spec, None, None
    date_in = target_raw.strip()
    if not date_in:
        raise OptionsMarketReadError(
            400,
            "invalid_date",
            "target_date must be an ISO date in YYYY-MM-DD format.",
            {"target_date": target_raw},
        )
    try:
        parsed = date.fromisoformat(date_in)
    except ValueError as exc:
        raise OptionsMarketReadError(
            400,
            "invalid_date",
            "target_date must be an ISO date in YYYY-MM-DD format.",
            {"target_date": date_in},
        ) from exc
    if date_in != parsed.isoformat():
        raise OptionsMarketReadError(
            400,
            "invalid_date",
            "target_date must be an ISO date in YYYY-MM-DD format.",
            {"target_date": date_in},
        )
    return spec, parsed, date_in


def default_target_date(as_of_date: date) -> date:
    return as_of_date + timedelta(days=DEFAULT_HORIZON_DAYS)


@dataclass(frozen=True)
class ResolvedExpiry:
    expiry_date: date
    effective_target_date: date
    offset_days: int
    resolution: str
    max_expiry_gap_days: int


def live_expiry_dates(expiry_dates: list[date], as_of_date: date) -> list[date]:
    return sorted(d for d in expiry_dates if d >= as_of_date)


def nearest_expiry_neighbors(
    live_dates: list[date],
    target: date,
) -> tuple[date | None, date | None]:
    before = [d for d in live_dates if d < target]
    after = [d for d in live_dates if d > target]
    return (max(before) if before else None, min(after) if after else None)


def resolve_expiry(
    target: date,
    expiry_dates: list[date],
    *,
    as_of_date: date,
    max_expiry_gap_days: int,
) -> ResolvedExpiry:
    live = live_expiry_dates(expiry_dates, as_of_date)
    nearest_before, nearest_after = nearest_expiry_neighbors(live, target)
    if target in live:
        return ResolvedExpiry(
            expiry_date=target,
            effective_target_date=target,
            offset_days=0,
            resolution=RESOLUTION_EXACT,
            max_expiry_gap_days=max_expiry_gap_days,
        )

    def _gap_error() -> OptionsMarketReadError:
        return OptionsMarketReadError(
            422,
            "expiry_not_close_enough",
            f"No supported options expiry is within {max_expiry_gap_days} days of the target date.",
            {
                "effective_target_date": target.isoformat(),
                "max_expiry_gap_days": max_expiry_gap_days,
                "nearest_before": nearest_before.isoformat() if nearest_before else None,
                "nearest_after": nearest_after.isoformat() if nearest_after else None,
            },
        )

    if not live:
        raise _gap_error()

    chosen = min(live, key=lambda d: (abs((d - target).days), -d.toordinal()))
    offset_days = (chosen - target).days
    if abs(offset_days) > max_expiry_gap_days:
        raise _gap_error()
    resolution = RESOLUTION_NEAREST_BEFORE if offset_days < 0 else RESOLUTION_NEAREST_AFTER
    return ResolvedExpiry(
        expiry_date=chosen,
        effective_target_date=target,
        offset_days=offset_days,
        resolution=resolution,
        max_expiry_gap_days=max_expiry_gap_days,
    )


def _canonical_snapshot_id(payload: dict[str, Any]) -> str:
    explicit = str(payload.get("snapshot_id") or "").strip()
    if explicit:
        return explicit
    digest_src = json.dumps(
        {
            "as_of": payload.get("as_of") or payload.get("as_of_utc"),
            "asset": payload.get("asset"),
            "quote_currency": payload.get("quote_currency"),
            "expiries": payload.get("expiries"),
        },
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(digest_src.encode("utf-8")).hexdigest()


def _parse_expiry_row(row: dict[str, Any], *, fallback_asset: str) -> MarketReadExpiry:
    row_asset = str(row.get("asset") or fallback_asset).strip().upper()
    if row_asset != fallback_asset:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": row_asset, "expected": fallback_asset},
        )
    expiry_raw = str(row.get("expiry_date") or "").strip()
    try:
        expiry = date.fromisoformat(expiry_raw)
    except ValueError as exc:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "expiry_date", "expiry_date": expiry_raw},
        ) from exc
    q25 = _parse_usd(row.get("q25_usd") if "q25_usd" in row else row.get("q25"), "q25")
    median = _parse_usd(row.get("q50_usd") if "q50_usd" in row else row.get("median"), "median")
    q75 = _parse_usd(row.get("q75_usd") if "q75_usd" in row else row.get("q75"), "q75")
    if not (q25 <= median <= q75) or (q75 - q25) <= 0:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "quartiles"},
        )
    return MarketReadExpiry(
        expiry_date=expiry,
        spot_price=_parse_usd(row.get("spot_usd") if "spot_usd" in row else row.get("spot_price"), "spot"),
        implied_forward_price=_parse_usd(
            row.get("forward_usd") if "forward_usd" in row else row.get("implied_forward_price"),
            "implied_forward",
        ),
        atm_iv_annual=_parse_usd(
            row.get("atm_iv_annual") if "atm_iv_annual" in row else row.get("atm_iv"),
            "atm_iv",
        ),
        q25=q25,
        median=median,
        q75=q75,
    )


def snapshot_from_payload(payload: dict[str, Any]) -> MarketReadSnapshot:
    as_of, as_of_date = format_as_of(str(payload.get("as_of") or payload.get("as_of_utc") or ""))
    asset = str(payload.get("asset") or "").strip().upper()
    quote = str(payload.get("quote_currency") or payload.get("currency") or "").strip().upper()
    if not asset or asset == "SOL":
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": asset or None, "expected": DEFAULT_ASSET_ID},
        )
    if not quote:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "quote_currency"},
        )
    raw_expiries = payload.get("expiries")
    if not isinstance(raw_expiries, list) or not raw_expiries:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_expiries"},
        )
    expiries = tuple(_parse_expiry_row(row, fallback_asset=asset) for row in raw_expiries)
    return MarketReadSnapshot(
        as_of=as_of,
        as_of_date=as_of_date,
        asset=asset,
        quote_currency=quote,
        snapshot_id=_canonical_snapshot_id({**payload, "as_of": as_of, "asset": asset, "quote_currency": quote}),
        expiries=expiries,
    )


def snapshot_from_export_rows(rows: list[dict[str, Any]]) -> MarketReadSnapshot:
    lognormal = [row for row in rows if str(row.get("distribution") or "") == LOGNORMAL_DISTRIBUTION]
    if not lognormal:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_lognormal_rows"},
        )
    as_ofs = {str(row.get("as_of_utc") or "").strip() for row in lognormal}
    as_ofs.discard("")
    if len(as_ofs) != 1:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "as_of_utc"},
        )
    assets = {str(row.get("asset") or "").strip().upper() for row in lognormal}
    if len(assets) != 1:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": sorted(assets)},
        )
    asset = next(iter(assets))
    return snapshot_from_payload(
        {
            "as_of": next(iter(as_ofs)),
            "asset": asset,
            "quote_currency": "USD",
            "expiries": lognormal,
        }
    )


def load_snapshot_from_json(path: Path) -> MarketReadSnapshot:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "unreadable_snapshot"},
        ) from exc
    if not isinstance(payload, dict):
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"reason": "snapshot_not_object"},
        )
    return snapshot_from_payload(payload)


def load_snapshot_from_csv(path: Path) -> MarketReadSnapshot:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "unreadable_snapshot"},
        ) from exc
    return snapshot_from_export_rows(rows)


def snapshot_from_display_payload(payload: dict[str, Any]) -> MarketReadSnapshot:
    """Map the display-boundary JSON (same object as GET /display.json) to a market read."""
    as_of_raw = str(payload.get("as_of_utc") or payload.get("as_of") or "")
    asset_block = payload.get("asset") if isinstance(payload.get("asset"), dict) else {}
    asset = str(asset_block.get("id") or "").strip().upper()
    spot = payload.get("spot_usd")
    series = payload.get("series_by_expiry")
    if not isinstance(series, list) or not series:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "display_payload_missing_series"},
        )
    try:
        quote = resolve_market_read_asset(asset).quote_currency
    except KeyError:
        quote = ""
    expiries: list[dict[str, Any]] = []
    for item in series:
        if not isinstance(item, dict):
            raise OptionsMarketReadError(
                503,
                "inconsistent_snapshot",
                "Snapshot metadata is missing or inconsistent.",
                {"field": "series_by_expiry"},
            )
        quartiles = item.get("quartiles_usd") if isinstance(item.get("quartiles_usd"), dict) else {}
        expiries.append(
            {
                "asset": str(item.get("asset") or asset),
                "expiry_date": item.get("expiry_date"),
                "spot_usd": item.get("spot_usd", spot),
                "forward_usd": item.get("forward_usd"),
                "atm_iv_annual": item.get("atm_iv_annual"),
                "q25_usd": quartiles.get("q1_usd"),
                "q50_usd": quartiles.get("median_usd"),
                "q75_usd": quartiles.get("q3_usd"),
            }
        )
    return snapshot_from_payload(
        {
            "as_of": as_of_raw,
            "asset": asset,
            "quote_currency": quote,
            "expiries": expiries,
        }
    )


def load_display_boundary_snapshot(asset_id: str = DEFAULT_ASSET_ID) -> MarketReadSnapshot:
    """Reuse the in-process TTL cache that serves GET /ppe-display-api/display.json."""
    from src.viz.embed_display_boundary import (
        DISPLAY_DEPTH_FULL,
        build_cached_live_distribution_display_payload,
    )

    environ = {"QUERY_STRING": f"asset={asset_id}&depth={DISPLAY_DEPTH_FULL}"}
    try:
        payload = build_cached_live_distribution_display_payload(environ)
    except OptionsMarketReadError:
        raise
    except Exception as exc:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "display_boundary_unavailable", "error": str(exc)},
        ) from exc
    return snapshot_from_display_payload(payload)


def load_prepared_snapshot(asset_id: str = DEFAULT_ASSET_ID) -> MarketReadSnapshot:
    explicit = (os.environ.get(_SNAPSHOT_ENV) or "").strip()
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise OptionsMarketReadError(
                503,
                "snapshot_unavailable",
                "No valid snapshot/distribution data.",
                {"reason": "snapshot_path_missing"},
            )
        if path.suffix.lower() == ".json":
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and raw.get("kind") == "distribution_display_boundary":
                return snapshot_from_display_payload(raw)
            return snapshot_from_payload(raw) if isinstance(raw, dict) else load_snapshot_from_json(path)
        return load_snapshot_from_csv(path)
    return load_display_boundary_snapshot(asset_id=asset_id)


def derived_metrics(row: MarketReadExpiry) -> dict[str, Any]:
    median_vs_spot_percent = ((row.median / row.spot_price) - 1.0) * 100.0
    width = row.q75 - row.q25
    return {
        "spot_price": row.spot_price,
        "implied_forward_price": row.implied_forward_price,
        "median_terminal_price": row.median,
        "median_vs_spot_percent": median_vs_spot_percent,
        "atm_iv_percent": row.atm_iv_annual * 100.0,
        "middle_50_range": {
            "low_price": row.q25,
            "high_price": row.q75,
            "width": width,
        },
    }


def _quantize_public(value: float, decimals: int, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": value},
        )
    parsed = float(value)
    if not math.isfinite(parsed):
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": parsed},
        )
    quantized = Decimal(str(parsed)).quantize(
        Decimal("1").scaleb(-decimals),
        rounding=ROUND_HALF_UP,
    )
    return float(quantized)


def public_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Round public JSON numbers only. Does not change PPE calculations or the answer."""
    mid = metrics["middle_50_range"]
    low = _quantize_public(float(mid["low_price"]), PUBLIC_PRICE_DECIMALS, "low_price")
    high = _quantize_public(float(mid["high_price"]), PUBLIC_PRICE_DECIMALS, "high_price")
    width = _quantize_public(high - low, PUBLIC_PRICE_DECIMALS, "width")
    return {
        "spot_price": _quantize_public(float(metrics["spot_price"]), PUBLIC_PRICE_DECIMALS, "spot_price"),
        "implied_forward_price": _quantize_public(
            float(metrics["implied_forward_price"]),
            PUBLIC_PRICE_DECIMALS,
            "implied_forward_price",
        ),
        "median_terminal_price": _quantize_public(
            float(metrics["median_terminal_price"]),
            PUBLIC_PRICE_DECIMALS,
            "median_terminal_price",
        ),
        "median_vs_spot_percent": _quantize_public(
            float(metrics["median_vs_spot_percent"]),
            PUBLIC_MEDIAN_VS_SPOT_DECIMALS,
            "median_vs_spot_percent",
        ),
        "atm_iv_percent": _quantize_public(
            float(metrics["atm_iv_percent"]),
            PUBLIC_IV_DECIMALS,
            "atm_iv_percent",
        ),
        "middle_50_range": {
            "low_price": low,
            "high_price": high,
            "width": width,
        },
    }


def _range_vs_spot_percent(metrics: dict[str, Any]) -> dict[str, float]:
    spot = float(metrics["spot_price"])
    middle = metrics["middle_50_range"]
    low = _quantize_public(
        ((float(middle["low_price"]) / spot) - 1.0) * 100.0,
        PUBLIC_CONTEXT_PERCENT_DECIMALS,
        "range_low_vs_spot_percent",
    )
    high = _quantize_public(
        ((float(middle["high_price"]) / spot) - 1.0) * 100.0,
        PUBLIC_CONTEXT_PERCENT_DECIMALS,
        "range_high_vs_spot_percent",
    )
    return {
        "low_percent": low,
        "high_percent": high,
        "width_percent": _quantize_public(
            high - low,
            PUBLIC_CONTEXT_PERCENT_DECIMALS,
            "range_width_vs_spot_percent",
        ),
    }


def _adjacent_expiry_rows(
    snapshot: MarketReadSnapshot,
    selected: MarketReadExpiry,
) -> tuple[MarketReadExpiry | None, MarketReadExpiry | None]:
    live = sorted(
        (row for row in snapshot.expiries if row.expiry_date >= snapshot.as_of_date),
        key=lambda row: row.expiry_date,
    )
    before = [row for row in live if row.expiry_date < selected.expiry_date]
    after = [row for row in live if row.expiry_date > selected.expiry_date]
    return (before[-1] if before else None, after[0] if after else None)


def _neighbor_context(
    target_iv_percent: float,
    neighbor: MarketReadExpiry | None,
) -> dict[str, Any] | None:
    if neighbor is None:
        return None
    neighbor_iv = _quantize_public(
        neighbor.atm_iv_annual * 100.0,
        PUBLIC_IV_DECIMALS,
        "neighbor_atm_iv_percent",
    )
    difference = _quantize_public(
        target_iv_percent - neighbor_iv,
        PUBLIC_IV_DECIMALS,
        "target_minus_neighbor_vol_points",
    )
    if difference >= TERM_STRUCTURE_MATERIALITY_VOL_POINTS:
        relation = RELATION_TARGET_HIGHER
    elif difference <= -TERM_STRUCTURE_MATERIALITY_VOL_POINTS:
        relation = RELATION_TARGET_LOWER
    else:
        relation = RELATION_SIMILAR
    return {
        "expiry": neighbor.expiry_date.isoformat(),
        "atm_iv_percent": neighbor_iv,
        "target_minus_neighbor_vol_points": difference,
        "relation": relation,
    }


def _uncertainty_rating(
    previous: dict[str, Any] | None,
    following: dict[str, Any] | None,
) -> tuple[str, str]:
    previous_relation = previous["relation"] if previous is not None else None
    following_relation = following["relation"] if following is not None else None

    if previous_relation is not None and following_relation is not None:
        pair = (previous_relation, following_relation)
        if pair == (RELATION_TARGET_HIGHER, RELATION_TARGET_HIGHER):
            return (
                UNCERTAINTY_HIGHER_THAN_NEIGHBORS,
                "This expiry prices noticeably more movement than both neighboring expiries.",
            )
        if pair == (RELATION_TARGET_LOWER, RELATION_TARGET_LOWER):
            return (
                UNCERTAINTY_LOWER_THAN_NEIGHBORS,
                "This expiry prices noticeably less movement than both neighboring expiries.",
            )
        if pair == (RELATION_TARGET_HIGHER, RELATION_TARGET_LOWER):
            return (
                UNCERTAINTY_RISING,
                "Implied volatility rises across the previous, selected, and next expiries.",
            )
        if pair == (RELATION_TARGET_LOWER, RELATION_TARGET_HIGHER):
            return (
                UNCERTAINTY_FALLING,
                "Implied volatility falls across the previous, selected, and next expiries.",
            )
        if pair == (RELATION_SIMILAR, RELATION_SIMILAR):
            return (
                UNCERTAINTY_SIMILAR,
                "This expiry prices about the same movement as both neighboring expiries.",
            )
        return (
            UNCERTAINTY_MIXED,
            "Nearby expiries do not show a clear volatility pattern around this expiry.",
        )

    available_relation = previous_relation or following_relation
    if available_relation == RELATION_TARGET_HIGHER:
        return (
            UNCERTAINTY_HIGHER_THAN_AVAILABLE,
            "This expiry prices noticeably more movement than the one available neighboring expiry.",
        )
    if available_relation == RELATION_TARGET_LOWER:
        return (
            UNCERTAINTY_LOWER_THAN_AVAILABLE,
            "This expiry prices noticeably less movement than the one available neighboring expiry.",
        )
    if available_relation == RELATION_SIMILAR:
        return (
            UNCERTAINTY_SIMILAR_TO_AVAILABLE,
            "This expiry prices about the same movement as the one available neighboring expiry.",
        )
    return (
        UNCERTAINTY_UNAVAILABLE,
        "There is not enough adjacent-expiry data to compare this expiry with nearby dates.",
    )


def build_interpretation(
    snapshot: MarketReadSnapshot,
    selected: MarketReadExpiry,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    target_iv = _quantize_public(
        float(metrics["atm_iv_percent"]),
        PUBLIC_IV_DECIMALS,
        "target_atm_iv_percent",
    )
    previous_row, following_row = _adjacent_expiry_rows(snapshot, selected)
    previous = _neighbor_context(target_iv, previous_row)
    following = _neighbor_context(target_iv, following_row)
    rating, description = _uncertainty_rating(previous, following)
    return {
        "days_to_expiry": (selected.expiry_date - snapshot.as_of_date).days,
        "range_vs_spot_percent": _range_vs_spot_percent(metrics),
        "uncertainty_context": {
            "rating": rating,
            "description": description,
            "basis": "atm_iv_vs_adjacent_live_expiries",
            "materiality_threshold_vol_points": TERM_STRUCTURE_MATERIALITY_VOL_POINTS,
            "target_expiry": {
                "expiry": selected.expiry_date.isoformat(),
                "atm_iv_percent": target_iv,
            },
            "previous_expiry": previous,
            "next_expiry": following,
        },
    }


def serialize_market_read_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True, allow_nan=False).encode("utf-8")


def _whole_units(value: float) -> str:
    return f"{int(round(value)):,}"


def _price_with_currency(currency: str, value: float) -> str:
    return f"{currency} {_whole_units(value)}"


def render_answer(
    *,
    as_of: str,
    asset: str,
    quote_currency: str,
    resolved_expiry: str,
    metrics: dict[str, Any],
    interpretation: dict[str, Any],
    resolution: str = RESOLUTION_EXACT,
    requested_target_date: str | None = None,
    effective_target_date: str | None = None,
    offset_days: int = 0,
) -> str:
    mid = metrics["middle_50_range"]
    range_percent = interpretation["range_vs_spot_percent"]
    uncertainty = interpretation["uncertainty_context"]
    resolved_expiry_display = _human_date(date.fromisoformat(resolved_expiry))
    body = ANSWER_TEMPLATE.format(
        as_of_display=humanize_as_of(as_of),
        asset=asset,
        quote_currency=quote_currency,
        spot=_whole_units(float(metrics["spot_price"])),
        resolved_expiry_display=resolved_expiry_display,
        median=_price_with_currency(quote_currency, float(metrics["median_terminal_price"])),
        low=_price_with_currency(quote_currency, float(mid["low_price"])),
        high=_price_with_currency(quote_currency, float(mid["high_price"])),
        low_percent=f"{float(range_percent['low_percent']):+.1f}",
        high_percent=f"{float(range_percent['high_percent']):+.1f}",
        iv=f"{float(metrics['atm_iv_percent']):.1f}",
        uncertainty_description=uncertainty["description"],
    )
    if resolution == RESOLUTION_EXACT:
        return body
    prefix_kwargs = {
        "effective_target_date_display": (
            _human_date(date.fromisoformat(effective_target_date))
            if effective_target_date
            else ""
        ),
        "resolved_expiry_display": resolved_expiry_display,
        "absolute_offset": abs(offset_days),
    }
    if requested_target_date is None:
        prefix = (
            DEFAULT_BEFORE_PREFIX if resolution == RESOLUTION_NEAREST_BEFORE else DEFAULT_AFTER_PREFIX
        )
    else:
        prefix = (
            EXPLICIT_BEFORE_PREFIX if resolution == RESOLUTION_NEAREST_BEFORE else EXPLICIT_AFTER_PREFIX
        )
    return prefix.format(**prefix_kwargs) + body


def build_market_read_response(
    *,
    spec: MarketReadAsset,
    requested_target_date: str | None,
    target_date: date | None,
    snapshot: MarketReadSnapshot,
) -> dict[str, Any]:
    if snapshot.asset != spec.asset_id:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": snapshot.asset, "expected": spec.asset_id},
        )
    if snapshot.quote_currency != spec.quote_currency:
        raise OptionsMarketReadError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"quote_currency": snapshot.quote_currency, "expected": spec.quote_currency},
        )
    resolved_target = target_date if target_date is not None else default_target_date(snapshot.as_of_date)
    if resolved_target < snapshot.as_of_date:
        raise OptionsMarketReadError(
            422,
            "past_target_date",
            "target_date is before the snapshot as-of date.",
            {
                "target_date": resolved_target.isoformat(),
                "as_of": snapshot.as_of,
            },
        )
    expiry_dates = [row.expiry_date for row in snapshot.expiries]
    resolved = resolve_expiry(
        resolved_target,
        expiry_dates,
        as_of_date=snapshot.as_of_date,
        max_expiry_gap_days=spec.max_expiry_gap_days,
    )
    row = next(item for item in snapshot.expiries if item.expiry_date == resolved.expiry_date)
    metrics = derived_metrics(row)
    interpretation = build_interpretation(snapshot, row, metrics)
    answer = render_answer(
        as_of=snapshot.as_of,
        asset=spec.asset_id,
        quote_currency=spec.quote_currency,
        resolved_expiry=resolved.expiry_date.isoformat(),
        metrics=metrics,
        interpretation=interpretation,
        resolution=resolved.resolution,
        requested_target_date=requested_target_date,
        effective_target_date=resolved.effective_target_date.isoformat(),
        offset_days=resolved.offset_days,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "asset": spec.asset_id,
        "quote_currency": spec.quote_currency,
        "as_of": snapshot.as_of,
        "as_of_display": humanize_as_of(snapshot.as_of),
        "snapshot_id": snapshot.snapshot_id,
        "requested_target_date": requested_target_date,
        "effective_target_date": resolved.effective_target_date.isoformat(),
        "default_horizon_days": DEFAULT_HORIZON_DAYS,
        "resolved_expiry": resolved.expiry_date.isoformat(),
        "expiry_offset_days": resolved.offset_days,
        "expiry_resolution": resolved.resolution,
        "max_expiry_gap_days": resolved.max_expiry_gap_days,
        "distribution_method": DISTRIBUTION_METHOD,
        "data_status": DATA_STATUS_CACHED,
        "metrics": public_metrics(metrics),
        "interpretation": interpretation,
        "answer": answer,
    }


def handle_options_market_read_request(
    environ: dict[str, Any],
    *,
    snapshot_loader: SnapshotLoader | None = None,
) -> tuple[str, bytes]:
    try:
        spec, target_date, requested = parse_market_read_request(environ)
        snapshot = (
            snapshot_loader()
            if snapshot_loader is not None
            else load_prepared_snapshot(asset_id=spec.asset_id)
        )
        payload = build_market_read_response(
            spec=spec,
            requested_target_date=requested,
            target_date=target_date,
            snapshot=snapshot,
        )
        body = serialize_market_read_json(payload)
        return "200 OK", body
    except OptionsMarketReadError as exc:
        body = serialize_market_read_json(error_body(exc))
        return exc.status_line, body
    except Exception as exc:  # noqa: BLE001 — contract requires 500 for unexpected errors
        unexpected = OptionsMarketReadError(
            500,
            "internal_error",
            "Unexpected internal error.",
            {"error": str(exc)},
        )
        body = serialize_market_read_json(error_body(unexpected))
        return unexpected.status_line, body


def handle_options_market_read_wsgi_path(
    path: str,
    environ: dict[str, Any],
    *,
    snapshot_loader: SnapshotLoader | None = None,
) -> tuple[str, bytes] | None:
    if path != OPTIONS_MARKET_READ_HTTP_PATH:
        return None
    return handle_options_market_read_request(environ, snapshot_loader=snapshot_loader)
