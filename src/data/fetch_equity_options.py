"""
Fetch US equity options via Yahoo Finance; normalize to Deribit-shaped instrument/mark payloads.

v1: single-name wedge (default NVDA). Marks use USD premium per share in the ``mark_btc`` field
for compatibility with existing engine helpers (misnamed for crypto coin units).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf

from src.data.assets_registry import equity_symbol as registry_equity_symbol

logger = logging.getLogger(__name__)

DEFAULT_OPTION_EXPIRIES_MAX = 20


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").strip().upper()


def _resolve_symbol(*, asset_id: str | None = None, symbol: str | None = None) -> str:
    if symbol:
        return _normalize_symbol(symbol)
    return registry_equity_symbol(asset_id or "NVDA")


def _expiry_str_to_ms(expiry: str) -> int:
    dt = datetime.strptime(str(expiry).strip(), "%Y-%m-%d").replace(
        hour=21, minute=0, second=0, tzinfo=timezone.utc
    )
    return int(dt.timestamp() * 1000)


def _instrument_name(symbol: str, expiry: str, strike: float, option_type: str) -> str:
    exp_compact = str(expiry).replace("-", "")
    strike_label = str(int(strike)) if float(strike).is_integer() else str(strike)
    side = "C" if option_type == "call" else "P"
    return f"{_normalize_symbol(symbol)}-{exp_compact}-{strike_label}-{side}"


def _row_mark_usd(row: pd.Series) -> float | None:
    for key in ("lastPrice", "last", "mark"):
        val = row.get(key)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            try:
                out = float(val)
                if out >= 0:
                    return out
            except (TypeError, ValueError):
                continue
    bid = row.get("bid")
    ask = row.get("ask")
    try:
        b = float(bid) if bid is not None and not pd.isna(bid) else None
        a = float(ask) if ask is not None and not pd.isna(ask) else None
    except (TypeError, ValueError):
        b = a = None
    if b is not None and a is not None and b >= 0 and a >= 0:
        return (b + a) / 2.0
    if b is not None and b >= 0:
        return b
    if a is not None and a >= 0:
        return a
    return None


def _iter_chain_rows(
    symbol: str,
    *,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[tuple[str, int, str, pd.Series]]:
    """Yield (expiry_str, expiry_ts_ms, option_type, row) for calls and puts."""
    sym = _normalize_symbol(symbol)
    try:
        tk = yf.Ticker(sym)
        opts = getattr(tk, "options", None)
        if not opts:
            return []
        expiries = list(opts)[: max(1, int(max_expiries))]
    except Exception as exc:
        logger.warning("equity options list failed for %s: %s", sym, exc)
        return []

    rows: list[tuple[str, int, str, pd.Series]] = []
    for exp in expiries:
        try:
            chain = tk.option_chain(str(exp))
        except Exception as exc:
            logger.warning("equity option_chain failed for %s %s: %s", sym, exp, exc)
            continue
        if chain is None:
            continue
        try:
            expiry_ts = _expiry_str_to_ms(str(exp))
        except ValueError:
            continue
        for option_type, frame in (("call", chain.calls), ("put", chain.puts)):
            if frame is None or frame.empty:
                continue
            for _, row in frame.iterrows():
                rows.append((str(exp), expiry_ts, option_type, row))
    return rows


def fetch_equity_options_instruments(
    symbol: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[dict[str, Any]]:
    """
    List option instruments in Deribit-shaped dicts:
    instrument_name, strike, expiration_timestamp, option_type (call/put).
    """
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    out: list[dict[str, Any]] = []
    for expiry, expiry_ts, option_type, row in _iter_chain_rows(sym, max_expiries=max_expiries):
        strike = row.get("strike")
        if strike is None or (isinstance(strike, float) and pd.isna(strike)):
            continue
        try:
            strike_f = float(strike)
        except (TypeError, ValueError):
            continue
        name = row.get("contractSymbol") or _instrument_name(sym, expiry, strike_f, option_type)
        out.append(
            {
                "instrument_name": str(name),
                "strike": strike_f,
                "expiration_timestamp": expiry_ts,
                "option_type": option_type,
                "equity_symbol": sym,
                "expiry_date_str": expiry,
            }
        )
    return out


def fetch_equity_option_expiries(
    symbol: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[dict[str, Any]]:
    """Nearest listed expiries (Deribit-shaped metadata)."""
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    seen: set[int] = set()
    out: list[dict[str, Any]] = []
    for expiry, expiry_ts, _option_type, _row in _iter_chain_rows(sym, max_expiries=max_expiries):
        if expiry_ts in seen:
            continue
        seen.add(expiry_ts)
        out.append(
            {
                "expiration_timestamp": expiry_ts,
                "expiry_date_str": expiry,
                "equity_symbol": sym,
            }
        )
        if len(out) >= max_expiries:
            break
    out.sort(key=lambda r: r["expiration_timestamp"])
    return out


def fetch_equity_option_book_marks(
    symbol: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> dict[str, float]:
    """instrument_name -> USD mark (Deribit book_marks shape)."""
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    marks: dict[str, float] = {}
    for expiry, _expiry_ts, option_type, row in _iter_chain_rows(sym, max_expiries=max_expiries):
        strike = row.get("strike")
        if strike is None:
            continue
        try:
            strike_f = float(strike)
        except (TypeError, ValueError):
            continue
        mark = _row_mark_usd(row)
        if mark is None:
            continue
        name = row.get("contractSymbol") or _instrument_name(sym, expiry, strike_f, option_type)
        marks[str(name)] = float(mark)
    return marks


def fetch_equity_option_marks_by_expiry(
    expiry_ts: int,
    symbol: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[dict[str, Any]]:
    """
    Call option (strike, mark_btc) for one expiry.
    mark_btc holds USD premium per share for equity venue compatibility.
    """
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    result: list[dict[str, Any]] = []
    for expiry, row_expiry_ts, option_type, row in _iter_chain_rows(sym, max_expiries=max_expiries):
        if row_expiry_ts != int(expiry_ts) or option_type != "call":
            continue
        strike = row.get("strike")
        if strike is None:
            continue
        try:
            strike_f = float(strike)
        except (TypeError, ValueError):
            continue
        mark = _row_mark_usd(row)
        if mark is None:
            continue
        result.append({"strike": strike_f, "mark_btc": float(mark), "expiry_date_str": expiry})
    result.sort(key=lambda x: x["strike"])
    return result


def fetch_equity_spot(symbol: str | None = None, *, asset_id: str | None = None) -> float | None:
    """Latest equity spot from Yahoo (regular market price)."""
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    try:
        tk = yf.Ticker(sym)
        info = tk.fast_info if hasattr(tk, "fast_info") else {}
        last = getattr(info, "last_price", None) if not isinstance(info, dict) else info.get("last_price")
        if last is not None:
            return float(last)
        hist = tk.history(period="1d")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            return float(hist["Close"].iloc[-1])
    except Exception as exc:
        logger.warning("equity spot failed for %s: %s", sym, exc)
    return None


def _normalize_iv_decimal(iv: float | None) -> float | None:
    if iv is None:
        return None
    try:
        val = float(iv)
    except (TypeError, ValueError):
        return None
    if val <= 0:
        return None
    if val > 2.0:
        return val / 100.0
    return val


def fetch_equity_forward_and_iv_for_expiry(
    expiry_ts: int,
    spot_price: float,
    *,
    asset_id: str | None = None,
    symbol: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> dict[str, Any] | None:
    """
    Forward + ATM IV for one equity expiry.
    v1: forward = spot (no dividend/carry); ATM IV from nearest call impliedVolatility.
    """
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    spot = float(spot_price)
    atm_candidates: list[tuple[float, float | None]] = []
    for _expiry, row_expiry_ts, option_type, row in _iter_chain_rows(sym, max_expiries=max_expiries):
        if row_expiry_ts != int(expiry_ts) or option_type != "call":
            continue
        strike = row.get("strike")
        if strike is None:
            continue
        try:
            strike_f = float(strike)
        except (TypeError, ValueError):
            continue
        iv = _normalize_iv_decimal(row.get("impliedVolatility"))
        atm_candidates.append((strike_f, iv))
    if not atm_candidates:
        return None
    _strike, iv = min(atm_candidates, key=lambda pair: abs(pair[0] - spot))
    return {
        "forward": spot,
        "atm_iv": iv if iv is not None else 0.35,
        "expiry_ts": int(expiry_ts),
        "spot": spot,
    }


def fetch_equity_option_marks_by_expiry_full(
    expiry_ts: int,
    symbol: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> dict[str, list[dict[str, Any]]]:
    """Call and put marks for one expiry (Deribit full-mark shape)."""
    sym = _resolve_symbol(asset_id=asset_id, symbol=symbol)
    res_calls: list[dict[str, Any]] = []
    res_puts: list[dict[str, Any]] = []
    for expiry, row_expiry_ts, option_type, row in _iter_chain_rows(sym, max_expiries=max_expiries):
        if row_expiry_ts != int(expiry_ts):
            continue
        strike = row.get("strike")
        if strike is None:
            continue
        try:
            strike_f = float(strike)
        except (TypeError, ValueError):
            continue
        mark = _row_mark_usd(row)
        if mark is None:
            continue
        oi = row.get("openInterest")
        try:
            open_interest = int(oi) if oi is not None and not pd.isna(oi) else 0
        except (TypeError, ValueError):
            open_interest = 0
        entry = {
            "strike": strike_f,
            "mark_btc": float(mark),
            "open_interest": open_interest,
            "expiry_date_str": expiry,
        }
        if option_type == "call":
            res_calls.append(entry)
        else:
            res_puts.append(entry)
    res_calls.sort(key=lambda x: x["strike"])
    res_puts.sort(key=lambda x: x["strike"])
    return {"calls": res_calls, "puts": res_puts}


MIN_EQUITY_CALL_MARKS_FOR_BL = 3
MIN_EQUITY_TOTAL_OPEN_INTEREST = 100


def assess_equity_chain_trust(
    call_marks: list[dict[str, Any]],
    *,
    min_marks: int = MIN_EQUITY_CALL_MARKS_FOR_BL,
    min_total_oi: int = MIN_EQUITY_TOTAL_OPEN_INTEREST,
) -> dict[str, Any]:
    """Trust flags for equity option chains (v1 honest labeling)."""
    flags: list[str] = ["dividend_caveat_unmodeled"]
    if len(call_marks) < min_marks:
        flags.append("insufficient_marks")
    total_oi = sum(int(m.get("open_interest") or 0) for m in call_marks)
    if total_oi < min_total_oi:
        flags.append("thin_open_interest")
    return {
        "trust_flags": flags,
        "trust_ok": "insufficient_marks" not in flags,
        "total_open_interest": total_oi,
    }


def format_equity_trust_suffix(trust: dict[str, Any]) -> str:
    flags = trust.get("trust_flags") or []
    extra = [f for f in flags if f != "dividend_caveat_unmodeled"]
    if not extra:
        return "dividend_caveat_unmodeled"
    return "|".join(flags)
