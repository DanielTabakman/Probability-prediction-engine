"""Deterministic option expiry horizon comparison rows."""

from __future__ import annotations

from datetime import UTC, datetime
from math import ceil, sqrt
from typing import Any, Callable

TARGET_BUCKET_DAYS = (30, 60, 90, 180, 365)
SECONDS_PER_DAY = 24 * 60 * 60
STALE_QUOTE_SECONDS = 15 * 60
THIN_OPEN_INTEREST_THRESHOLD = 100


ForwardIvFn = Callable[[int, float], dict[str, Any] | None]
MarksFullFn = Callable[[int], dict[str, list[dict[str, Any]]] | None]


def _parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _expiry_ts_ms(expiry: dict[str, Any]) -> int | None:
    raw_ts = expiry.get("expiry_ts") or expiry.get("expiry_ms")
    if raw_ts is not None:
        try:
            ts = int(raw_ts)
        except (TypeError, ValueError):
            return None
        return ts if ts > 10_000_000_000 else ts * 1000

    dt = _parse_time(expiry.get("expiry_utc") or expiry.get("expiry"))
    if dt is not None:
        return int(dt.timestamp() * 1000)

    date_text = expiry.get("expiry_date_str") or expiry.get("expiry_date")
    if date_text:
        dt = _parse_time(f"{str(date_text)[:10]}T00:00:00+00:00")
        if dt is not None:
            return int(dt.timestamp() * 1000)
    return None


def _expiry_date(expiry: dict[str, Any], expiry_ts: int) -> str:
    for key in ("expiry_date_str", "expiry_date"):
        if expiry.get(key):
            return str(expiry[key])[:10]
    return datetime.fromtimestamp(expiry_ts / 1000, tz=UTC).strftime("%Y-%m-%d")


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None


def _quote_time(row: dict[str, Any], expiry: dict[str, Any]) -> datetime | None:
    for key in (
        "quote_time_utc",
        "quote_timestamp_utc",
        "timestamp_utc",
        "as_of_utc",
        "as_of",
    ):
        parsed = _parse_time(row.get(key) or expiry.get(key))
        if parsed is not None:
            return parsed
    return None


def _open_interest_total(marks: dict[str, list[dict[str, Any]]] | None) -> int | None:
    if not marks:
        return None
    total = 0
    found = False
    for side in ("calls", "puts"):
        for mark in marks.get(side) or []:
            oi = _float_or_none(mark.get("open_interest"))
            if oi is not None:
                total += int(oi)
                found = True
    return total if found else None


def _time_decay_language(days_out: int, flags: list[str]) -> str:
    if "missing_atm_iv" in flags or "missing_forward" in flags:
        return "Time-window comparison only; option quote inputs are incomplete."
    if days_out <= 45:
        return "Nearer expiry: more time-decay pressure and tighter timing."
    if days_out <= 120:
        return "Middle expiry: balances time for the view with meaningful decay."
    return "Longer expiry: more calendar room, with slower daily time decay."


