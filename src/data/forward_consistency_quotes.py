"""
Live bid/ask quotes for forward consistency checks (venue adapters).
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from src.data.assets_registry import (
    asset_venue,
    deribit_currency,
    is_asset_enabled,
    is_usd_premium_options_venue,
)
from src.data.fetch_deribit import (
    fetch_deribit_index,
    fetch_deribit_forward_and_iv_for_expiry,
    fetch_deribit_option_expiries,
    fetch_deribit_options_instruments,
    fetch_deribit_ticker,
    _deribit_public_request,
)
from src.engine.forward_consistency import (
    FutureLegQuote,
    OptionLegQuote,
    run_forward_consistency_check,
)


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
    )

    base.update(
        {
            "comparable": True,
            "future_instrument": future_quote.instrument_name,
            **{k: v for k, v in check.__dict__.items() if k != "legs"},
            "legs": [
                {"side": leg.side, "instrument_type": leg.instrument_type, "label": leg.label}
                for leg in check.legs
            ],
        }
    )
    return base
