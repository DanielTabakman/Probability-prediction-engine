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
DEFAULT_OUT_ROOT = ROOT / "artifacts" / "hedge_backed_event_liquidity"

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
        r"any point|at any point|high|low|before|by)\b",
        re.I,
    ),
    "conditional_or_fallback": re.compile(r"\b(if neither|50-50|50/50|before gta|conditional)\b", re.I),
    "scalar_or_range": re.compile(r"\b(what price|between|range|or more|or less|close between)\b", re.I),
    "multivariable": re.compile(r"\b(and|or)\b.*\b(ethereum|eth|solana|sol|gta|etf|ipo|stock|trump)\b", re.I),
}

PRICE_RE = re.compile(r"\$(\d+(?:,\d{3})*(?:\.\d+)?)(\s*[kKmM])?\b")
BTC_RE = re.compile(r"\b(bitcoin|btc)\b|\$btc\b", re.I)
ABOVE_RE = re.compile(r"\babove\b", re.I)
BELOW_RE = re.compile(r"\bbelow\b", re.I)
EXPLICIT_TIME_RE = re.compile(
    r"\b(at|as of|on)\b.{0,80}\b("
    r"\d{1,2}:\d{2}|am|pm|utc|et|est|edt|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|"
    r"january|february|march|april|june|july|august|september|october|november|december|"
    r"\d{4}-\d{2}-\d{2})\b",
    re.I,
)


@dataclass(frozen=True)
class Classification:
    is_btc_price: bool
    comparator: str | None
    strike: float | None
    terminal_candidate: bool
    decision: str
    reasons: list[str]


def market_text(market: dict[str, Any]) -> str:
    fields = (
        market.get("question"),
        market.get("groupItemTitle"),
        market.get("description"),
        market.get("slug"),
    )
    return "\n".join(str(v or "") for v in fields)


def parse_price_usd(text: str) -> float | None:
    match = PRICE_RE.search(text)
    if not match:
        return None
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


def classify_market(market: dict[str, Any]) -> Classification:
    text = market_text(market)
    is_btc_price = bool(BTC_RE.search(text) and parse_price_usd(text))
    comparator = "above" if ABOVE_RE.search(text) else ("below" if BELOW_RE.search(text) else None)
    reasons: list[str] = []

    if not is_btc_price:
        return Classification(False, comparator, None, False, "OUT_OF_SCOPE", ["not_btc_price_threshold"])

    for reason, pattern in REJECT_PATTERNS.items():
        if pattern.search(text):
            reasons.append(reason)

    outcomes = parse_json_list(market.get("outcomes"))
    if [str(o).lower() for o in outcomes[:2]] != ["yes", "no"]:
        reasons.append("not_binary_yes_no")

    if comparator not in {"above", "below"}:
        reasons.append("no_terminal_above_below_comparator")

    if comparator in {"above", "below"} and not EXPLICIT_TIME_RE.search(text):
        reasons.append("no_explicit_single_timestamp")

    terminal = is_btc_price and comparator in {"above", "below"} and not reasons
    if terminal:
        decision = "ELIGIBLE_FOR_SCANNER_FEASIBILITY"
    elif is_btc_price and comparator in {"above", "below"} and reasons == ["no_explicit_single_timestamp"]:
        decision = "WATCH_EVIDENCE_INCOMPLETE"
    else:
        decision = "REJECT_NOT_SAFELY_HEDGEABLE"

    return Classification(is_btc_price, comparator, parse_price_usd(text), terminal, decision, reasons)


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
    return {
        "id": market.get("id"),
        "conditionId": market.get("conditionId"),
        "questionID": market.get("questionID"),
        "slug": market.get("slug"),
        "question": market.get("question"),
        "description": market.get("description"),
        "outcomes": parse_json_list(market.get("outcomes")),
        "outcomePrices": parse_json_list(market.get("outcomePrices")),
        "endDate": market.get("endDate"),
        "endDateIso": market.get("endDateIso"),
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
        "clobTokenIds": parse_json_list(market.get("clobTokenIds")),
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
        legs = choose_deribit_legs(classification, market, instruments)
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
            if classification.decision != "ELIGIBLE_FOR_SCANNER_FEASIBILITY"
            else "eligible_for_manual_synthetic_witness"
        )
        frozen.append(row)

    summary = {
        "as_of_utc": as_of.isoformat(),
        "search_terms": list(SEARCH_TERMS),
        "polymarket_markets_discovered": len(markets),
        "btc_price_threshold_markets": len(btc_price),
        "candidates_frozen": len(frozen),
        "qualifying_terminal_count": sum(1 for _m, c in btc_price if c.terminal_candidate),
        "watch_count": sum(1 for _m, c in btc_price if c.decision == "WATCH_EVIDENCE_INCOMPLETE"),
        "rejected_count": sum(1 for _m, c in btc_price if c.decision == "REJECT_NOT_SAFELY_HEDGEABLE"),
        "deribit_btc_option_instruments": instrument_count,
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
