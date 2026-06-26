"""Equity venue distribution CSV rows (PPE_CORE)."""

from __future__ import annotations

from typing import Any, Callable

from src.data.assets_registry import default_asset_id
from src.data.fetch_equity_options import (
    assess_equity_chain_trust,
    format_equity_trust_suffix,
)
from src.engine.implied_distribution import (
    build_distribution_chart_data,
    density_distribution_stats,
    lognormal_distribution_stats,
    market_implied_density_breeden_litzenberger,
)

CSV_COLUMNS = [
    "as_of_utc",
    "asset",
    "expiry_date",
    "T_years",
    "distribution",
    "mean_usd",
    "q05_usd",
    "q10_usd",
    "q25_usd",
    "q50_usd",
    "q75_usd",
    "q90_usd",
    "q95_usd",
    "iqr_usd",
    "bl_ln_mean_gap_usd",
    "forward_usd",
    "atm_iv_annual",
    "spot_usd",
    "call_marks_count",
    "bl_status",
]


def _fmt_usd(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.2f}"


def _empty_bl_stats() -> dict[str, float]:
    return {
        "mean_usd": 0.0,
        "q05_usd": 0.0,
        "q10_usd": 0.0,
        "q25_usd": 0.0,
        "q50_usd": 0.0,
        "q75_usd": 0.0,
        "q90_usd": 0.0,
        "q95_usd": 0.0,
    }


def _iqr_usd(stats: dict[str, float]) -> float | None:
    q25 = stats.get("q25_usd")
    q75 = stats.get("q75_usd")
    if q25 is None or q75 is None:
        return None
    width = float(q75) - float(q25)
    if width <= 0:
        return None
    return width


def _stats_row(
    *,
    as_of_utc: str,
    asset: str,
    expiry_date: str,
    T_years: float,
    distribution: str,
    stats: dict[str, float],
    forward_usd: float,
    atm_iv_annual: float,
    spot_usd: float,
    call_marks_count: str,
    bl_status: str,
    bl_ln_mean_gap_usd: float | None = None,
) -> dict[str, str]:
    iqr = _iqr_usd(stats)
    return {
        "as_of_utc": as_of_utc,
        "asset": asset,
        "expiry_date": expiry_date,
        "T_years": f"{float(T_years):.6f}",
        "distribution": distribution,
        "mean_usd": _fmt_usd(stats.get("mean_usd")),
        "q05_usd": _fmt_usd(stats.get("q05_usd")),
        "q10_usd": _fmt_usd(stats.get("q10_usd")),
        "q25_usd": _fmt_usd(stats.get("q25_usd")),
        "q50_usd": _fmt_usd(stats.get("q50_usd")),
        "q75_usd": _fmt_usd(stats.get("q75_usd")),
        "q90_usd": _fmt_usd(stats.get("q90_usd")),
        "q95_usd": _fmt_usd(stats.get("q95_usd")),
        "iqr_usd": _fmt_usd(iqr),
        "bl_ln_mean_gap_usd": _fmt_usd(bl_ln_mean_gap_usd),
        "forward_usd": _fmt_usd(forward_usd),
        "atm_iv_annual": f"{float(atm_iv_annual):.6f}",
        "spot_usd": _fmt_usd(spot_usd),
        "call_marks_count": call_marks_count,
        "bl_status": bl_status,
    }


def _equity_chart_bounds(forward: float) -> tuple[float, float]:
    lo = max(1.0, forward * 0.35)
    hi = forward * 2.5
    return lo, hi


