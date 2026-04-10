"""
Fetch Bitcoin options from Deribit (public API, no auth). Rate limit: ~1 req/sec sustained for get_instruments.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import requests

DERIBIT_BASE = "https://www.deribit.com/api/v2"

logger = logging.getLogger(__name__)

# Set on failed get_instruments; cleared on success (for implied-lab debug UI).
_LAST_INSTRUMENTS_DIAGNOSTIC: str | None = None


def last_deribit_instruments_diagnostic() -> str | None:
    return _LAST_INSTRUMENTS_DIAGNOSTIC


def _deribit_public_request(
    method: str,
    params: dict[str, Any] | None = None,
) -> tuple[Any | None, str | None]:
    """
    GET public JSON-RPC-style endpoint. Returns (result, None) on success, (None, err_msg) on failure.
    Retries transient timeouts, connection errors, and HTTP 429 / 502 / 503 / 504.
    """
    url = f"{DERIBIT_BASE}/public/{method}"
    q = params or {}
    last_err: str | None = None
    for attempt in range(3):
        try:
            r = requests.get(url, params=q, timeout=15)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(0.4 * (attempt + 1))
                last_err = f"HTTP {r.status_code} (transient)"
                continue
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, dict):
                last_err = f"Unexpected JSON root type: {type(data).__name__}"
                if attempt < 2:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                logger.warning("Deribit %s: %s", method, last_err)
                return None, last_err
            if data.get("error"):
                err = data["error"]
                if isinstance(err, dict):
                    code = err.get("code")
                    msg = err.get("message", err)
                    detail = f"Deribit error {code}: {msg}" if code is not None else f"Deribit error: {msg}"
                else:
                    detail = f"Deribit error: {err}"
                logger.warning("Deribit %s: %s", method, detail)
                return None, detail
            if "result" in data:
                return data["result"], None
            last_err = "JSON had no result (and no error)"
            logger.warning("Deribit %s: %s", method, last_err)
            return None, last_err
        except requests.Timeout:
            last_err = "Request timed out"
        except requests.ConnectionError as e:
            last_err = f"Connection error: {e}"
        except requests.HTTPError as e:
            sc = e.response.status_code if e.response is not None else None
            last_err = f"HTTP {sc}"
            if sc in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(0.4 * (attempt + 1))
                continue
            break
        except ValueError as e:
            last_err = f"Invalid JSON: {e}"
            break
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            break
        if attempt < 2:
            time.sleep(0.4 * (attempt + 1))
    logger.warning("Deribit %s failed after retries: %s", method, last_err)
    return None, last_err


def _request(method: str, params: dict[str, Any] | None = None) -> dict | list | None:
    """GET request to Deribit JSON-RPC style public endpoint. Params as query string."""
    out, _err = _deribit_public_request(method, params)
    return out


def fetch_deribit_btc_options_instruments(expired: bool = False) -> list[dict[str, Any]]:
    """
    List BTC option instruments. Each has instrument_name, strike, expiration_timestamp, option_type (call/put).
    """
    global _LAST_INSTRUMENTS_DIAGNOSTIC
    out, err = _deribit_public_request(
        "get_instruments",
        {"currency": "BTC", "kind": "option", "expired": str(expired).lower()},
    )
    if isinstance(out, list):
        _LAST_INSTRUMENTS_DIAGNOSTIC = None
        return out
    _LAST_INSTRUMENTS_DIAGNOSTIC = err or "No instrument list returned."
    return []


def fetch_deribit_btc_options_for_chart(
    instruments: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    List of options with expiry_date (datetime), strike, option_type for plotting on (date, price) chart.
    No ticker calls; uses get_instruments once unless instruments is provided.
    """
    if instruments is None:
        instruments = fetch_deribit_btc_options_instruments(expired=False)
    out = []
    for i in instruments:
        ts = i.get("expiration_timestamp")
        strike = i.get("strike")
        if ts is None or strike is None:
            continue
        out.append({
            "expiry_date": datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
            "strike": float(strike),
            "option_type": i.get("option_type") or "option",
            "instrument_name": i.get("instrument_name"),
        })
    return out


