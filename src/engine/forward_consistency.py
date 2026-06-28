"""
Put-call parity synthetic forward vs tradable future/perp — research-only consistency check.

Bid/ask only for executable edges; never midpoint for arb comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ForwardConsistencyStatus = Literal[
    "NO_ARB",
    "WATCH",
    "POSSIBLE_ARB",
    "BAD_DATA",
    "NOT_COMPARABLE",
]

ForwardConsistencyDirection = Literal[
    "SELL_FUTURE_BUY_SYNTHETIC",
    "BUY_FUTURE_SELL_SYNTHETIC",
]


@dataclass(frozen=True)
class OptionLegQuote:
    strike: float
    call_bid: float | None
    call_ask: float | None
    put_bid: float | None
    put_ask: float | None
    quote_ts_ms: int | None = None


@dataclass(frozen=True)
class FutureLegQuote:
    instrument_name: str
    bid: float | None
    ask: float | None
    expiry_ts_ms: int | None = None
    quote_ts_ms: int | None = None


@dataclass(frozen=True)
class SyntheticForwardRow:
    strike: float
    synthetic_bid: float
    synthetic_ask: float
    width_usd: float
    call_bid: float
    call_ask: float
    put_bid: float
    put_ask: float
    quote_ts_ms: int | None = None


@dataclass(frozen=True)
class ForwardConsistencyConfig:
    max_synthetic_width_usd: float = 750.0
    max_quote_age_ms: int = 180_000
    estimated_cost_bps: float = 10.0
    estimated_cost_floor_usd: float = 30.0
    watch_buffer_usd: float = 25.0


@dataclass
class ForwardConsistencyLeg:
    side: Literal["buy", "sell"]
    instrument_type: Literal["future", "call", "put"]
    label: str


@dataclass
class ForwardConsistencyCheck:
    status: ForwardConsistencyStatus
    direction: ForwardConsistencyDirection | None = None
    best_strike: float | None = None
    synthetic_bid: float | None = None
    synthetic_ask: float | None = None
    synthetic_width_usd: float | None = None
    future_bid: float | None = None
    future_ask: float | None = None
    gross_edge_usd: float | None = None
    estimated_cost_usd: float | None = None
    net_edge_usd: float | None = None
    legs: list[ForwardConsistencyLeg] = field(default_factory=list)
    detail: str = ""


def premium_coin_to_usd(premium_coin: float, forward_usd: float) -> float:
    """Deribit coin-margined option premium → USD (matches distribution export)."""
    return float(premium_coin) * float(forward_usd)


def compute_synthetic_forward_rows(
    quotes: list[OptionLegQuote],
    *,
    premium_in_usd: bool,
    forward_usd: float,
) -> list[SyntheticForwardRow]:
    """Build synthetic forward bid/ask bands per strike from option quotes."""
    rows: list[SyntheticForwardRow] = []
    scale = 1.0 if premium_in_usd else float(forward_usd)

    for q in quotes:
        if (
            q.call_bid is None
            or q.call_ask is None
            or q.put_bid is None
            or q.put_ask is None
        ):
            continue
        if q.call_bid <= 0 or q.call_ask <= 0 or q.put_bid <= 0 or q.put_ask <= 0:
            continue

        call_bid_usd = q.call_bid * scale if not premium_in_usd else q.call_bid
        call_ask_usd = q.call_ask * scale if not premium_in_usd else q.call_ask
        put_bid_usd = q.put_bid * scale if not premium_in_usd else q.put_bid
        put_ask_usd = q.put_ask * scale if not premium_in_usd else q.put_ask

        synthetic_bid = float(q.strike) + call_bid_usd - put_ask_usd
        synthetic_ask = float(q.strike) + call_ask_usd - put_bid_usd
        if synthetic_ask <= synthetic_bid:
            continue

        width = synthetic_ask - synthetic_bid
        rows.append(
            SyntheticForwardRow(
                strike=float(q.strike),
                synthetic_bid=synthetic_bid,
                synthetic_ask=synthetic_ask,
                width_usd=width,
                call_bid=call_bid_usd,
                call_ask=call_ask_usd,
                put_bid=put_bid_usd,
                put_ask=put_ask_usd,
                quote_ts_ms=q.quote_ts_ms,
            )
        )
    return rows


def filter_reliable_synthetic_rows(
    rows: list[SyntheticForwardRow],
    config: ForwardConsistencyConfig,
    *,
    now_ms: int | None = None,
) -> list[SyntheticForwardRow]:
    """Drop wide, stale, or invalid synthetic bands; rank tightest first."""
    kept: list[SyntheticForwardRow] = []
    for row in rows:
        if row.width_usd > config.max_synthetic_width_usd:
            continue
        if now_ms is not None and row.quote_ts_ms is not None:
            age = now_ms - int(row.quote_ts_ms)
            if age > config.max_quote_age_ms:
                continue
        kept.append(row)
    kept.sort(key=lambda r: r.width_usd)
    return kept


def _estimated_cost_usd(forward_ref_usd: float, config: ForwardConsistencyConfig) -> float:
    ref = max(float(forward_ref_usd), 1.0)
    from_bps = ref * float(config.estimated_cost_bps) / 10_000.0
    return max(float(config.estimated_cost_floor_usd), from_bps)


def check_forward_consistency(
    row: SyntheticForwardRow,
    future: FutureLegQuote,
    config: ForwardConsistencyConfig,
) -> ForwardConsistencyCheck:
    """Compare one synthetic forward band to a tradable future/perp quote."""
    if future.bid is None or future.ask is None or future.bid <= 0 or future.ask <= 0:
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            best_strike=row.strike,
            synthetic_bid=row.synthetic_bid,
            synthetic_ask=row.synthetic_ask,
            synthetic_width_usd=row.width_usd,
            detail="Future/perp bid or ask missing or non-positive.",
        )
    if future.ask < future.bid:
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            best_strike=row.strike,
            detail="Future/perp quote crossed (ask < bid).",
        )

    forward_ref = (float(future.bid) + float(future.ask)) / 2.0
    cost = _estimated_cost_usd(forward_ref, config)

    edge_sell_future = float(future.bid) - row.synthetic_ask
    edge_buy_future = row.synthetic_bid - float(future.ask)

    if edge_sell_future >= edge_buy_future:
        gross = edge_sell_future
        direction: ForwardConsistencyDirection = "SELL_FUTURE_BUY_SYNTHETIC"
        legs = [
            ForwardConsistencyLeg(side="sell", instrument_type="future", label="Sell dated future/perp"),
            ForwardConsistencyLeg(side="buy", instrument_type="call", label="Buy call"),
            ForwardConsistencyLeg(side="sell", instrument_type="put", label="Sell put"),
        ]
    else:
        gross = edge_buy_future
        direction = "BUY_FUTURE_SELL_SYNTHETIC"
        legs = [
            ForwardConsistencyLeg(side="buy", instrument_type="future", label="Buy dated future/perp"),
            ForwardConsistencyLeg(side="sell", instrument_type="call", label="Sell call"),
            ForwardConsistencyLeg(side="buy", instrument_type="put", label="Buy put"),
        ]

    net = gross - cost

    future_inside = float(future.bid) >= row.synthetic_bid and float(future.ask) <= row.synthetic_ask

    if net > 0:
        status: ForwardConsistencyStatus = "POSSIBLE_ARB"
    elif gross > 0 and gross <= cost + config.watch_buffer_usd:
        status = "WATCH"
    elif future_inside or gross <= 0:
        status = "NO_ARB"
    else:
        status = "NO_ARB"

    result = ForwardConsistencyCheck(
        status=status,
        direction=direction if status == "POSSIBLE_ARB" else None,
        best_strike=row.strike,
        synthetic_bid=row.synthetic_bid,
        synthetic_ask=row.synthetic_ask,
        synthetic_width_usd=row.width_usd,
        future_bid=float(future.bid),
        future_ask=float(future.ask),
        gross_edge_usd=gross,
        estimated_cost_usd=cost,
        net_edge_usd=net,
        legs=legs if status == "POSSIBLE_ARB" else [],
        detail="",
    )
    return result


def run_forward_consistency_check(
    option_quotes: list[OptionLegQuote],
    future: FutureLegQuote,
    *,
    premium_in_usd: bool,
    forward_usd: float,
    config: ForwardConsistencyConfig | None = None,
    now_ms: int | None = None,
) -> ForwardConsistencyCheck:
    """End-to-end: build rows, filter, pick tightest, compare to future."""
    cfg = config or ForwardConsistencyConfig()
    rows = compute_synthetic_forward_rows(
        option_quotes,
        premium_in_usd=premium_in_usd,
        forward_usd=forward_usd,
    )
    reliable = filter_reliable_synthetic_rows(rows, cfg, now_ms=now_ms)
    if not reliable:
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            detail="No reliable strike pairs with tight synthetic forward (missing quotes or wide bands).",
        )
    return check_forward_consistency(reliable[0], future, cfg)


def check_to_dict(check: ForwardConsistencyCheck) -> dict[str, Any]:
    return {
        "status": check.status,
        "direction": check.direction,
        "best_strike": check.best_strike,
        "synthetic_bid": check.synthetic_bid,
        "synthetic_ask": check.synthetic_ask,
        "synthetic_width_usd": check.synthetic_width_usd,
        "future_bid": check.future_bid,
        "future_ask": check.future_ask,
        "gross_edge_usd": check.gross_edge_usd,
        "estimated_cost_usd": check.estimated_cost_usd,
        "net_edge_usd": check.net_edge_usd,
        "legs": [
            {"side": leg.side, "instrument_type": leg.instrument_type, "label": leg.label}
            for leg in check.legs
        ],
        "detail": check.detail,
    }
