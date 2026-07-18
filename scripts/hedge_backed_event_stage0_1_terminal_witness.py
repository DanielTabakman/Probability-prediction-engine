"""Stage 0.1 terminal BTC Polymarket/Deribit availability witness.

Research-only public-data collector. It fetches Polymarket Gamma market metadata,
Polymarket CLOB books, and Deribit public option metadata/order books. It never
touches accounts, wallets, signing, custody, treasury, or order-entry endpoints.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.fetch_deribit import DERIBIT_BASE, fetch_deribit_btc_options_instruments

GAMMA_MARKETS_URL = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK_URL = "https://clob.polymarket.com/book"
DEFAULT_OUT_ROOT = ROOT / "artifacts" / "hedge_backed_event_liquidity" / "terminal_availability"

SEARCH_TERMS = (
    "Bitcoin",
    "BTC",
    "Bitcoin price",
    "BTC price",
    "Bitcoin above",
    "Bitcoin below",
    "BTC above",
    "BTC below",
    "Bitcoin reach",
    "Bitcoin hit",
    "Bitcoin dip",
)

REJECT_PATTERNS = {
    "touch_or_path_dependent": re.compile(
        r"\b(reach|reaches|reached|hit|hits|break|breaks|touch|touches|dip|dips|"
        r"any point|at any point|intraday|before the deadline|prior to)\b|"
        r"\b(?:candle|daily|weekly|monthly)\s+(?:high|low)\b|\b(?:high|low)\s+price\b",
        re.I,
    ),
    "conditional_or_fallback": re.compile(
        r"\b(if neither|50-50|50/50|fallback|otherwise.*(?:void|split)|conditional)\b",
        re.I | re.S,
    ),
    "scalar_or_range": re.compile(r"\b(what price|between|range|or more|or less|close between)\b", re.I),
}

PRICE_RE = re.compile(r"\$(\d+(?:,\d{3})*(?:\.\d+)?)(\s*[kKmM])?\b")
BTC_RE = re.compile(r"\b(bitcoin|btc)\b|\$btc\b", re.I)
SECONDARY_UNDERLYING_RE = re.compile(r"\b(ethereum|eth|solana|sol|gta|etf|ipo|stock|trump)\b", re.I)
ABOVE_RE = re.compile(r"\b(above|greater than|higher than|at or above|equal to or greater than)\b", re.I)
BELOW_RE = re.compile(r"\b(below|less than|lower than|at or below|equal to or less than)\b", re.I)
TIMEZONE_RE = re.compile(r"\b(UTC|ET|EST|EDT|CST|CDT|MST|MDT|PST|PDT|GMT)\b", re.I)
DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|"
    r"\d{1,2}/\d{1,2}/\d{2,4})\b",
    re.I,
)
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:AM|PM|am|pm)?|(?:1[0-2]|0?[1-9])\s*(?:AM|PM|am|pm)\b")
ALTERNATIVE_MOMENT_RE = re.compile(
    r"\b(?:at|on|as of)\b.{0,80}\b(?:or|either|alternatively|whichever|earlier|later)\b.{0,80}\b(?:at|on|as of)\b",
    re.I | re.S,
)
SOURCE_RE = re.compile(
    r"\b(Binance|Coinbase|Kraken|Deribit|CME|CF Benchmarks|CoinDesk|Kaiko|"
    r"BTCUSDT|BTC/USDT|BTC/USD|BTC-USD|bitcoin price index|btc price index|index|oracle)\b",
    re.I,
)
VENUE_RE = re.compile(r"\b(Binance|Coinbase|Kraken|Deribit|CME|CF Benchmarks|CoinDesk|Kaiko)\b", re.I)
PAIR_RE = re.compile(r"\b(BTCUSDT|BTC/USDT|BTC/USD|BTC-USD)\b", re.I)
SOURCE_PHRASE_RE = re.compile(
    r"\b((?:Coinbase|Kraken|Binance|Deribit|CME|CF Benchmarks|CoinDesk|Kaiko)"
    r"(?:\s+[A-Z]{2,5}/[A-Z]{2,5}|\s+BTC-USD|\s+BTCUSDT)?"
    r".{0,80}?\b(?:spot price index|price index|index|oracle))\b",
    re.I,
)
INDEX_PHRASE_RE = re.compile(
    r"\b((?:[A-Z][A-Za-z0-9-]*\s+){0,6}(?:BTC/USD|BTC-USD|BTCUSDT|bitcoin|btc)"
    r"(?:\s+[A-Za-z0-9-]+){0,6}\s+(?:spot price index|price index|index|oracle))\b",
    re.I,
)
SOURCE_FALLBACK_RE = re.compile(
    r"\b(?:fallback|backup|secondary|alternate|alternative|if .*?(?:unavailable|fails|not available)|"
    r"otherwise use|will use|may use)\b.{0,120}\b(?:source|index|oracle|Coinbase|Kraken|Binance|Deribit|CME)\b",
    re.I | re.S,
)
CONDITIONAL_SOURCE_RE = re.compile(
    r"\bif\b.{0,120}\b(?:Coinbase|Kraken|Binance|Deribit|CME|index|source|oracle)\b.{0,160}\b(?:otherwise|else|then)\b",
    re.I | re.S,
)
CALCULATION_RE = re.compile(
    r"\b(single|spot|index|published|closing|close|settlement|final)\b.{0,80}\b(price|value|print|level)|"
    r"\b(price|value|print|level)\b.{0,80}\b(at|as of|exactly|published|settlement)\b",
    re.I,
)
YES_NO_PAYOUT_RE = re.compile(
    r"\b(?:yes|\"yes\")\b.{0,80}\$?1(?:\.00)?\b.{0,120}\b(?:no|\"no\")\b.{0,80}\$?0(?:\.00)?\b|"
    r"\b(?:no|\"no\")\b.{0,80}\$?0(?:\.00)?\b.{0,120}\b(?:yes|\"yes\")\b.{0,80}\$?1(?:\.00)?\b",
    re.I | re.S,
)
NONSTANDARD_PAYOUT_RE = re.compile(r"\b(?:yes|no)\b.{0,80}(?:50-50|50/50|\$0\.50|\$0\.5|half|scalar|pro rata)", re.I | re.S)


@dataclass(frozen=True)
class EventContractSpec:
    underlying: str | None
    comparator: str | None
    threshold: float | None
    resolution_timestamp: str | None
    timezone: str | None
    resolution_source_index: str | None
    calculation_method: str | None
    yes_payout: str | None
    no_payout: str | None
    ambiguity_or_fallback_flags: list[str]


@dataclass(frozen=True)
class Classification:
    is_btc_price: bool
    comparator: str | None
    strike: float | None
    terminal_candidate: bool
    decision: str
    reasons: list[str]
    contract_spec: EventContractSpec


def market_text(market: dict[str, Any]) -> str:
    fields = (
        market.get("question"),
        market.get("groupItemTitle"),
        market.get("description"),
        market.get("slug"),
    )
    return "\n".join(str(v or "") for v in fields)


def parse_price_usd(text: str) -> float | None:
    prices = parse_price_usd_values(text)
    return prices[0] if prices else None


def parse_price_usd_values(text: str) -> list[float]:
    prices: list[float] = []
    for match in PRICE_RE.finditer(text):
        parsed = parse_price_match(match)
        if parsed is not None and parsed >= 1_000:
            prices.append(parsed)
    return prices


def parse_price_match(match: re.Match[str]) -> float | None:
    raw = match.group(1).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    suffix = (match.group(2) or "").strip().lower()
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return value


def unique_values(values: list[Any]) -> list[Any]:
    out: list[Any] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def parse_resolution_timestamp(text: str) -> tuple[str | None, str | None, str | None]:
    dates = unique_values([match.group(0).strip() for match in DATE_RE.finditer(text)])
    times = unique_values([normalize_time(match.group(0)) for match in TIME_RE.finditer(text)])
    timezones = unique_values([match.group(0).upper() for match in TIMEZONE_RE.finditer(text)])
    if len(dates) > 1:
        return None, timezones[0] if len(timezones) == 1 else None, "multiple_observation_dates"
    if len(timezones) > 1:
        return None, None, "conflicting_timezones"
    if len(times) > 1:
        return None, timezones[0] if len(timezones) == 1 else None, "multiple_observation_times"
    if ALTERNATIVE_MOMENT_RE.search(text):
        return None, timezones[0] if len(timezones) == 1 else None, "alternative_observation_moments"
    date = dates[0] if dates else None
    time_match = times[0] if times else None
    timezone = timezones[0] if timezones else None
    if date and time_match and timezone:
        return (
            f"{date} {time_match} {timezone}",
            timezone,
            None,
        )
    if date and (not time_match or not timezone):
        return None, timezone, "missing_explicit_time_or_timezone"
    return None, timezone, "missing_explicit_timestamp"


def normalize_time(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().upper())


def parse_source_and_method(text: str) -> tuple[str | None, str | None, list[str]]:
    flags: list[str] = []
    source_phrases = unique_values([normalize_source_phrase(match.group(1)) for match in SOURCE_PHRASE_RE.finditer(text)])
    venues = unique_values([match.group(1).title() for match in VENUE_RE.finditer(text)])
    pairs = unique_values([normalize_pair(match.group(1)) for match in PAIR_RE.finditer(text)])
    index_phrases = unique_values([normalize_source_phrase(match.group(1)) for match in INDEX_PHRASE_RE.finditer(text)])

    if len(venues) > 1:
        flags.append("multiple_or_alternative_resolution_sources")
    if {"Coinbase", "Kraken"}.issubset(set(venues)):
        flags.append("coinbase_or_kraken_alternative_sources")
    if SOURCE_FALLBACK_RE.search(text):
        flags.append("fallback_resolution_source")
    if CONDITIONAL_SOURCE_RE.search(text):
        flags.append("conditional_resolution_sources")
    if len(index_phrases) > 1:
        flags.append("conflicting_named_indexes")

    source = source_phrases[0] if len(source_phrases) == 1 else None
    if source is None and len(venues) == 1 and len(pairs) <= 1:
        source_match = SOURCE_RE.search(text)
        source = source_match.group(0) if source_match else None
    method = CALCULATION_RE.search(text)
    return (source, method.group(0) if method else None, unique_values(flags))


def normalize_pair(value: str) -> str:
    return value.upper().replace("-", "/")


def normalize_source_phrase(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).rstrip(".,;:")


def parse_payout(text: str, market: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    outcomes = [str(o).lower() for o in parse_json_list(market.get("outcomes"))[:2]]
    if outcomes != ["yes", "no"]:
        return None, None, "not_binary_yes_no"
    if NONSTANDARD_PAYOUT_RE.search(text):
        return None, None, "nonstandard_payout_mapping"
    if YES_NO_PAYOUT_RE.search(text):
        return "$1", "$0", None
    return None, None, "missing_explicit_yes_no_payout"


def parse_event_contract_spec(market: dict[str, Any]) -> EventContractSpec:
    text = market_text(market)
    flags: list[str] = []

    underlying = "BTC" if BTC_RE.search(text) else None
    if not underlying:
        flags.append("missing_btc_underlying")
    if SECONDARY_UNDERLYING_RE.search(text):
        flags.append("secondary_non_btc_condition")

    comparator_values = []
    if ABOVE_RE.search(text):
        comparator_values.append("above")
    if BELOW_RE.search(text):
        comparator_values.append("below")
    comparator_values = unique_values(comparator_values)
    comparator = comparator_values[0] if len(comparator_values) == 1 else None
    if len(comparator_values) == 0:
        flags.append("missing_above_below_comparator")
    elif len(comparator_values) > 1:
        flags.append("conflicting_comparators")

    thresholds = unique_values(parse_price_usd_values(text))
    threshold = thresholds[0] if len(thresholds) == 1 else None
    if len(thresholds) == 0:
        flags.append("missing_threshold")
    elif len(thresholds) > 1:
        flags.append("multiple_thresholds")

    resolution_timestamp, timezone, timestamp_flag = parse_resolution_timestamp(text)
    if timestamp_flag:
        flags.append(timestamp_flag)

    source, method, source_flags = parse_source_and_method(text)
    flags.extend(source_flags)
    if not source:
        flags.append("missing_resolution_source_index")
    if not method:
        flags.append("missing_calculation_method")

    yes_payout, no_payout, payout_flag = parse_payout(text, market)
    if payout_flag:
        flags.append(payout_flag)

    for reason, pattern in REJECT_PATTERNS.items():
        if pattern.search(text):
            flags.append(reason)

    return EventContractSpec(
        underlying=underlying,
        comparator=comparator,
        threshold=threshold,
        resolution_timestamp=resolution_timestamp,
        timezone=timezone,
        resolution_source_index=source,
        calculation_method=method,
        yes_payout=yes_payout,
        no_payout=no_payout,
        ambiguity_or_fallback_flags=unique_values(flags),
    )


def classify_market(market: dict[str, Any]) -> Classification:
    spec = parse_event_contract_spec(market)
    reasons = spec.ambiguity_or_fallback_flags
    is_btc_price = bool(spec.underlying == "BTC" and spec.threshold)
    hard_reject_reasons = {
        "touch_or_path_dependent",
        "conditional_or_fallback",
        "scalar_or_range",
        "secondary_non_btc_condition",
        "conflicting_comparators",
        "multiple_thresholds",
        "not_binary_yes_no",
        "nonstandard_payout_mapping",
        "alternative_observation_moments",
        "multiple_observation_times",
        "multiple_observation_dates",
        "conflicting_timezones",
        "multiple_or_alternative_resolution_sources",
        "coinbase_or_kraken_alternative_sources",
        "fallback_resolution_source",
        "conditional_resolution_sources",
        "conflicting_named_indexes",
    }

    terminal = is_btc_price and spec.comparator in {"above", "below"} and not reasons
    if terminal:
        decision = "ELIGIBLE"
    elif any(reason in hard_reject_reasons for reason in reasons):
        decision = "REJECT"
    else:
        decision = "WATCH"

    return Classification(is_btc_price, spec.comparator, spec.threshold, terminal, decision, reasons, spec)


def parse_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def get_json(url: str, *, params: dict[str, Any], timeout: int = 30) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_polymarket_markets(limit: int, include_closed: bool) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    page_size = min(limit, 100)
    for offset in range(0, max(page_size * 10, page_size), page_size):
        params = {"active": "true", "closed": "false", "limit": page_size, "offset": offset}
        data = get_json(GAMMA_MARKETS_URL, params=params)
        if not isinstance(data, list) or not data:
            break
        for market in data:
            market_id = str(market.get("id") or market.get("conditionId") or "")
            if market_id:
                seen.setdefault(market_id, market)
    closed_values = ("false", "true") if include_closed else ("false",)
    active_values = ("true", "false") if include_closed else ("true",)
    for active in active_values:
        for closed in closed_values:
            for term in SEARCH_TERMS:
                params = {"active": active, "closed": closed, "limit": limit, "search": term}
                data = get_json(GAMMA_MARKETS_URL, params=params)
                if not isinstance(data, list):
                    continue
                for market in data:
                    market_id = str(market.get("id") or market.get("conditionId") or "")
                    if market_id:
                        seen.setdefault(market_id, market)
    return list(seen.values())


def fetch_clob_books(market: dict[str, Any], depth: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    token_ids = parse_json_list(market.get("clobTokenIds"))
    outcomes = parse_json_list(market.get("outcomes"))
    for idx, token_id in enumerate(token_ids[:2]):
        label = str(outcomes[idx]) if idx < len(outcomes) else f"outcome_{idx}"
        try:
            book = get_json(CLOB_BOOK_URL, params={"token_id": token_id})
            out[label] = {
                "token_id": token_id,
                "timestamp": book.get("timestamp"),
                "bids": (book.get("bids") or [])[:depth],
                "asks": (book.get("asks") or [])[:depth],
                "book_hash": book.get("hash"),
            }
        except Exception as exc:  # noqa: BLE001 - preserved as research evidence.
            out[label] = {"token_id": token_id, "error": f"{type(exc).__name__}: {exc}"}
    return out


def parse_end_ts(market: dict[str, Any]) -> int | None:
    raw = market.get("endDate") or market.get("endDateIso")
    if not raw:
        return None
    text = str(raw)
    if len(text) == 10:
        text = f"{text}T00:00:00Z"
    try:
        return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError:
        return None


def deribit_public(method: str, params: dict[str, Any]) -> Any:
    data = get_json(f"{DERIBIT_BASE}/public/{method}", params=params)
    if isinstance(data, dict) and "result" in data:
        return data["result"]
    return data


def option_book(instrument_name: str, depth: int) -> dict[str, Any]:
    try:
        book = deribit_public("get_order_book", {"instrument_name": instrument_name, "depth": depth})
        if not isinstance(book, dict):
            return {"instrument_name": instrument_name, "error": "unexpected_non_dict_book"}
        return {
            "instrument_name": instrument_name,
            "timestamp": book.get("timestamp"),
            "best_bid_price": book.get("best_bid_price"),
            "best_ask_price": book.get("best_ask_price"),
            "bids": (book.get("bids") or [])[:depth],
            "asks": (book.get("asks") or [])[:depth],
            "mark_price": book.get("mark_price"),
            "index_price": book.get("index_price"),
        }
    except Exception as exc:  # noqa: BLE001 - preserved as research evidence.
        return {"instrument_name": instrument_name, "error": f"{type(exc).__name__}: {exc}"}


def choose_deribit_legs(
    classification: Classification,
    market: dict[str, Any],
    instruments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not classification.strike:
        return []
    end_ts = parse_end_ts(market)
    now_ts = int(datetime.now(tz=UTC).timestamp() * 1000)
    if end_ts is not None and end_ts < now_ts:
        return []
    opt_type = "put" if classification.comparator == "below" else "call"
    by_exp: dict[int, list[dict[str, Any]]] = {}
    for inst in instruments:
        if inst.get("option_type") != opt_type:
            continue
        exp = inst.get("expiration_timestamp")
        if exp is None:
            continue
        by_exp.setdefault(int(exp), []).append(inst)
    if not by_exp:
        return []
    expiries = sorted(by_exp)
    exp = min(expiries, key=lambda ts: abs(ts - end_ts)) if end_ts else expiries[0]
    legs_for_exp = by_exp[exp]
    strikes = sorted({float(i["strike"]) for i in legs_for_exp if i.get("strike") is not None})
    if len(strikes) < 2:
        return []
    strike = float(classification.strike)
    if strike < strikes[0] or strike > strikes[-1]:
        return []
    lower = max((s for s in strikes if s <= strike), default=strikes[0])
    upper = min((s for s in strikes if s >= strike), default=strikes[-1])
    if lower == upper:
        idx = strikes.index(lower)
        if idx > 0 and (idx == len(strikes) - 1 or abs(strikes[idx - 1] - strike) <= abs(strikes[idx + 1] - strike)):
            lower = strikes[idx - 1]
        elif idx < len(strikes) - 1:
            upper = strikes[idx + 1]
    chosen_strikes = sorted({lower, upper})
    out = []
    for chosen in chosen_strikes:
        inst = next((i for i in legs_for_exp if float(i.get("strike") or -1) == chosen), None)
        if inst:
            out.append(inst)
    return out


def compact_market(market: dict[str, Any], classification: Classification, clob_depth: int) -> dict[str, Any]:
    token_ids = parse_json_list(market.get("clobTokenIds"))
    source_pointer = f"https://polymarket.com/event/{market.get('slug')}" if market.get("slug") else None
    return {
        "event_id": market.get("eventId") or market.get("event_id"),
        "market_id": market.get("id"),
        "id": market.get("id"),
        "conditionId": market.get("conditionId"),
        "questionID": market.get("questionID"),
        "question_id": market.get("questionID"),
        "slug": market.get("slug"),
        "canonical_source_pointer": source_pointer,
        "question": market.get("question"),
        "description": market.get("description"),
        "resolution_text": market.get("description"),
        "outcomes": parse_json_list(market.get("outcomes")),
        "outcomePrices": parse_json_list(market.get("outcomePrices")),
        "yes_token_id": token_ids[0] if len(token_ids) > 0 else None,
        "no_token_id": token_ids[1] if len(token_ids) > 1 else None,
        "createdAt": market.get("createdAt") or market.get("created_at"),
        "closeTime": market.get("closeTime") or market.get("closeDate"),
        "resolutionDate": market.get("resolutionDate") or market.get("resolvedAt"),
        "endDate": market.get("endDate"),
        "endDateIso": market.get("endDateIso"),
        "deadline": classification.contract_spec.resolution_timestamp or market.get("endDate"),
        "deadline_timezone": classification.contract_spec.timezone,
        "resolution_source_index": classification.contract_spec.resolution_source_index,
        "calculation_method": classification.contract_spec.calculation_method,
        "payout_mapping": {
            "YES": classification.contract_spec.yes_payout,
            "NO": classification.contract_spec.no_payout,
            "denomination": "USDC" if classification.contract_spec.yes_payout == "$1" else None,
        },
        "active": market.get("active"),
        "closed": market.get("closed"),
        "acceptingOrders": market.get("acceptingOrders"),
        "bestBid": market.get("bestBid"),
        "bestAsk": market.get("bestAsk"),
        "spread": market.get("spread"),
        "liquidity": market.get("liquidity"),
        "volume": market.get("volume"),
        "orderPriceMinTickSize": market.get("orderPriceMinTickSize"),
        "orderMinSize": market.get("orderMinSize"),
        "makerBaseFee": market.get("makerBaseFee"),
        "takerBaseFee": market.get("takerBaseFee"),
        "feeSchedule": market.get("feeSchedule"),
        "clobTokenIds": token_ids,
        "fetch_timestamps": {
            "gamma_as_of_utc": datetime.now(tz=UTC).isoformat(),
        },
        "classification": asdict(classification),
        "clob_books": fetch_clob_books(market, clob_depth),
    }


def run(limit: int, max_candidates: int, clob_depth: int, deribit_depth: int, include_closed: bool) -> dict[str, Any]:
    as_of = datetime.now(tz=UTC)
    markets = fetch_polymarket_markets(limit=limit, include_closed=include_closed)
    classified = [(m, classify_market(m)) for m in markets]
    btc_price = [(m, c) for m, c in classified if c.is_btc_price]
    btc_price.sort(
        key=lambda item: (
            not bool(item[0].get("active")),
            bool(item[0].get("closed")),
            -(float(item[0].get("liquidity") or 0)),
        )
    )
    candidates = btc_price[:max_candidates]
    instruments = fetch_deribit_btc_options_instruments(expired=False)
    instrument_count = len(instruments)

    frozen = []
    for market, classification in candidates:
        row = compact_market(market, classification, clob_depth)
        legs = choose_deribit_legs(classification, market, instruments) if classification.decision == "ELIGIBLE" else []
        deribit_legs = []
        for leg in legs:
            name = leg.get("instrument_name")
            if not name:
                continue
            deribit_legs.append(
                {
                    "metadata": leg,
                    "order_book": option_book(str(name), deribit_depth),
                    "quote_label": "top_of_book_and_displayed_depth",
                }
            )
            time.sleep(0.15)
        row["deribit_legs"] = deribit_legs
        row["hedge_witness_status"] = (
            "synthetic_not_constructed_semantic_gate_failed"
            if classification.decision != "ELIGIBLE"
            else "eligible_for_manual_synthetic_witness"
        )
        frozen.append(row)

    summary = {
        "as_of_utc": as_of.isoformat(),
        "search_terms": list(SEARCH_TERMS),
        "polymarket_markets_discovered": len(markets),
        "btc_price_threshold_markets": len(btc_price),
        "active_markets_inspected": sum(1 for m in markets if bool(m.get("active")) and not bool(m.get("closed"))),
        "recent_history_markets_inspected": sum(1 for m in markets if not bool(m.get("active")) or bool(m.get("closed"))),
        "recent_history_lookback": "targeted closed/resolved Gamma search for BTC search terms; report records observed date span and limits",
        "candidates_frozen": len(frozen),
        "qualifying_terminal_count": sum(1 for _m, c in btc_price if c.terminal_candidate),
        "active_qualifying_terminal_count": sum(
            1 for m, c in btc_price if bool(m.get("active")) and not bool(m.get("closed")) and c.terminal_candidate
        ),
        "recent_history_qualifying_terminal_count": sum(
            1 for m, c in btc_price if (not bool(m.get("active")) or bool(m.get("closed"))) and c.terminal_candidate
        ),
        "watch_count": sum(1 for _m, c in btc_price if c.decision == "WATCH"),
        "rejected_count": sum(1 for _m, c in btc_price if c.decision == "REJECT"),
        "deribit_btc_option_instruments": instrument_count,
        "deribit_probe_label": "data_availability_only_not_hedge_compilation",
        "quote_labels": {
            "polymarket_bestBid_bestAsk": "Gamma top-of-book fields; CLOB books freeze displayed depth by token",
            "polymarket_outcomePrices": "market estimate, not executable by itself",
            "deribit_order_book": "public get_order_book top-of-book and displayed depth",
            "deribit_mark_price": "mark only; not executable",
        },
    }
    return {"summary": summary, "candidates": frozen}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Stage 0.1 terminal market availability witness")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--max-candidates", type=int, default=20)
    parser.add_argument("--clob-depth", type=int, default=10)
    parser.add_argument("--deribit-depth", type=int, default=5)
    parser.add_argument("--include-closed", action="store_true")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUT_ROOT)
    args = parser.parse_args(argv)

    witness = run(
        limit=args.limit,
        max_candidates=args.max_candidates,
        clob_depth=args.clob_depth,
        deribit_depth=args.deribit_depth,
        include_closed=args.include_closed,
    )
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    args.output_root.mkdir(parents=True, exist_ok=True)
    out = args.output_root / f"stage0_1_terminal_availability_witness_{stamp}.json"
    out.write_text(json.dumps(witness, indent=2, sort_keys=True), encoding="utf-8")
    print(f"hedge_backed_event_stage0_1_terminal_witness: wrote {out}")
    print(json.dumps(witness["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