def fetch_deribit_ticker(instrument_name: str) -> dict[str, Any] | None:
    """Get ticker (mark_price, last, bid, ask, etc.) for one instrument."""
    out = _request("ticker", {"instrument_name": instrument_name})
    if isinstance(out, dict):
        return out
    return None


def fetch_deribit_btc_index() -> float | None:
    """Get BTC spot/index price from Deribit perpetual. Fallback when Yahoo fails."""
    ticker = fetch_deribit_ticker("BTC-PERPETUAL")
    if not isinstance(ticker, dict):
        return None
    idx = ticker.get("index_price") or ticker.get("indexPrice")
    if idx is not None:
        try:
            return float(idx)
        except (TypeError, ValueError):
            pass
    return _ticker_price(ticker)


def _ticker_price(ticker: dict[str, Any] | None) -> float | None:
    """Extract price from ticker; try mark_price, last_price, mid, etc."""
    if not isinstance(ticker, dict):
        return None
    for key in (
        "mark_price", "last_price", "markPrice", "lastPrice",
        "settlement_price", "estimated_delivery_price",
    ):
        v = ticker.get(key)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    bid = ticker.get("best_bid_price") or ticker.get("bestBidPrice")
    ask = ticker.get("best_ask_price") or ticker.get("bestAskPrice")
    if bid is not None and ask is not None:
        try:
            return (float(bid) + float(ask)) / 2
        except (TypeError, ValueError):
            pass
    if bid is not None:
        try:
            return float(bid)
        except (TypeError, ValueError):
            pass
    if ask is not None:
        try:
            return float(ask)
        except (TypeError, ValueError):
            pass
    return None


def _mark_prices_by_instrument_from_book_summary(rows: list | None) -> dict[str, float]:
    """Map instrument_name -> mark_price from get_book_summary_by_currency result."""
    out: dict[str, float] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        name = row.get("instrument_name") or row.get("instrumentName")
        if not name:
            continue
        mark = row.get("mark_price") or row.get("markPrice")
        if mark is None:
            continue
        try:
            out[name] = float(mark)
        except (TypeError, ValueError):
            continue
    return out


def fetch_deribit_btc_option_book_marks() -> dict[str, float]:
    """All BTC option mark prices in one request (preferred over many public/ticker calls)."""
    book = _request("get_book_summary_by_currency", {"currency": "BTC", "kind": "option"})
    return _mark_prices_by_instrument_from_book_summary(book if isinstance(book, list) else None)


def _option_mark_btc_from_book_or_ticker(name: str, book_marks: dict[str, float]) -> float | None:
    v = book_marks.get(name)
    if v is not None:
        return v
    return _ticker_price(fetch_deribit_ticker(name))


def fetch_deribit_btc_futures_forward_curve(max_contracts: int = 12) -> list[dict[str, Any]]:
    """
    Option B "see into the future": list of BTC futures with (expiry_date, mark_price).
    Excludes perpetual. Returns sorted by expiry; each point is (expiry_date, price) for the chart.
    Uses one get_book_summary_by_currency(BTC, future) for marks instead of N ticker calls.
    """
    out = _request("get_instruments", {"currency": "BTC", "kind": "future", "expired": "false"})
    if not isinstance(out, list):
        return []
    # Exclude perpetual (expiration_timestamp very large, e.g. year 3000)
    now_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    five_years_ms = 5 * 365 * 24 * 60 * 60 * 1000
    dated = [i for i in out if (i.get("expiration_timestamp") or 0) < now_ts + five_years_ms]
    # Sort by expiry, take nearest max_contracts
    dated.sort(key=lambda i: i.get("expiration_timestamp") or 0)
    dated = dated[:max_contracts]

    book = _request("get_book_summary_by_currency", {"currency": "BTC", "kind": "future"})
    mark_by_name = _mark_prices_by_instrument_from_book_summary(book if isinstance(book, list) else None)

    result = []
    missing_ticker: list[tuple[str, int]] = []  # (name, expiry_ts_ms)
    for inst in dated:
        name = inst.get("instrument_name")
        ts = inst.get("expiration_timestamp")
        if not name or not ts:
            continue
        mark = mark_by_name.get(name)
        if mark is not None:
            result.append({
                "expiry_date": datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                "mark_price": mark,
                "instrument_name": name,
            })
        else:
            missing_ticker.append((name, ts))

    if missing_ticker:
        # Rare: book summary missing an instrument; fall back to ticker (gentle pacing)
        for j, (name, ts) in enumerate(missing_ticker):
            if j > 0:
                time.sleep(0.2)
            ticker = fetch_deribit_ticker(name)
            mark = _ticker_price(ticker)
            if mark is not None:
                result.append({
                    "expiry_date": datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                    "mark_price": mark,
                    "instrument_name": name,
                })

    result.sort(key=lambda r: r["expiry_date"])
    return [r for r in result if r.get("mark_price") is not None]


