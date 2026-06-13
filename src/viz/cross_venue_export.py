"""Cross-venue probability panel CSV — Polymarket vs options-implied P(S > K)."""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime
from typing import Any, Callable

from src.data.fetch_deribit import fetch_deribit_spreads_around_predictions
from src.viz.prediction_spread_probs import enrich_prediction_spreads_pointwise

CSV_COLUMNS = [
    "as_of_utc",
    "question",
    "strike_usd",
    "resolution_date",
    "matched_expiry_date",
    "horizon_days",
    "expiry_alignment",
    "polymarket_yes_pct",
    "options_ln_p_above_pct",
    "options_bl_p_above_pct",
    "gap_bl_minus_pm_pct",
    "gap_ln_minus_pm_pct",
    "spread_cost_usd",
    "spread_proxy_prob_pct",
    "spot_usd",
    "forward_usd",
    "atm_iv_annual",
    "call_marks_count",
    "match_status",
]


def _fmt_usd(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.2f}"


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").replace(tzinfo=UTC)
    except ValueError:
        return None


def expiry_alignment_label(*, matched_expiry_date: str, resolution_date: str) -> str:
    exp = _parse_date(matched_expiry_date)
    res = _parse_date(resolution_date)
    if exp is None or res is None:
        return ""
    if exp.date() == res.date():
        return "same_day"
    if exp.date() < res.date():
        return "before_resolution"
    return "after_resolution"


def horizon_days_label(*, as_of_utc: str, resolution_date: str) -> str:
    as_of = _parse_date(as_of_utc[:10] if as_of_utc else "")
    res = _parse_date(resolution_date)
    if as_of is None or res is None:
        return ""
    days = (res.date() - as_of.date()).days
    return str(max(0, days))


def match_status_for_spread(spread: dict[str, Any]) -> str:
    if spread.get("options_chain_p_above_pct") is not None:
        return "ok"
    if spread.get("lognormal_p_above_pct") is not None:
        return "ok_ln_only"
    return "insufficient_data"


def gap_pct(options_pct: float | None, polymarket_pct: float | None) -> float | None:
    if options_pct is None or polymarket_pct is None:
        return None
    return float(options_pct) - float(polymarket_pct)


def _expiry_date_str(spread: dict[str, Any]) -> str:
    expiry = spread.get("expiry_date")
    if hasattr(expiry, "strftime"):
        return expiry.strftime("%Y-%m-%d")
    return str(expiry or "")[:10]


def build_cross_venue_export_rows(
    *,
    as_of_utc: str,
    spot_usd: float,
    enriched_spreads: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """One row per enriched prediction-aligned spread."""
    rows: list[dict[str, str]] = []
    for spread in enriched_spreads:
        resolution_date = str(spread.get("resolution_date") or "")[:10]
        matched_expiry_date = _expiry_date_str(spread)
        pm_pct = spread.get("polymarket_yes_pct")
        ln_pct = spread.get("lognormal_p_above_pct")
        bl_pct = spread.get("options_chain_p_above_pct")
        rows.append(
            {
                "as_of_utc": as_of_utc,
                "question": str(spread.get("question") or ""),
                "strike_usd": _fmt_usd(spread.get("target")),
                "resolution_date": resolution_date,
                "matched_expiry_date": matched_expiry_date,
                "horizon_days": horizon_days_label(
                    as_of_utc=as_of_utc,
                    resolution_date=resolution_date,
                ),
                "expiry_alignment": expiry_alignment_label(
                    matched_expiry_date=matched_expiry_date,
                    resolution_date=resolution_date,
                ),
                "polymarket_yes_pct": _fmt_pct(pm_pct),
                "options_ln_p_above_pct": _fmt_pct(ln_pct),
                "options_bl_p_above_pct": _fmt_pct(bl_pct),
                "gap_bl_minus_pm_pct": _fmt_pct(gap_pct(bl_pct, pm_pct)),
                "gap_ln_minus_pm_pct": _fmt_pct(gap_pct(ln_pct, pm_pct)),
                "spread_cost_usd": _fmt_usd(spread.get("cost_usd")),
                "spread_proxy_prob_pct": _fmt_pct(spread.get("approx_implied_prob_pct")),
                "spot_usd": _fmt_usd(spot_usd),
                "forward_usd": _fmt_usd(spread.get("forward_usd")),
                "atm_iv_annual": (
                    f"{float(spread['atm_iv_annual']):.6f}"
                    if spread.get("atm_iv_annual") is not None
                    else ""
                ),
                "call_marks_count": str(spread.get("call_marks_count") or ""),
                "match_status": match_status_for_spread(spread),
            }
        )
    return rows


def build_cross_venue_panel_rows(
    *,
    as_of_utc: str,
    spot_usd: float,
    btc_questions: list[dict[str, Any]],
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None],
    marks_full_fn: Callable[[int], dict[str, Any]],
    instruments_fn: Callable[[], list[dict[str, Any]]] | None = None,
    option_book_marks_fn: Callable[[], dict[str, float]] | None = None,
    max_questions: int = 8,
) -> list[dict[str, str]]:
    """Fetch prediction-aligned spreads, enrich with P(>K), serialize export rows."""
    if not btc_questions or spot_usd <= 0:
        return []

    instruments = instruments_fn() if instruments_fn else None
    option_book_marks = option_book_marks_fn() if option_book_marks_fn else None
    eligible = [q for q in btc_questions if (q.get("strike") or 0) >= 10_000]
    eligible.sort(key=lambda q: q.get("strike") or 0, reverse=True)
    spreads = fetch_deribit_spreads_around_predictions(
        btc_questions=eligible or btc_questions,
        current_spot=float(spot_usd),
        max_questions=max_questions,
        instruments=instruments,
        option_book_marks=option_book_marks,
    )
    if not spreads:
        return []

    enriched = enrich_prediction_spreads_pointwise(
        spreads,
        current_spot=float(spot_usd),
        forward_iv_fn=forward_iv_fn,
        marks_full_fn=marks_full_fn,
    )
    for spread in enriched:
        exp_ts = spread.get("expiry_ts")
        if exp_ts is None:
            continue
        try:
            marks = marks_full_fn(int(exp_ts)) or {}
        except (TypeError, ValueError):
            marks = {}
        spread["call_marks_count"] = len(marks.get("calls") or [])
        fwd_iv = forward_iv_fn(int(exp_ts), float(spot_usd)) or {}
        spread["forward_usd"] = fwd_iv.get("forward") or spot_usd
        spread["atm_iv_annual"] = fwd_iv.get("atm_iv")

    return build_cross_venue_export_rows(
        as_of_utc=as_of_utc,
        spot_usd=float(spot_usd),
        enriched_spreads=enriched,
    )


def serialize_cross_venue_export_csv(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})
    return buf.getvalue()
