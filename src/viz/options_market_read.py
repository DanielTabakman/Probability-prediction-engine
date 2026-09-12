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
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs

from src.viz.options_market_read_assets import (
    DEFAULT_ASSET_ID,
    MarketReadAsset,
    resolve_market_read_asset,
)

OPTIONS_MARKET_READ_HTTP_PATH = "/v1/options-market-read"
SCHEMA_VERSION = "1.0"
RULESET_VERSION = "options-market-read.v1"
DISTRIBUTION_METHOD = "lognormal"
LOGNORMAL_DISTRIBUTION = "lognormal_reference"
DATA_STATUS_CACHED = "cached"
DEFAULT_HORIZON_DAYS = 30

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SNAPSHOT_ROOT = _REPO_ROOT / "artifacts" / "distribution_snapshots"
_SNAPSHOT_ENV = "PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH"
_SNAPSHOT_ROOT_ENV = "PPE_OPTIONS_MARKET_READ_SNAPSHOT_ROOT"

ANSWER_TEMPLATE = (
    "As of {as_of}, {asset} spot is {quote_currency} {spot}. "
    "For options expiring {resolved_expiry}, the options-implied terminal "
    "distribution is centred near {median}, which is {signed_percent}% versus "
    "spot. The middle 50% of priced outcomes runs from {low} to {high}, and "
    "ATM implied volatility is {iv}%. This is risk-neutral options pricing, "
    "not a forecast."
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


def resolve_expiry(target: date, expiry_dates: list[date]) -> date:
    on_or_after = sorted(d for d in expiry_dates if d >= target)
    if not on_or_after:
        raise OptionsMarketReadError(
            422,
            "expiry_unavailable",
            "No options expiry on or after the requested date.",
            {"requested_target_date": target.isoformat()},
        )
    return on_or_after[0]


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


def _list_distribution_csvs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    files: list[Path] = []
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir():
            continue
        files.extend(sorted(day_dir.glob("ppe_btc_distribution_stats_*.csv")))
    return files


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


def load_prepared_snapshot() -> MarketReadSnapshot:
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
            return load_snapshot_from_json(path)
        return load_snapshot_from_csv(path)
    root = Path(os.environ.get(_SNAPSHOT_ROOT_ENV) or _DEFAULT_SNAPSHOT_ROOT)
    files = _list_distribution_csvs(root)
    if not files:
        raise OptionsMarketReadError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_prepared_snapshot"},
        )
    return load_snapshot_from_csv(files[-1])


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
) -> str:
    mid = metrics["middle_50_range"]
    return ANSWER_TEMPLATE.format(
        as_of=as_of,
        asset=asset,
        quote_currency=quote_currency,
        spot=_whole_units(float(metrics["spot_price"])),
        resolved_expiry=resolved_expiry,
        median=_price_with_currency(quote_currency, float(metrics["median_terminal_price"])),
        signed_percent=f"{float(metrics['median_vs_spot_percent']):+.1f}",
        low=_price_with_currency(quote_currency, float(mid["low_price"])),
        high=_price_with_currency(quote_currency, float(mid["high_price"])),
        iv=f"{float(metrics['atm_iv_percent']):.1f}",
    )


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
    resolved = resolve_expiry(resolved_target, expiry_dates)
    row = next(item for item in snapshot.expiries if item.expiry_date == resolved)
    metrics = derived_metrics(row)
    answer = render_answer(
        as_of=snapshot.as_of,
        asset=spec.asset_id,
        quote_currency=spec.quote_currency,
        resolved_expiry=resolved.isoformat(),
        metrics=metrics,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "asset": spec.asset_id,
        "quote_currency": spec.quote_currency,
        "as_of": snapshot.as_of,
        "snapshot_id": snapshot.snapshot_id,
        "requested_target_date": requested_target_date,
        "default_horizon_days": DEFAULT_HORIZON_DAYS,
        "resolved_expiry": resolved.isoformat(),
        "distribution_method": DISTRIBUTION_METHOD,
        "data_status": DATA_STATUS_CACHED,
        "metrics": metrics,
        "answer": answer,
    }


def handle_options_market_read_request(
    environ: dict[str, Any],
    *,
    snapshot_loader: SnapshotLoader | None = None,
) -> tuple[str, bytes]:
    try:
        spec, target_date, requested = parse_market_read_request(environ)
        snapshot = (snapshot_loader or load_prepared_snapshot)()
        payload = build_market_read_response(
            spec=spec,
            requested_target_date=requested,
            target_date=target_date,
            snapshot=snapshot,
        )
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return "200 OK", body
    except OptionsMarketReadError as exc:
        body = json.dumps(error_body(exc), separators=(",", ":"), sort_keys=True).encode("utf-8")
        return exc.status_line, body
    except Exception as exc:  # noqa: BLE001 — contract requires 500 for unexpected errors
        unexpected = OptionsMarketReadError(
            500,
            "internal_error",
            "Unexpected internal error.",
            {"error": str(exc)},
        )
        body = json.dumps(error_body(unexpected), separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
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