def fetch_deribit_btc_option_expiries(max_expiries: int = 12) -> list[dict[str, Any]]:
    """
    List of BTC option expiries: {expiry_ts, expiry_date_str} for use in distribution chart.
    """
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    exp_ts = sorted(set(i.get("expiration_timestamp") for i in instruments if i.get("expiration_timestamp")))
    out = []
    for ts in exp_ts[:max_expiries]:
        out.append({
            "expiry_ts": ts,
            "expiry_date_str": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
        })
    return out


def fetch_deribit_btc_option_marks_by_expiry(expiry_ts: int) -> list[dict[str, Any]]:
    """
    Get call option (strike, mark_btc) for one expiry. Uses get_book_summary_by_currency
    for one request, then filters by expiry. Returns list of {strike, mark_btc} for calls.
    """
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    calls_for_exp = [
        i for i in instruments
        if i.get("option_type") == "call" and i.get("expiration_timestamp") == expiry_ts
    ]
    if not calls_for_exp:
        return []
    names = {i.get("instrument_name") for i in calls_for_exp if i.get("instrument_name")}
    strike_by_name = {i.get("instrument_name"): i.get("strike") for i in calls_for_exp if i.get("strike") is not None}
    out = _request("get_book_summary_by_currency", {"currency": "BTC", "kind": "option"})
    if not isinstance(out, list):
        return []
    result = []
    for row in out:
        name = row.get("instrument_name") or row.get("instrumentName")
        if name not in names:
            continue
        strike = strike_by_name.get(name)
        if strike is None:
            continue
        mark = row.get("mark_price") or row.get("markPrice")
        if mark is not None:
            try:
                result.append({"strike": float(strike), "mark_btc": float(mark)})
            except (TypeError, ValueError):
                pass
    result.sort(key=lambda x: x["strike"])
    return result


def fetch_deribit_btc_option_marks_by_expiry_full(expiry_ts: int) -> dict[str, list[dict[str, Any]]]:
    """
    Get call and put option (strike, mark_btc) for one expiry. One book summary request.
    Returns {"calls": [{strike, mark_btc}, ...], "puts": [{strike, mark_btc}, ...]}.
    """
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    for_exp = [i for i in instruments if i.get("expiration_timestamp") == expiry_ts]
    calls = [i for i in for_exp if i.get("option_type") == "call"]
    puts = [i for i in for_exp if i.get("option_type") == "put"]
    names_to_strike = {i.get("instrument_name"): i.get("strike") for i in for_exp if i.get("strike") is not None and i.get("instrument_name")}
    call_names = {i.get("instrument_name") for i in calls if i.get("instrument_name")}
    put_names = {i.get("instrument_name") for i in puts if i.get("instrument_name")}
    out = _request("get_book_summary_by_currency", {"currency": "BTC", "kind": "option"})
    if not isinstance(out, list):
        return {"calls": [], "puts": []}
    res_calls = []
    res_puts = []
    for row in out:
        name = row.get("instrument_name") or row.get("instrumentName")
        strike = names_to_strike.get(name) if name else None
        if strike is None:
            continue
        mark = row.get("mark_price") or row.get("markPrice")
        if mark is None:
            continue
        try:
            entry = {"strike": float(strike), "mark_btc": float(mark)}
        except (TypeError, ValueError):
            continue
        if name in call_names:
            res_calls.append(entry)
        if name in put_names:
            res_puts.append(entry)
    res_calls.sort(key=lambda x: x["strike"])
    res_puts.sort(key=lambda x: x["strike"])
    return {"calls": res_calls, "puts": res_puts}