def _candidate_rows(
    *,
    listed_expiries: list[dict[str, Any]],
    evaluation_time: datetime,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in listed_expiries:
        expiry_ts = _expiry_ts_ms(raw)
        if expiry_ts is None:
            continue
        seconds_out = expiry_ts / 1000 - evaluation_time.timestamp()
        if seconds_out <= 0:
            continue
        days_out = max(1, int(ceil(seconds_out / SECONDS_PER_DAY)))
        rows.append(
            {
                "raw": raw,
                "expiry_ts": expiry_ts,
                "expiry_date": _expiry_date(raw, expiry_ts),
                "days_out": days_out,
            }
        )
    return sorted(rows, key=lambda row: (row["expiry_ts"], row["expiry_date"]))


def _selected_by_bucket(candidates: list[dict[str, Any]], targets: tuple[int, ...]) -> dict[int, list[int]]:
    selected: dict[int, list[int]] = {}
    for target in targets:
        # Tie-breaks: nearest absolute day distance, then later expiry, then timestamp.
        best = min(
            candidates,
            key=lambda row: (
                abs(int(row["days_out"]) - target),
                0 if int(row["days_out"]) >= target else 1,
                int(row["expiry_ts"]),
            ),
        )
        selected.setdefault(int(best["expiry_ts"]), []).append(target)
    return selected


def build_options_horizon_comparison(
    *,
    listed_expiries: list[dict[str, Any]],
    evaluation_time_utc: datetime | str,
    spot_usd: float | None,
    forward_iv_fn: ForwardIvFn | None = None,
    marks_full_fn: MarksFullFn | None = None,
    target_bucket_days: tuple[int, ...] = TARGET_BUCKET_DAYS,
    stale_quote_seconds: int = STALE_QUOTE_SECONDS,
) -> dict[str, Any]:
    """Build stable educational rows for about-30/60/90/180/365-day expiries."""
    evaluation_time = _parse_time(evaluation_time_utc)
    if evaluation_time is None:
        raise ValueError("evaluation_time_utc must be an ISO timestamp or datetime")
    spot = _float_or_none(spot_usd)
    candidates = _candidate_rows(listed_expiries=listed_expiries, evaluation_time=evaluation_time)
    if not candidates:
        return {
            "schema_version": 1,
            "kind": "options_horizon_comparison",
            "as_of_utc": evaluation_time.isoformat(),
            "target_bucket_days": list(target_bucket_days),
            "rows": [],
            "limitations": [
                "No listed future expiries were available for the target buckets.",
                "Educational comparison only; not financial advice, not a recommendation, and not order execution.",
            ],
            "meta": {"read_only": True, "simulation_only": True},
        }

    selected = _selected_by_bucket(candidates, target_bucket_days)
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        expiry_ts = int(candidate["expiry_ts"])
        buckets = selected.get(expiry_ts)
        if not buckets:
            continue
        raw = candidate["raw"]
        quote = forward_iv_fn(expiry_ts, float(spot)) if forward_iv_fn and spot else None
        quote = quote or {}
        forward = _float_or_none(quote.get("forward") or raw.get("forward_usd") or raw.get("mark_price_usd"))
        atm_iv = _float_or_none(quote.get("atm_iv") or raw.get("atm_iv_annual") or raw.get("atm_iv"))
        quote_dt = _quote_time(quote, raw)
        marks = marks_full_fn(expiry_ts) if marks_full_fn else None
        total_oi = _open_interest_total(marks)

        data_flags: list[str] = []
        trust_flags: list[str] = []
        if quote_dt is None:
            data_flags.append("missing_quote_time")
        elif (evaluation_time - quote_dt).total_seconds() > stale_quote_seconds:
            data_flags.append("stale_quote")
        if forward is None or forward <= 0:
            data_flags.append("missing_forward")
            trust_flags.append("forward_unavailable")
        if atm_iv is None or atm_iv <= 0:
            data_flags.append("missing_atm_iv")
            trust_flags.append("iv_unavailable")
        if total_oi is None:
            data_flags.append("missing_liquidity")
        elif total_oi < THIN_OPEN_INTEREST_THRESHOLD:
            data_flags.append("thin_liquidity")
            trust_flags.append("thin_open_interest")

        t_years = max(float(candidate["days_out"]) / 365.25, 1 / 365.25)
        one_sigma = forward * atm_iv * sqrt(t_years) if forward and atm_iv and forward > 0 and atm_iv > 0 else None
        rows.append(
            {
                "expiry_ts": expiry_ts,
                "expiry_date": candidate["expiry_date"],
                "days_out": candidate["days_out"],
                "target_bucket_days": buckets,
                "target_bucket_label": " / ".join(f"{bucket}d" for bucket in buckets),
                "forward_usd": forward,
                "atm_iv_annual": atm_iv,
                "one_sigma_move_usd": one_sigma,
                "trust_flags": trust_flags,
                "data_flags": data_flags,
                "time_decay_language": _time_decay_language(int(candidate["days_out"]), data_flags),
            }
        )

    return {
        "schema_version": 1,
        "kind": "options_horizon_comparison",
        "as_of_utc": evaluation_time.isoformat(),
        "target_bucket_days": list(target_bucket_days),
        "rows": rows,
        "limitations": [
            "Rows compare listed expiry windows before expression selection.",
            "Educational comparison only; not financial advice, not a recommendation, and not order execution.",
        ],
        "meta": {"read_only": True, "simulation_only": True},
    }
