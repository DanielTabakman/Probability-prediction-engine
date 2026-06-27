"""Options Horizon chart payload — historical + forward + implied sections."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.data.fetch_deribit import (
    fetch_deribit_btc_index,
    fetch_deribit_btc_option_expiries,
    fetch_deribit_btc_futures_forward_curve,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_forward_and_iv_for_expiry,
)
from src.data.fetch_yahoo import DEFAULT_SYMBOLS, fetch_yahoo_prices
from src.data.horizon_surface_archive import (
    archive_meta,
    default_archive_root,
    load_latest_snapshot,
    load_nearest_snapshot,
)
from src.engine.implied_distribution import build_distribution_chart_data
from src.viz.embed_display_boundary import build_chart_series_from_export_row
from src.viz.distribution_export import build_distribution_export_rows

CHART_PAYLOAD_SCHEMA_VERSION = 1
CHART_PAYLOAD_KIND = "horizon_chart"
CHART_PAYLOAD_HTTP_PATH = "/ppe-display-api/horizon/chart.json"
DEFAULT_CHART_DAYS = 90


def _yahoo_historical_series(chart_days: int = DEFAULT_CHART_DAYS) -> list[dict[str, Any]]:
    df = fetch_yahoo_prices(symbols={"bitcoin": DEFAULT_SYMBOLS["bitcoin"]}, period=f"{chart_days}d")
    if df is None or df.empty:
        return []
    out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        ts = row.get("timestamp") or row.get("date")
        if ts is None:
            continue
        try:
            dt = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else datetime.fromisoformat(str(ts))
        except (TypeError, ValueError):
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        close = row.get("close")
        if close is None:
            continue
        try:
            close_f = float(close)
        except (TypeError, ValueError):
            continue
        vol = row.get("volume")
        volume = float(vol) if vol is not None and str(vol) != "nan" else None
        out.append(
            {
                "date_utc": dt.astimezone(UTC).strftime("%Y-%m-%d"),
                "timestamp_utc": dt.astimezone(UTC).isoformat(),
                "close_usd": close_f,
                "volume": volume,
            }
        )
    return out


def _forward_curve_points() -> list[dict[str, Any]]:
    curve = fetch_deribit_btc_futures_forward_curve(max_contracts=8)
    out: list[dict[str, Any]] = []
    for row in curve:
        exp = row.get("expiry_date")
        mark = row.get("mark_price")
        if exp is None or mark is None:
            continue
        try:
            mark_f = float(mark)
        except (TypeError, ValueError):
            continue
        if hasattr(exp, "strftime"):
            date_str = exp.strftime("%Y-%m-%d")
            ts_iso = exp.astimezone(UTC).isoformat() if exp.tzinfo else exp.replace(tzinfo=UTC).isoformat()
        else:
            date_str = str(exp)[:10]
            ts_iso = date_str
        out.append(
            {
                "expiry_date": date_str,
                "expiry_utc": ts_iso,
                "mark_price_usd": mark_f,
                "instrument_name": row.get("instrument_name"),
            }
        )
    return out


def build_horizon_chart_payload(
    *,
    asset_id: str = "BTC",
    expiry_ts: int | None = None,
    as_of: str | None = None,
    chart_days: int = DEFAULT_CHART_DAYS,
    archive_root: Any | None = None,
) -> dict[str, Any]:
    """JSON chart payload for Options Horizon MSOS route."""
    aid = str(asset_id or "BTC").strip().upper()
    root = archive_root or default_archive_root()
    now = datetime.now(tz=UTC)
    as_of_utc = now.isoformat()
    now_ms = now.timestamp() * 1000

    spot = fetch_deribit_btc_index()
    if spot is None or float(spot) <= 0:
        raise RuntimeError("spot price unavailable")
    spot_f = float(spot)

    expiries = fetch_deribit_btc_option_expiries()
    selected_ts = expiry_ts
    if selected_ts is None and expiries:
        selected_ts = int(expiries[0]["expiry_ts"])

    implied_section: dict[str, Any] | None = None
    if selected_ts is not None:
        fwd_iv = fetch_deribit_forward_and_iv_for_expiry(int(selected_ts), spot_f)
        forward = float((fwd_iv or {}).get("forward") or spot_f)
        vol = float((fwd_iv or {}).get("atm_iv") or 0.6)
        if vol <= 0:
            vol = 0.6
        T_years = max(0.02, (int(selected_ts) - now_ms) / 1000 / (365.25 * 24 * 3600))
        expiry_date = ""
        for exp in expiries:
            if int(exp.get("expiry_ts") or 0) == int(selected_ts):
                expiry_date = str(exp.get("expiry_date_str") or "")
                break
        rows = build_distribution_export_rows(
            as_of_utc=as_of_utc,
            spot_usd=spot_f,
            expiries=[{"expiry_ts": selected_ts, "expiry_date_str": expiry_date}],
            forward_iv_fn=lambda ts, s: fetch_deribit_forward_and_iv_for_expiry(ts, s),
            marks_full_fn=fetch_deribit_btc_option_marks_by_expiry_full,
            now_ms=now_ms,
            asset_id=aid,
        )
        ref_row = next((r for r in rows if r.get("distribution") == "lognormal_reference"), None)
        if ref_row:
            series = build_chart_series_from_export_row(ref_row)
            if series:
                implied_section = {
                    "expiry_ts": int(selected_ts),
                    "expiry_date": expiry_date,
                    "forward_usd": forward,
                    "atm_iv_annual": vol,
                    "T_years": T_years,
                    "prices_usd": series.get("prices_usd") or [],
                    "pdf_pct": series.get("pdf_pct") or [],
                }
        if implied_section is None:
            price_min = max(1000.0, forward * 0.4)
            price_max = forward * 2.2
            chart = build_distribution_chart_data(
                forward=forward,
                vol_annual=vol,
                T_years=T_years,
                price_min=price_min,
                price_max=price_max,
            )
            implied_section = {
                "expiry_ts": int(selected_ts),
                "expiry_date": expiry_date,
                "forward_usd": forward,
                "atm_iv_annual": vol,
                "T_years": T_years,
                "prices_usd": chart["prices"],
                "pdf_pct": chart["pdf_pct"],
            }

    archived = None
    if as_of:
        archived = load_nearest_snapshot(root, as_of=as_of, asset_id=aid)
    elif archive_meta(root).get("available_days", 0) > 0:
        archived = load_latest_snapshot(root, asset_id=aid)

    return {
        "schema_version": CHART_PAYLOAD_SCHEMA_VERSION,
        "kind": CHART_PAYLOAD_KIND,
        "as_of_utc": as_of_utc,
        "asset_id": aid,
        "spot_usd": spot_f,
        "historical": {
            "series": _yahoo_historical_series(chart_days),
            "chart_days": chart_days,
            "source": "yahoo_btc_usd",
        },
        "forward": {
            "curve": _forward_curve_points(),
            "source": "deribit_futures",
        },
        "implied": implied_section,
        "archive": archive_meta(root),
        "archived_surface": archived,
        "meta": {
            "read_only": True,
            "simulation_only": True,
            "http_path": CHART_PAYLOAD_HTTP_PATH,
        },
    }