def build_equity_distribution_export_rows(
    *,
    as_of_utc: str,
    spot_usd: float,
    expiries: list[dict[str, Any]],
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None],
    marks_full_fn: Callable[[int], dict[str, Any]],
    now_ms: float,
    asset_id: str | None = None,
) -> list[dict[str, str]]:
    """Lognormal + BL rows for equity; marks are USD/share (no forward scaling)."""
    asset = (asset_id or default_asset_id()).strip().upper()
    rows: list[dict[str, str]] = []
    for exp in expiries:
        expiry_date = str(exp.get("expiry_date_str") or "")
        expiry_ts = int(exp.get("expiry_ts") or 0)
        if not expiry_date or expiry_ts <= 0:
            continue

        fwd_iv = forward_iv_fn(expiry_ts, float(spot_usd)) or {}
        forward = float(fwd_iv.get("forward") or spot_usd)
        vol = float(fwd_iv.get("atm_iv") or 0.35)
        if vol <= 0:
            vol = 0.35
        T_years = max(0.02, (expiry_ts - now_ms) / 1000 / (365.25 * 24 * 3600))

        price_min, price_max = _equity_chart_bounds(forward)
        dist = build_distribution_chart_data(
            forward=forward,
            vol_annual=vol,
            T_years=T_years,
            price_min=price_min,
            price_max=price_max,
            num_points=100,
        )
        prices = dist["prices"]
        ln_stats = lognormal_distribution_stats(forward, vol, T_years)
        rows.append(
            _stats_row(
                as_of_utc=as_of_utc,
                asset=asset,
                expiry_date=expiry_date,
                T_years=T_years,
                distribution="lognormal_reference",
                stats=ln_stats,
                forward_usd=forward,
                atm_iv_annual=vol,
                spot_usd=spot_usd,
                call_marks_count="",
                bl_status=format_equity_trust_suffix({"trust_flags": ["dividend_caveat_unmodeled"]}),
            )
        )

        marks = marks_full_fn(expiry_ts) or {}
        call_marks = marks.get("calls") or []
        trust = assess_equity_chain_trust(call_marks)
        trust_suffix = format_equity_trust_suffix(trust)

        if len(call_marks) < 3:
            rows.append(
                _stats_row(
                    as_of_utc=as_of_utc,
                    asset=asset,
                    expiry_date=expiry_date,
                    T_years=T_years,
                    distribution="market_implied_bl",
                    stats=_empty_bl_stats(),
                    forward_usd=forward,
                    atm_iv_annual=vol,
                    spot_usd=spot_usd,
                    call_marks_count=str(len(call_marks)),
                    bl_status=f"skipped:insufficient_marks|{trust_suffix}",
                )
            )
            continue

        strikes = [float(m["strike"]) for m in call_marks]
        call_usd = [float(m.get("mark_btc") or 0.0) for m in call_marks]
        market_pdf = market_implied_density_breeden_litzenberger(strikes, call_usd, prices)
        if not market_pdf or max(market_pdf) <= 1e-20:
            rows.append(
                _stats_row(
                    as_of_utc=as_of_utc,
                    asset=asset,
                    expiry_date=expiry_date,
                    T_years=T_years,
                    distribution="market_implied_bl",
                    stats=_empty_bl_stats(),
                    forward_usd=forward,
                    atm_iv_annual=vol,
                    spot_usd=spot_usd,
                    call_marks_count=str(len(call_marks)),
                    bl_status=f"skipped:degenerate_density|{trust_suffix}",
                )
            )
            continue

        bl_stats = density_distribution_stats(prices, market_pdf)
        if not trust.get("trust_ok"):
            bl_status = f"computed_caution|{trust_suffix}"
        else:
            bl_status = f"computed|{trust_suffix}"
        rows.append(
            _stats_row(
                as_of_utc=as_of_utc,
                asset=asset,
                expiry_date=expiry_date,
                T_years=T_years,
                distribution="market_implied_bl",
                stats=bl_stats,
                forward_usd=forward,
                atm_iv_annual=vol,
                spot_usd=spot_usd,
                call_marks_count=str(len(call_marks)),
                bl_status=bl_status,
                bl_ln_mean_gap_usd=float(bl_stats["mean_usd"]) - float(ln_stats["mean_usd"]),
            )
        )
    return rows
