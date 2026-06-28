"""
Fetch crypto options from Bybit v5 public API; normalize to Deribit-shaped instrument/mark payloads.

USDT-settled premiums (USD/share semantics) — use equity-style distribution export path.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any

import requests

from src.data.assets_registry import bybit_base_coin as registry_bybit_base_coin

logger = logging.getLogger(__name__)

BYBIT_BASE = "https://api.bybit.com/v5"
DEFAULT_OPTION_EXPIRIES_MAX = 20

_SYMBOL_RE = re.compile(
    r"^(?P<base>[A-Z0-9]+)-(?P<exp>[0-9]{1,2}[A-Z]{3}[0-9]{2})-(?P<strike>[0-9.]+)-(?P<side>[CP])-(?P<settle>[A-Z]+)$"
)


def _normalize_base_coin(base_coin: str) -> str:
    return str(base_coin or "").strip().upper()


def _resolve_base_coin(*, asset_id: str | None = None, base_coin: str | None = None) -> str:
    if base_coin:
        return _normalize_base_coin(base_coin)
    return registry_bybit_base_coin(asset_id or "SOL")


def _bybit_get(path: str, params: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, str | None]:
    url = f"{BYBIT_BASE}/{path.lstrip('/')}"
    last_err: str | None = None
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params or {}, timeout=20)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(0.4 * (attempt + 1))
                last_err = f"HTTP {resp.status_code}"
                continue
            resp.raise_for_status()
            body = resp.json()
            if not isinstance(body, dict):
                return None, "unexpected JSON root"
            if int(body.get("retCode") or 0) != 0:
                return None, str(body.get("retMsg") or body.get("retCode"))
            result = body.get("result")
            return result if isinstance(result, dict) else {}, None
        except requests.RequestException as exc:
            last_err = str(exc)
            if attempt < 2:
                time.sleep(0.4 * (attempt + 1))
                continue
            break
    logger.warning("Bybit GET %s failed: %s", path, last_err)
    return None, last_err


def _parse_symbol(symbol: str) -> dict[str, Any] | None:
    m = _SYMBOL_RE.match(str(symbol or "").strip().upper())
    if not m:
        return None
    side = m.group("side")
    try:
        strike = float(m.group("strike"))
    except ValueError:
        return None
    return {
        "strike": strike,
        "option_type": "call" if side == "C" else "put",
    }


def _option_type_from_row(row: dict[str, Any]) -> str:
    raw = str(row.get("optionsType") or "").strip().lower()
    if raw == "call":
        return "call"
    if raw == "put":
        return "put"
    parsed = _parse_symbol(str(row.get("symbol") or ""))
    return parsed["option_type"] if parsed else "call"


def _fetch_instruments_pages(base_coin: str) -> list[dict[str, Any]]:
    coin = _normalize_base_coin(base_coin)
    out: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(20):
        params: dict[str, Any] = {"category": "option", "baseCoin": coin, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        result, err = _bybit_get("market/instruments-info", params)
        if result is None:
            logger.warning("Bybit instruments-info for %s: %s", coin, err)
            break
        batch = result.get("list") or []
        if isinstance(batch, list):
            out.extend(row for row in batch if isinstance(row, dict))
        cursor = result.get("nextPageCursor") or None
        if not cursor:
            break
    return out


def _fetch_tickers(base_coin: str) -> list[dict[str, Any]]:
    coin = _normalize_base_coin(base_coin)
    result, err = _bybit_get(
        "market/tickers",
        {"category": "option", "baseCoin": coin},
    )
    if result is None:
        logger.warning("Bybit tickers for %s: %s", coin, err)
        return []
    batch = result.get("list") or []
    return batch if isinstance(batch, list) else []


def _ticker_map(base_coin: str) -> dict[str, dict[str, Any]]:
    return {str(row.get("symbol")): row for row in _fetch_tickers(base_coin) if row.get("symbol")}


def fetch_bybit_options_instruments(
    base_coin: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[dict[str, Any]]:
    """Deribit-shaped instruments: instrument_name, strike, expiration_timestamp, option_type."""
    coin = _resolve_base_coin(asset_id=asset_id, base_coin=base_coin)
    raw_rows = _fetch_instruments_pages(coin)
    expiry_ts_set: set[int] = set()
    for row in raw_rows:
        if str(row.get("status") or "").lower() not in ("trading", "live", ""):
            if row.get("status"):
                continue
        try:
            ts = int(row.get("deliveryTime") or 0)
        except (TypeError, ValueError):
            continue
        if ts > 0:
            expiry_ts_set.add(ts)
    allowed_ts = sorted(expiry_ts_set)[: max(1, int(max_expiries))]

    out: list[dict[str, Any]] = []
    for row in raw_rows:
        symbol = str(row.get("symbol") or "")
        if not symbol:
            continue
        parsed = _parse_symbol(symbol)
        if not parsed:
            continue
        try:
            expiry_ts = int(row.get("deliveryTime") or 0)
        except (TypeError, ValueError):
            continue
        if expiry_ts not in allowed_ts:
            continue
        out.append(
            {
                "instrument_name": symbol,
                "strike": float(parsed["strike"]),
                "expiration_timestamp": expiry_ts,
                "option_type": _option_type_from_row(row),
                "bybit_base_coin": coin,
                "expiry_date_str": datetime.fromtimestamp(
                    expiry_ts / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d"),
            }
        )
    return out


def fetch_bybit_option_expiries(
    base_coin: str | None = None,
    *,
    asset_id: str | None = None,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
) -> list[dict[str, Any]]:
    instruments = fetch_bybit_options_instruments(
        base_coin, asset_id=asset_id, max_expiries=max_expiries
    )
    exp_ts = sorted({int(i["expiration_timestamp"]) for i in instruments if i.get("expiration_timestamp")})
    return [
        {
            "expiry_ts": ts,
            "expiry_date_str": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
        }
        for ts in exp_ts[:max_expiries]
    ]


def fetch_bybit_option_book_marks(
    base_coin: str | None = None,
    *,
    asset_id: str | None = None,
) -> dict[str, float]:
    coin = _resolve_base_coin(asset_id=asset_id, base_coin=base_coin)
    out: dict[str, float] = {}
    for symbol, row in _ticker_map(coin).items():
        mark = row.get("markPrice")
        if mark is None:
            continue
        try:
            out[symbol] = float(mark)
        except (TypeError, ValueError):
            continue
    return out


def fetch_bybit_spot(*, asset_id: str | None = None, base_coin: str | None = None) -> float | None:
    coin = _resolve_base_coin(asset_id=asset_id, base_coin=base_coin)
    tickers = _ticker_map(coin)
    for row in tickers.values():
        for key in ("indexPrice", "underlyingPrice", "markPrice"):
            val = row.get(key)
            if val is None:
                continue
            try:
                price = float(val)
                if price > 0:
                    return price
            except (TypeError, ValueError):
                continue
    result, _ = _bybit_get("market/tickers", {"category": "linear", "symbol": f"{coin}USDT"})
    if result:
        for row in result.get("list") or []:
            val = row.get("lastPrice") or row.get("markPrice")
            if val is not None:
                try:
                    return float(val)
                except (TypeError, ValueError):
                    pass
    return None


def fetch_bybit_forward_and_iv_for_expiry(
    expiry_ts: int,
    spot_price: float,
    *,
    asset_id: str | None = None,
    base_coin: str | None = None,
) -> dict[str, Any] | None:
    coin = _resolve_base_coin(asset_id=asset_id, base_coin=base_coin)
    instruments = fetch_bybit_options_instruments(coin, asset_id=asset_id)
    calls = [
        i
        for i in instruments
        if i.get("option_type") == "call" and int(i.get("expiration_timestamp") or 0) == int(expiry_ts)
    ]
    if not calls:
        return None
    best = min(calls, key=lambda i: abs(float(i.get("strike") or 0) - float(spot_price)))
    symbol = str(best.get("instrument_name") or "")
    ticker = _ticker_map(coin).get(symbol)
    if not ticker:
        return {"forward": float(spot_price), "atm_iv": 0.6, "expiry_ts": expiry_ts}
    forward = ticker.get("underlyingPrice") or ticker.get("indexPrice") or spot_price
    iv = ticker.get("markIv")
    try:
        forward_f = float(forward)
    except (TypeError, ValueError):
        forward_f = float(spot_price)
    iv_f: float | None = None
    if iv is not None:
        try:
            iv_f = float(iv)
            if iv_f > 2:
                iv_f = iv_f / 100.0
        except (TypeError, ValueError):
            iv_f = None
    return {"forward": forward_f, "atm_iv": iv_f or 0.6, "expiry_ts": expiry_ts}


def fetch_bybit_option_marks_by_expiry_full(
    expiry_ts: int,
    *,
    asset_id: str | None = None,
    base_coin: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    coin = _resolve_base_coin(asset_id=asset_id, base_coin=base_coin)
    instruments = fetch_bybit_options_instruments(coin, asset_id=asset_id)
    for_exp = [i for i in instruments if int(i.get("expiration_timestamp") or 0) == int(expiry_ts)]
    marks = fetch_bybit_option_book_marks(coin, asset_id=asset_id)
    res_calls: list[dict[str, Any]] = []
    res_puts: list[dict[str, Any]] = []
    for inst in for_exp:
        name = str(inst.get("instrument_name") or "")
        strike = inst.get("strike")
        mark = marks.get(name)
        if strike is None or mark is None:
            continue
        entry = {"strike": float(strike), "mark_btc": float(mark)}
        if inst.get("option_type") == "call":
            res_calls.append(entry)
        else:
            res_puts.append(entry)
    res_calls.sort(key=lambda x: x["strike"])
    res_puts.sort(key=lambda x: x["strike"])
    return {"calls": res_calls, "puts": res_puts}
