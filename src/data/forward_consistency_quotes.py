"""
Live bid/ask quotes for forward consistency checks (venue adapters).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.data.assets_registry import (
    asset_venue,
    deribit_currency,
    is_asset_enabled,
    is_usd_premium_options_venue,
    list_enabled_asset_ids,
)
from src.data.fetch_deribit import (
    DEFAULT_OPTION_EXPIRIES_MAX,
    fetch_deribit_index,
    fetch_deribit_forward_and_iv_for_expiry,
    fetch_deribit_option_expiries,
    fetch_deribit_options_instruments,
    fetch_deribit_ticker,
    _deribit_public_request,
)
from src.engine.forward_consistency import (
    ForwardConsistencyCheck,
    ForwardConsistencyQualityFlag,
    ForwardConsistencyStatus,
    FutureLegQuote,
    OptionLegQuote,
    run_forward_consistency_check,
)


@dataclass(frozen=True)
class ForwardConsistencyHeatmapCell:
    asset_id: str
    expiry_date: str
    status: ForwardConsistencyStatus
    net_edge_usd: float | None
    quality_flags: list[str]
    as_of_utc: str


@dataclass
class ForwardConsistencyDashboardPayload:
    kind: str = "forward_consistency_dashboard"
    schema_version: int = 1
    summary: dict[str, int] = field(default_factory=dict)
    cells: list[ForwardConsistencyHeatmapCell] = field(default_factory=list)


def _bid_ask_from_book_row(row: dict[str, Any]) -> tuple[float | None, float | None]:
    bid = row.get("best_bid_price") or row.get("bestBidPrice") or row.get("bid_price")
    ask = row.get("best_ask_price") or row.get("bestAskPrice") or row.get("ask_price")
    try:
        bid_f = float(bid) if bid is not None else None
    except (TypeError, ValueError):
        bid_f = None
    try:
        ask_f = float(ask) if ask is not None else None
    except (TypeError, ValueError):
        ask_f = None
    return bid_f, ask_f


def _bid_ask_from_ticker(ticker: dict[str, Any] | None) -> tuple[float | None, float | None]:
    if not isinstance(ticker, dict):
        return None, None
    return _bid_ask_from_book_row(ticker)


def _ts_ms_from_row(row: dict[str, Any]) -> int | None:
    for key in ("timestamp", "creation_timestamp", "updated_timestamp"):
        raw = row.get(key)
        if raw is None:
            continue
        try:
            ts = int(raw)
            return ts if ts > 10_000_000_000 else ts * 1000
        except (TypeError, ValueError):
            continue
    return None


def resolve_expiry_ts_ms(asset_id: str, expiry_date: str) -> int | None:
    """Match display payload expiry string to Deribit option expiry timestamp."""
    needle = str(expiry_date or "").strip()[:10]
    if not needle:
        return None
    expiries = fetch_deribit_option_expiries(currency=deribit_currency(asset_id))
    for row in expiries:
        ds = str(row.get("expiry_date_str") or "")
        if ds.startswith(needle):
            try:
                return int(row["expiry_ts"])
            except (TypeError, ValueError, KeyError):
                continue
    return None


def _fetch_deribit_book_summary(currency: str, kind: str) -> list[dict[str, Any]]:
    out, err = _deribit_public_request(
        "get_book_summary_by_currency",
        {"currency": currency, "kind": kind},
    )
    if err or not isinstance(out, list):
        return []
    return [row for row in out if isinstance(row, dict)]


def fetch_deribit_option_bid_ask_for_expiry(
    expiry_ts_ms: int,
    *,
    asset_id: str,
) -> list[OptionLegQuote]:
    currency = deribit_currency(asset_id)
    instruments = fetch_deribit_options_instruments(currency, expired=False)
    for_exp = [
        i
        for i in instruments
        if int(i.get("expiration_timestamp") or 0) == int(expiry_ts_ms)
    ]
    calls = {i.get("instrument_name"): i for i in for_exp if i.get("option_type") == "call"}
    puts = {i.get("instrument_name"): i for i in for_exp if i.get("option_type") == "put"}
    book = _fetch_deribit_book_summary(currency, "option")
    book_by_name = {
        str(r.get("instrument_name") or r.get("instrumentName") or ""): r for r in book
    }

    strikes: set[float] = set()
    for inst in for_exp:
        try:
            strikes.add(float(inst.get("strike") or 0))
        except (TypeError, ValueError):
            continue

    quotes: list[OptionLegQuote] = []
    for strike in sorted(strikes):
        call_name = next(
            (n for n, i in calls.items() if n and float(i.get("strike") or 0) == strike),
            None,
        )
        put_name = next(
            (n for n, i in puts.items() if n and float(i.get("strike") or 0) == strike),
            None,
        )
        if not call_name or not put_name:
            continue
        call_row = book_by_name.get(call_name) or {}
        put_row = book_by_name.get(put_name) or {}
        call_bid, call_ask = _bid_ask_from_book_row(call_row)
        put_bid, put_ask = _bid_ask_from_book_row(put_row)
        ts = _ts_ms_from_row(call_row) or _ts_ms_from_row(put_row)
        quotes.append(
            OptionLegQuote(
                strike=strike,
                call_bid=call_bid,
                call_ask=call_ask,
                put_bid=put_bid,
                put_ask=put_ask,
                quote_ts_ms=ts,
            )
        )
    return quotes


def fetch_deribit_future_for_expiry(
    expiry_ts_ms: int,
    *,
    asset_id: str,
) -> FutureLegQuote | None:
    currency = deribit_currency(asset_id)
    instruments_raw, _ = _deribit_public_request(
        "get_instruments",
        {"currency": currency, "kind": "future", "expired": "false"},
    )
    if not isinstance(instruments_raw, list):
        return None

    match = None
    for inst in instruments_raw:
        if not isinstance(inst, dict):
            continue
        try:
            ts = int(inst.get("expiration_timestamp") or 0)
        except (TypeError, ValueError):
            continue
        if ts == int(expiry_ts_ms):
            match = inst
            break
    if not match:
        return None

    name = str(match.get("instrument_name") or "")
    if not name:
        return None

    book = _fetch_deribit_book_summary(currency, "future")
    row = next(
        (
            r
            for r in book
            if str(r.get("instrument_name") or r.get("instrumentName") or "") == name
        ),
        None,
    )
    bid, ask = _bid_ask_from_book_row(row or {})
    if bid is None and ask is None:
        time.sleep(0.15)
        ticker = fetch_deribit_ticker(name)
        bid, ask = _bid_ask_from_ticker(ticker)
        ts = _ts_ms_from_row(ticker or {})
    else:
        ts = _ts_ms_from_row(row or {})

    return FutureLegQuote(
        instrument_name=name,
        bid=bid,
        ask=ask,
        expiry_ts_ms=int(expiry_ts_ms),
        quote_ts_ms=ts,
    )


def build_forward_consistency_live(
    *,
    asset_id: str,
    expiry_date: str,
) -> dict[str, Any]:
    """Build JSON-serializable forward consistency payload for one asset/expiry."""
    aid = str(asset_id or "BTC").strip().upper()
    as_of = datetime.now(timezone.utc).isoformat()
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    base: dict[str, Any] = {
        "schema_version": 1,
        "kind": "forward_consistency_boundary",
        "asset_id": aid,
        "expiry_date": expiry_date,
        "as_of_utc": as_of,
        "research_only": True,
        "copy_note": (
            "Spot vs future distribution is not arbitrage. This checks whether options imply "
            "a different executable forward than the futures/perp market after spreads and "
            "estimated costs. Simulation only — not order execution."
        ),
    }

    if not is_asset_enabled(aid):
        base.update(
            {
                "comparable": False,
                "venue": asset_venue(aid),
                "status": "NOT_COMPARABLE",
                "detail": f"Asset {aid} is not enabled in the catalog.",
            }
        )
        return base

    venue = asset_venue(aid)
    base["venue"] = venue

    if venue not in ("deribit",):
        base.update(
            {
                "comparable": False,
                "status": "NOT_COMPARABLE",
                "detail": (
                    f"Forward consistency v1 supports Deribit crypto (BTC/ETH). "
                    f"{aid} uses venue {venue!r} — coming in a follow-on slice."
                ),
            }
        )
        return base

    spot = fetch_deribit_index(deribit_currency(aid))
    if spot is None or spot <= 0:
        base.update(
            {
                "comparable": False,
                "status": "BAD_DATA",
                "detail": "Spot/index unavailable from venue.",
            }
        )
        return base
    base["spot_usd"] = float(spot)

    expiry_ts = resolve_expiry_ts_ms(aid, expiry_date)
    if expiry_ts is None:
        base.update(
            {
                "comparable": False,
                "status": "BAD_DATA",
                "detail": f"No option expiry matching {expiry_date!r}.",
            }
        )
        return base

    fwd_meta = fetch_deribit_forward_and_iv_for_expiry(expiry_ts, float(spot), currency=deribit_currency(aid))
    forward_usd = float(fwd_meta["forward"]) if fwd_meta else float(spot)
    base["forward_usd"] = forward_usd

    option_quotes = fetch_deribit_option_bid_ask_for_expiry(expiry_ts, asset_id=aid)
    future_quote = fetch_deribit_future_for_expiry(expiry_ts, asset_id=aid)
    if future_quote is None:
        base.update(
            {
                "comparable": False,
                "status": "BAD_DATA",
                "detail": "No dated future/perp matched to this option expiry on Deribit.",
            }
        )
        return base

    check = run_forward_consistency_check(
        option_quotes,
        future_quote,
        premium_in_usd=is_usd_premium_options_venue(aid),
        forward_usd=forward_usd,
        now_ms=now_ms,
        expected_expiry_ts_ms=expiry_ts,
    )

    base.update(
        {
            "comparable": True,
            "future_instrument": future_quote.instrument_name,
            **{k: v for k, v in check.__dict__.items() if k not in ("legs", "quality_flags")},
            "quality_flags": [flag.value for flag in check.quality_flags],
            "legs": [
                {"side": leg.side, "instrument_type": leg.instrument_type, "label": leg.label}
                for leg in check.legs
            ],
        }
    )
    return base


def list_forward_consistency_expiries(
    asset_id: str,
    *,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[str]:
    """Option expiry date strings for dashboard matrix (Deribit assets)."""
    aid = str(asset_id or "").strip().upper()
    if asset_venue(aid) != "deribit":
        return []
    rows = fetch_deribit_option_expiries(max_expiries, currency=deribit_currency(aid))
    return [str(row.get("expiry_date_str") or "")[:10] for row in rows if row.get("expiry_date_str")]


def _heatmap_cell_from_check(
    *,
    asset_id: str,
    expiry_date: str,
    check: ForwardConsistencyCheck,
    as_of_utc: str,
) -> ForwardConsistencyHeatmapCell:
    return ForwardConsistencyHeatmapCell(
        asset_id=asset_id,
        expiry_date=expiry_date,
        status=check.status,
        net_edge_usd=check.net_edge_usd,
        quality_flags=[flag.value for flag in check.quality_flags],
        as_of_utc=as_of_utc,
    )


def build_forward_consistency_matrix_cell(
    *,
    asset_id: str,
    expiry_date: str,
    as_of_utc: str | None = None,
    now_ms: int | None = None,
) -> ForwardConsistencyHeatmapCell:
    """Run one asset/expiry check and return a heatmap cell (no full boundary payload)."""
    aid = str(asset_id or "BTC").strip().upper()
    expiry = str(expiry_date or "").strip()[:10]
    as_of = as_of_utc or datetime.now(timezone.utc).isoformat()
    ts_now = now_ms if now_ms is not None else int(datetime.now(timezone.utc).timestamp() * 1000)

    if not is_asset_enabled(aid):
        return ForwardConsistencyHeatmapCell(
            asset_id=aid,
            expiry_date=expiry,
            status="NOT_COMPARABLE",
            net_edge_usd=None,
            quality_flags=[],
            as_of_utc=as_of,
        )

    if asset_venue(aid) != "deribit":
        return ForwardConsistencyHeatmapCell(
            asset_id=aid,
            expiry_date=expiry,
            status="NOT_COMPARABLE",
            net_edge_usd=None,
            quality_flags=[],
            as_of_utc=as_of,
        )

    spot = fetch_deribit_index(deribit_currency(aid))
    if spot is None or spot <= 0:
        return ForwardConsistencyHeatmapCell(
            asset_id=aid,
            expiry_date=expiry,
            status="BAD_DATA",
            net_edge_usd=None,
            quality_flags=[ForwardConsistencyQualityFlag.MISSING_LEG.value],
            as_of_utc=as_of,
        )

    expiry_ts = resolve_expiry_ts_ms(aid, expiry)
    if expiry_ts is None:
        return ForwardConsistencyHeatmapCell(
            asset_id=aid,
            expiry_date=expiry,
            status="BAD_DATA",
            net_edge_usd=None,
            quality_flags=[ForwardConsistencyQualityFlag.EXPIRY_MISMATCH.value],
            as_of_utc=as_of,
        )

    fwd_meta = fetch_deribit_forward_and_iv_for_expiry(
        expiry_ts, float(spot), currency=deribit_currency(aid)
    )
    forward_usd = float(fwd_meta["forward"]) if fwd_meta else float(spot)

    option_quotes = fetch_deribit_option_bid_ask_for_expiry(expiry_ts, asset_id=aid)
    future_quote = fetch_deribit_future_for_expiry(expiry_ts, asset_id=aid)
    if future_quote is None:
        check = ForwardConsistencyCheck(
            status="BAD_DATA",
            quality_flags=[ForwardConsistencyQualityFlag.MISSING_LEG],
            detail="No dated future/perp matched to this option expiry on Deribit.",
        )
        return _heatmap_cell_from_check(
            asset_id=aid,
            expiry_date=expiry,
            check=check,
            as_of_utc=as_of,
        )

    check = run_forward_consistency_check(
        option_quotes,
        future_quote,
        premium_in_usd=is_usd_premium_options_venue(aid),
        forward_usd=forward_usd,
        now_ms=ts_now,
        expected_expiry_ts_ms=expiry_ts,
    )
    return _heatmap_cell_from_check(
        asset_id=aid,
        expiry_date=expiry,
        check=check,
        as_of_utc=as_of,
    )


def summarize_forward_consistency_cells(
    cells: list[ForwardConsistencyHeatmapCell],
) -> dict[str, int]:
    assets = {cell.asset_id for cell in cells}
    expiries = {(cell.asset_id, cell.expiry_date) for cell in cells}
    return {
        "assets_checked": len(assets),
        "expiries_checked": len(expiries),
        "watch_count": sum(1 for c in cells if c.status == "WATCH"),
        "possible_count": sum(1 for c in cells if c.status == "POSSIBLE_ARB"),
        "bad_data_count": sum(1 for c in cells if c.status == "BAD_DATA"),
    }


def build_forward_consistency_dashboard(
    *,
    asset_ids: list[str] | None = None,
    max_expiries_per_asset: int = DEFAULT_OPTION_EXPIRIES_MAX,
    as_of_utc: str | None = None,
    now_ms: int | None = None,
) -> ForwardConsistencyDashboardPayload:
    """Build heatmap matrix over enabled assets × option expiries."""
    as_of = as_of_utc or datetime.now(timezone.utc).isoformat()
    ids = asset_ids if asset_ids is not None else list_enabled_asset_ids()
    cells: list[ForwardConsistencyHeatmapCell] = []

    for aid in ids:
        expiries = list_forward_consistency_expiries(aid, max_expiries=max_expiries_per_asset)
        if not expiries:
            cells.append(
                ForwardConsistencyHeatmapCell(
                    asset_id=aid,
                    expiry_date="",
                    status="NOT_COMPARABLE" if asset_venue(aid) != "deribit" else "BAD_DATA",
                    net_edge_usd=None,
                    quality_flags=[],
                    as_of_utc=as_of,
                )
            )
            continue
        for expiry_date in expiries:
            cells.append(
                build_forward_consistency_matrix_cell(
                    asset_id=aid,
                    expiry_date=expiry_date,
                    as_of_utc=as_of,
                    now_ms=now_ms,
                )
            )

    return ForwardConsistencyDashboardPayload(
        summary=summarize_forward_consistency_cells(cells),
        cells=cells,
    )


def dashboard_payload_to_dict(payload: ForwardConsistencyDashboardPayload) -> dict[str, Any]:
    return {
        "kind": payload.kind,
        "schema_version": payload.schema_version,
        "summary": dict(payload.summary),
        "cells": [
            {
                "asset_id": cell.asset_id,
                "expiry_date": cell.expiry_date,
                "status": cell.status,
                "net_edge_usd": cell.net_edge_usd,
                "quality_flags": list(cell.quality_flags),
                "as_of_utc": cell.as_of_utc,
            }
            for cell in payload.cells
        ],
    }