def fetch_deribit_forward_and_iv_for_expiry(
    expiry_ts: int,
    spot_price: float,
) -> dict[str, Any] | None:
    """
    Get forward price and ATM implied vol for a given option expiry.
    Picks a call with strike nearest to spot, fetches ticker; returns index_price (forward) and mark_iv.
    """
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    calls = [i for i in instruments if i.get("option_type") == "call" and i.get("expiration_timestamp") == expiry_ts]
    if not calls:
        return None
    # Strike closest to spot
    best = min(calls, key=lambda i: abs((i.get("strike") or 0) - spot_price))
    name = best.get("instrument_name")
    if not name:
        return None
    time.sleep(0.2)
    ticker = fetch_deribit_ticker(name)
    if not isinstance(ticker, dict):
        return None
    forward = ticker.get("index_price") or ticker.get("indexPrice")
    iv = ticker.get("mark_iv") or ticker.get("markIv")
    if forward is not None:
        try:
            forward = float(forward)
        except (TypeError, ValueError):
            forward = spot_price
    else:
        forward = spot_price
    if iv is not None:
        try:
            iv = float(iv)
            # Deribit returns IV as percentage (e.g. 52.66 for 52.66%); use decimal in formulas
            if iv > 2:
                iv = iv / 100.0
        except (TypeError, ValueError):
            iv = None
    return {"forward": forward, "atm_iv": iv, "expiry_ts": expiry_ts}


