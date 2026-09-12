"""Public GET /v1/implied-range — MSOS market-implied BTC range (lognormal IQR).

Validation and snapshot loading live here. Quartiles come from prepared
distribution-export rows (or an injected fixture). This module does not
recompute option-implied densities.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs

IMPLIED_RANGE_HTTP_PATH = "/v1/implied-range"
SCHEMA_VERSION = "1.0"
SUPPORTED_ASSET = "BTC"
CURRENCY = "USD"
DISTRIBUTION_METHOD = "lognormal_iqr"
DATA_STATUS_CACHED = "cached"
LOGNORMAL_DISTRIBUTION = "lognormal_reference"
PERCENTILE_LOW = 25
PERCENTILE_HIGH = 75

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SNAPSHOT_ROOT = _REPO_ROOT / "artifacts" / "distribution_snapshots"
_SNAPSHOT_ENV = "PPE_IMPLIED_RANGE_SNAPSHOT_PATH"
_SNAPSHOT_ROOT_ENV = "PPE_IMPLIED_RANGE_SNAPSHOT_ROOT"


class ImpliedRangeError(Exception):
    """Mapped HTTP error for the implied-range contract."""

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
class ImpliedRangeSnapshot:
    as_of: str
    as_of_date: date
    asset: str
    expiries: tuple[dict[str, Any], ...]


SnapshotLoader = Callable[[], ImpliedRangeSnapshot]


def error_body(exc: ImpliedRangeError) -> dict[str, Any]:
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


def parse_implied_range_request(environ: dict[str, Any]) -> tuple[str, date, str]:
    """Return (BTC, target_date, raw_target_date). Raises ImpliedRangeError."""
    asset_raw = _first_query(environ, "asset")
    target_raw = _first_query(environ, "target_date")
    missing: list[str] = []
    if asset_raw is None or not asset_raw.strip():
        missing.append("asset")
    if target_raw is None or not target_raw.strip():
        missing.append("target_date")
    if missing:
        raise ImpliedRangeError(
            400,
            "missing_parameter",
            "Missing required query parameter.",
            {"missing": missing},
        )

    asset_in = asset_raw.strip()
    asset = asset_in.upper()
    if asset != SUPPORTED_ASSET:
        raise ImpliedRangeError(
            422,
            "unsupported_asset",
            "V1 supports BTC only.",
            {"asset": asset_in},
        )

    date_in = target_raw.strip()
    try:
        parsed = date.fromisoformat(date_in)
    except ValueError as exc:
        raise ImpliedRangeError(
            400,
            "invalid_date",
            "target_date must be an ISO date in YYYY-MM-DD format.",
            {"target_date": date_in},
        ) from exc
    if date_in != parsed.isoformat():
        raise ImpliedRangeError(
            400,
            "invalid_date",
            "target_date must be an ISO date in YYYY-MM-DD format.",
            {"target_date": date_in},
        )
    return asset, parsed, date_in


def format_as_of(raw: str) -> tuple[str, date]:
    """Normalize snapshot as_of to ...Z when UTC. Never invent a clock time."""
    text = str(raw or "").strip()
    if not text:
        raise ImpliedRangeError(
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
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "as_of", "as_of": text},
        ) from exc
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ"), parsed.date()


def _parse_usd(value: Any, field: str) -> float:
    if value is None or value == "":
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field},
        )
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": value},
        ) from exc
    if parsed <= 0 or parsed != parsed:  # NaN
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": field, "value": value},
        )
    return parsed


def resolve_expiry(target: date, expiry_dates: list[date]) -> date:
    on_or_after = sorted(d for d in expiry_dates if d >= target)
    if not on_or_after:
        raise ImpliedRangeError(
            422,
            "expiry_unavailable",
            "No options expiry on or after the requested date.",
            {"requested_target_date": target.isoformat()},
        )
    return on_or_after[0]


def snapshot_from_payload(payload: dict[str, Any]) -> ImpliedRangeSnapshot:
    as_of, as_of_date = format_as_of(str(payload.get("as_of") or payload.get("as_of_utc") or ""))
    asset = str(payload.get("asset") or "").strip().upper()
    if asset == "SOL" or (asset and asset != SUPPORTED_ASSET):
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": asset, "expected": SUPPORTED_ASSET},
        )
    if not asset:
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "asset"},
        )
    raw_expiries = payload.get("expiries")
    if not isinstance(raw_expiries, list) or not raw_expiries:
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_expiries"},
        )
    cleaned: list[dict[str, Any]] = []
    for row in raw_expiries:
        if not isinstance(row, dict):
            raise ImpliedRangeError(
                503,
                "inconsistent_snapshot",
                "Snapshot metadata is missing or inconsistent.",
                {"field": "expiries"},
            )
        row_asset = str(row.get("asset") or asset).strip().upper()
        if row_asset != SUPPORTED_ASSET:
            raise ImpliedRangeError(
                503,
                "inconsistent_snapshot",
                "Snapshot metadata is missing or inconsistent.",
                {"asset": row_asset, "expected": SUPPORTED_ASSET},
            )
        expiry_raw = str(row.get("expiry_date") or "").strip()
        try:
            expiry = date.fromisoformat(expiry_raw)
        except ValueError as exc:
            raise ImpliedRangeError(
                503,
                "inconsistent_snapshot",
                "Snapshot metadata is missing or inconsistent.",
                {"field": "expiry_date", "expiry_date": expiry_raw},
            ) from exc
        cleaned.append(
            {
                "expiry_date": expiry.isoformat(),
                "q25_usd": _parse_usd(row.get("q25_usd"), "q25_usd"),
                "q50_usd": _parse_usd(row.get("q50_usd"), "q50_usd"),
                "q75_usd": _parse_usd(row.get("q75_usd"), "q75_usd"),
            }
        )
    return ImpliedRangeSnapshot(
        as_of=as_of,
        as_of_date=as_of_date,
        asset=SUPPORTED_ASSET,
        expiries=tuple(cleaned),
    )


def snapshot_from_export_rows(rows: list[dict[str, Any]]) -> ImpliedRangeSnapshot:
    lognormal = [
        row
        for row in rows
        if str(row.get("distribution") or "") == LOGNORMAL_DISTRIBUTION
    ]
    if not lognormal:
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_lognormal_rows"},
        )
    as_of_values = {str(row.get("as_of_utc") or "").strip() for row in lognormal}
    as_of_values.discard("")
    if len(as_of_values) != 1:
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "as_of_utc"},
        )
    assets = {str(row.get("asset") or "").strip().upper() for row in lognormal}
    if assets != {SUPPORTED_ASSET}:
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": sorted(assets), "expected": SUPPORTED_ASSET},
        )
    return snapshot_from_payload(
        {
            "as_of": next(iter(as_of_values)),
            "asset": SUPPORTED_ASSET,
            "expiries": [
                {
                    "asset": SUPPORTED_ASSET,
                    "expiry_date": row.get("expiry_date"),
                    "q25_usd": row.get("q25_usd"),
                    "q50_usd": row.get("q50_usd"),
                    "q75_usd": row.get("q75_usd"),
                }
                for row in lognormal
            ],
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


def load_snapshot_from_csv(path: Path) -> ImpliedRangeSnapshot:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "unreadable_snapshot"},
        ) from exc
    return snapshot_from_export_rows(rows)


def load_snapshot_from_json(path: Path) -> ImpliedRangeSnapshot:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "unreadable_snapshot"},
        ) from exc
    if not isinstance(payload, dict):
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"reason": "snapshot_not_object"},
        )
    return snapshot_from_payload(payload)


def load_prepared_snapshot() -> ImpliedRangeSnapshot:
    explicit = (os.environ.get(_SNAPSHOT_ENV) or "").strip()
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise ImpliedRangeError(
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
        raise ImpliedRangeError(
            503,
            "snapshot_unavailable",
            "No valid snapshot/distribution data.",
            {"reason": "no_prepared_snapshot"},
        )
    return load_snapshot_from_csv(files[-1])


def build_implied_range_response(
    *,
    asset: str,
    target_date: date,
    requested_target_date: str,
    snapshot: ImpliedRangeSnapshot,
) -> dict[str, Any]:
    if snapshot.asset != asset or snapshot.asset != SUPPORTED_ASSET:
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"asset": snapshot.asset, "expected": asset},
        )
    if target_date < snapshot.as_of_date:
        raise ImpliedRangeError(
            422,
            "past_target_date",
            "target_date is before the snapshot as-of date.",
            {
                "target_date": requested_target_date,
                "as_of": snapshot.as_of,
            },
        )
    expiry_dates = [date.fromisoformat(str(row["expiry_date"])) for row in snapshot.expiries]
    resolved = resolve_expiry(target_date, expiry_dates)
    row = next(r for r in snapshot.expiries if r["expiry_date"] == resolved.isoformat())
    low = float(row["q25_usd"])
    median = float(row["q50_usd"])
    high = float(row["q75_usd"])
    width = high - low
    if width <= 0 or not (low <= median <= high):
        raise ImpliedRangeError(
            503,
            "inconsistent_snapshot",
            "Snapshot metadata is missing or inconsistent.",
            {"field": "quartiles"},
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "asset": SUPPORTED_ASSET,
        "currency": CURRENCY,
        "requested_target_date": requested_target_date,
        "resolved_expiry": resolved.isoformat(),
        "as_of": snapshot.as_of,
        "distribution_method": DISTRIBUTION_METHOD,
        "implied_range": {
            "low_usd": low,
            "median_usd": median,
            "high_usd": high,
            "width_usd": width,
            "percentile_low": PERCENTILE_LOW,
            "percentile_high": PERCENTILE_HIGH,
        },
        "data_status": DATA_STATUS_CACHED,
    }


def handle_implied_range_request(
    environ: dict[str, Any],
    *,
    snapshot_loader: SnapshotLoader | None = None,
) -> tuple[str, bytes]:
    try:
        asset, target_date, requested = parse_implied_range_request(environ)
        loader = snapshot_loader or load_prepared_snapshot
        snapshot = loader()
        payload = build_implied_range_response(
            asset=asset,
            target_date=target_date,
            requested_target_date=requested,
            snapshot=snapshot,
        )
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return "200 OK", body
    except ImpliedRangeError as exc:
        body = json.dumps(error_body(exc), separators=(",", ":"), sort_keys=True).encode("utf-8")
        return exc.status_line, body
    except Exception as exc:  # noqa: BLE001 — contract requires 500 for unexpected errors
        unexpected = ImpliedRangeError(
            500,
            "internal_error",
            "Unexpected internal error.",
            {"error": str(exc)},
        )
        body = json.dumps(error_body(unexpected), separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
        return unexpected.status_line, body


def handle_implied_range_wsgi_path(
    path: str,
    environ: dict[str, Any],
    *,
    snapshot_loader: SnapshotLoader | None = None,
) -> tuple[str, bytes] | None:
    if path != IMPLIED_RANGE_HTTP_PATH:
        return None
    return handle_implied_range_request(environ, snapshot_loader=snapshot_loader)