def fetch_deribit_btc_tight_bull_spreads(
    spot_price: float,
    spread_width: float = 5000.0,
    max_expiries: int = 5,
    instruments: list[dict[str, Any]] | None = None,
    option_book_marks: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """
    Tight bull call spreads: long call K_low, short call K_high (same expiry).
    For each expiry pick two strikes near spot (K_low = round(spot/width)*width, K_high = K_low + width).
    Returns list of {expiry_date, K_low, K_high, cost_usd, max_loss, max_gain, rr_ratio, instrument_low, instrument_high}.
    Pass instruments from a prior get_instruments call to avoid duplicate large downloads.
    Pass option_book_marks from fetch_deribit_btc_option_book_marks() to avoid one large book call per task.
    """
    if instruments is None:
        instruments = fetch_deribit_btc_options_instruments(expired=False)
    calls = [i for i in instruments if i.get("option_type") == "call"]
    if not calls:
        return []
    by_exp: dict[Any, list[Any]] = {}
    for i in calls:
        ts = i.get("expiration_timestamp")
        if ts is None:
            continue
        if ts not in by_exp:
            by_exp[ts] = []
        by_exp[ts].append(i)
    expiries_sorted = sorted(by_exp.keys())[:max_expiries]
    rows: list[dict[str, Any]] = []
    for exp_ts in expiries_sorted:
        list_calls = by_exp[exp_ts]
        strikes = sorted(set(c.get("strike") for c in list_calls if c.get("strike") is not None))
        if len(strikes) < 2:
            continue
        # K_low: strike at or just below spot; K_high: next strike above (tight spread)
        below = [s for s in strikes if s <= spot_price]
        k_low = max(below) if below else min(strikes)
        above = [s for s in strikes if s > k_low]
        k_high = min(above) if above else (k_low + spread_width)
        if k_high - k_low > spread_width * 2:
            continue  # skip if not tight
        inst_low = next((c for c in list_calls if c.get("strike") == k_low), None)
        inst_high = next((c for c in list_calls if c.get("strike") == k_high), None)
        if not inst_low or not inst_high:
            continue
        n_lo = inst_low.get("instrument_name") or ""
        n_hi = inst_high.get("instrument_name") or ""
        if not n_lo or not n_hi:
            continue
        rows.append({
            "exp_ts": exp_ts,
            "k_low": k_low,
            "k_high": k_high,
            "n_lo": n_lo,
            "n_hi": n_hi,
            "instrument_low": n_lo,
            "instrument_high": n_hi,
        })

    marks = option_book_marks if option_book_marks is not None else fetch_deribit_btc_option_book_marks()

    result = []
    for row in rows:
        mark_low = _option_mark_btc_from_book_or_ticker(row["n_lo"], marks)
        mark_high = _option_mark_btc_from_book_or_ticker(row["n_hi"], marks)
        if mark_low is None or mark_high is None:
            continue
        cost_btc = float(mark_low) - float(mark_high)
        if cost_btc <= 0:
            continue
        cost_usd = cost_btc * spot_price  # Deribit option premiums in BTC
        width = row["k_high"] - row["k_low"]
        max_gain = width - cost_usd
        max_loss = cost_usd
        rr = (max_gain / max_loss) if max_loss else 0
        exp_ts = row["exp_ts"]
        result.append({
            "expiry_date": datetime.fromtimestamp(exp_ts / 1000, tz=timezone.utc),
            "K_low": row["k_low"],
            "K_high": row["k_high"],
            "cost_usd": cost_usd,
            "max_loss": max_loss,
            "max_gain": max_gain,
            "rr_ratio": rr,
            "instrument_low": row["instrument_low"],
            "instrument_high": row["instrument_high"],
        })
    return result


def fetch_deribit_spreads_around_predictions(
    btc_questions: list[dict[str, Any]],
    current_spot: float,
    max_questions: int = 5,
    spread_width: float = 5000.0,
    min_target_strike: float = 10000.0,
    instruments: list[dict[str, Any]] | None = None,
    option_book_marks: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """
    Bull call spreads aligned with Polymarket predictions. For each question:
    K_high = target strike, K_low = target - width, expiry = nearest Deribit expiry <= resolution_date (or closest after).
    Skips: already hit (spot > target), odd targets (< min_target_strike).
    Returns list with question info + spread cost, R:R, approx_implied_prob.
    """
    if instruments is None:
        instruments = fetch_deribit_btc_options_instruments(expired=False)
    calls = [i for i in instruments if i.get("option_type") == "call"]
    if not calls:
        return []
    by_exp = {}
    for i in calls:
        ts = i.get("expiration_timestamp")
        if ts is None:
            continue
        if ts not in by_exp:
            by_exp[ts] = []
        by_exp[ts].append(i)
    expiries_ts = sorted(by_exp.keys())
    pending: list[dict[str, Any]] = []
    for q in btc_questions[:max_questions]:
        target = q.get("strike")
        res_str = q.get("resolution_date")
        prob = q.get("yes_probability")
        if target is None or not res_str:
            continue
        if target < min_target_strike:
            continue
        if current_spot >= target:
            continue  # already hit
        try:
            res_ts = int(datetime.strptime(res_str[:10], "%Y-%m-%d").timestamp() * 1000)
        except Exception:
            continue
        # Prefer expiry <= resolution_date; else nearest after
        before = [e for e in expiries_ts if e <= res_ts]
        after = [e for e in expiries_ts if e > res_ts]
        exp_ts = max(before) if before else (min(after) if after else None)
        if exp_ts is None:
            continue
        list_calls = by_exp.get(exp_ts, [])
        strikes = sorted(set(c.get("strike") for c in list_calls if c.get("strike") is not None))
        if len(strikes) < 2:
            continue
        k_high = min((s for s in strikes if s >= target), default=strikes[-1])
        if k_high < target * 0.9:
            continue
        below = [s for s in strikes if s < k_high]
        k_low = max(below) if below else (k_high - spread_width)
        if k_high - k_low > spread_width * 2:
            k_low = max((s for s in strikes if s < k_high), default=k_low)
        inst_low = next((c for c in list_calls if c.get("strike") == k_low), None)
        inst_high = next((c for c in list_calls if c.get("strike") == k_high), None)
        if not inst_low or not inst_high:
            continue
        n_lo = inst_low.get("instrument_name") or ""
        n_hi = inst_high.get("instrument_name") or ""
        if not n_lo or not n_hi:
            continue
        pending.append({
            "q": q,
            "target": target,
            "res_str": res_str,
            "prob": prob,
            "exp_ts": exp_ts,
            "k_low": k_low,
            "k_high": k_high,
            "n_lo": n_lo,
            "n_hi": n_hi,
        })

    marks = option_book_marks if option_book_marks is not None else fetch_deribit_btc_option_book_marks()

    result = []
    for row in pending:
        mark_low = _option_mark_btc_from_book_or_ticker(row["n_lo"], marks)
        mark_high = _option_mark_btc_from_book_or_ticker(row["n_hi"], marks)
        if mark_low is None or mark_high is None:
            continue
        cost_btc = float(mark_low) - float(mark_high)
        if cost_btc <= 0:
            continue
        k_low, k_high = row["k_low"], row["k_high"]
        cost_usd = cost_btc * current_spot  # Deribit option premiums in BTC
        width = k_high - k_low
        max_gain = width - cost_usd
        max_loss = cost_usd
        rr = (max_gain / max_loss) if max_loss else 0
        approx_implied_prob = (cost_usd / width) if width else None
        exp_ts = row["exp_ts"]
        q = row["q"]
        result.append({
            "question": q,
            "target": row["target"],
            "resolution_date": row["res_str"],
            "polymarket_yes_pct": (row["prob"] or 0) * 100,
            "expiry_date": datetime.fromtimestamp(exp_ts / 1000, tz=timezone.utc),
            "K_low": k_low,
            "K_high": k_high,
            "cost_usd": cost_usd,
            "max_loss": max_loss,
            "max_gain": max_gain,
            "rr_ratio": rr,
            "approx_implied_prob_pct": approx_implied_prob * 100 if approx_implied_prob is not None else None,
        })
    return result


def fetch_deribit_btc_options_summary(
    max_tickers: int = 20,
) -> dict[str, Any]:
    """
    Get BTC options list from Deribit, then fetch mark_price for up to max_tickers
    (to respect rate limits). Groups by expiry; returns expiries, counts, and sample rows with mark.
    """
    result = {
        "available": False,
        "expiries": [],
        "total_count": 0,
        "calls_count": 0,
        "puts_count": 0,
        "sample": [],
        "source": "deribit",
    }
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    if not instruments:
        return result

    result["available"] = True
    result["total_count"] = len(instruments)
    result["calls_count"] = sum(1 for i in instruments if i.get("option_type") == "call")
    result["puts_count"] = sum(1 for i in instruments if i.get("option_type") == "put")

    # Unique expirations (timestamp -> date string)
    exp_ts = sorted(set(i.get("expiration_timestamp") for i in instruments if i.get("expiration_timestamp")))
    result["expiries"] = [
        datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        for ts in exp_ts[:15]
    ]

    # Sample: pick one expiry, get first N instruments and fetch tickers (with small delay)
    if not instruments or max_tickers <= 0:
        return result

    # Pick instruments from nearest expiry
    by_exp = {}
    for i in instruments:
        ts = i.get("expiration_timestamp")
        if ts not in by_exp:
            by_exp[ts] = []
        by_exp[ts].append(i)
    nearest_ts = min(by_exp.keys()) if by_exp else None
    sample_instruments = (by_exp.get(nearest_ts) or [])[:max_tickers]

    sample = []
    for i, inst in enumerate(sample_instruments):
        if i > 0:
            time.sleep(0.2)  # gentle rate limit
        ticker = fetch_deribit_ticker(inst.get("instrument_name", ""))
        mark = _ticker_price(ticker)
        sample.append({
            "instrument": inst.get("instrument_name"),
            "strike": inst.get("strike"),
            "type": inst.get("option_type"),
            "expiry_ts": inst.get("expiration_timestamp"),
            "mark_price": mark,
        })
    result["sample"] = sample
    return result
