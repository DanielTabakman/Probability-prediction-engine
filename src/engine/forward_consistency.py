"""
Put-call parity synthetic forward vs tradable future/perp — research-only consistency check.

Bid/ask only for executable edges; never midpoint for arb comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class ForwardConsistencyQualityFlag(str, Enum):
    STALE_QUOTES = "STALE_QUOTES"
    WIDE_SPREAD = "WIDE_SPREAD"
    INSUFFICIENT_DEPTH = "INSUFFICIENT_DEPTH"
    MISSING_LEG = "MISSING_LEG"
    EXPIRY_MISMATCH = "EXPIRY_MISMATCH"

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
    min_reliable_strikes: int = 2
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
    quality_flags: list[ForwardConsistencyQualityFlag] = field(default_factory=list)
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


def _option_leg_missing(q: OptionLegQuote) -> bool:
    return (
        q.call_bid is None
        or q.call_ask is None
        or q.put_bid is None
        or q.put_ask is None
    )


def _quote_is_stale(ts_ms: int | None, *, now_ms: int, max_age_ms: int) -> bool:
    if ts_ms is None:
        return False
    return now_ms - int(ts_ms) > max_age_ms


def derive_quality_flags(
    *,
    option_quotes: list[OptionLegQuote],
    future: FutureLegQuote | None,
    all_rows: list[SyntheticForwardRow],
    reliable_rows: list[SyntheticForwardRow],
    config: ForwardConsistencyConfig,
    now_ms: int | None = None,
    expected_expiry_ts_ms: int | None = None,
) -> list[ForwardConsistencyQualityFlag]:
    """Collect data-quality flags for a forward consistency run."""
    flags: set[ForwardConsistencyQualityFlag] = set()

    if not option_quotes:
        flags.add(ForwardConsistencyQualityFlag.MISSING_LEG)
    else:
        for q in option_quotes:
            if _option_leg_missing(q):
                flags.add(ForwardConsistencyQualityFlag.MISSING_LEG)
                break

    if future is None or future.bid is None or future.ask is None:
        flags.add(ForwardConsistencyQualityFlag.MISSING_LEG)

    if (
        future is not None
        and expected_expiry_ts_ms is not None
        and future.expiry_ts_ms is not None
        and int(future.expiry_ts_ms) != int(expected_expiry_ts_ms)
    ):
        flags.add(ForwardConsistencyQualityFlag.EXPIRY_MISMATCH)

    if now_ms is not None:
        stale = False
        if future is not None and _quote_is_stale(
            future.quote_ts_ms, now_ms=now_ms, max_age_ms=config.max_quote_age_ms
        ):
            stale = True
        if not stale:
            for q in option_quotes:
                if _quote_is_stale(q.quote_ts_ms, now_ms=now_ms, max_age_ms=config.max_quote_age_ms):
                    stale = True
                    break
        if not stale:
            for row in all_rows:
                if _quote_is_stale(row.quote_ts_ms, now_ms=now_ms, max_age_ms=config.max_quote_age_ms):
                    stale = True
                    break
        if stale:
            flags.add(ForwardConsistencyQualityFlag.STALE_QUOTES)

    if all_rows:
        if any(r.width_usd > config.max_synthetic_width_usd for r in all_rows):
            if not reliable_rows or reliable_rows[0].width_usd > config.max_synthetic_width_usd:
                flags.add(ForwardConsistencyQualityFlag.WIDE_SPREAD)

    if len(reliable_rows) < config.min_reliable_strikes:
        flags.add(ForwardConsistencyQualityFlag.INSUFFICIENT_DEPTH)

    return sorted(flags, key=lambda f: f.value)


def _estimated_cost_usd(forward_ref_usd: float, config: ForwardConsistencyConfig) -> float:
    ref = max(float(forward_ref_usd), 1.0)
    from_bps = ref * float(config.estimated_cost_bps) / 10_000.0
    return max(float(config.estimated_cost_floor_usd), from_bps)


def check_forward_consistency(
    row: SyntheticForwardRow,
    future: FutureLegQuote,
    config: ForwardConsistencyConfig,
    *,
    quality_flags: list[ForwardConsistencyQualityFlag] | None = None,
) -> ForwardConsistencyCheck:
    """Compare one synthetic forward band to a tradable future/perp quote."""
    flags = list(quality_flags or [])
    if future.bid is None or future.ask is None or future.bid <= 0 or future.ask <= 0:
        if ForwardConsistencyQualityFlag.MISSING_LEG not in flags:
            flags.append(ForwardConsistencyQualityFlag.MISSING_LEG)
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            best_strike=row.strike,
            synthetic_bid=row.synthetic_bid,
            synthetic_ask=row.synthetic_ask,
            synthetic_width_usd=row.width_usd,
            quality_flags=sorted(set(flags), key=lambda f: f.value),
            detail="Future/perp bid or ask missing or non-positive.",
        )
    if future.ask < future.bid:
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            best_strike=row.strike,
            quality_flags=sorted(set(flags), key=lambda f: f.value),
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
        quality_flags=sorted(set(flags), key=lambda f: f.value),
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
    expected_expiry_ts_ms: int | None = None,
) -> ForwardConsistencyCheck:
    """End-to-end: build rows, filter, pick tightest, compare to future."""
    cfg = config or ForwardConsistencyConfig()
    rows = compute_synthetic_forward_rows(
        option_quotes,
        premium_in_usd=premium_in_usd,
        forward_usd=forward_usd,
    )
    flags = derive_quality_flags(
        option_quotes=option_quotes,
        future=future,
        all_rows=rows,
        reliable_rows=[],
        config=cfg,
        now_ms=now_ms,
        expected_expiry_ts_ms=expected_expiry_ts_ms,
    )
    reliable = filter_reliable_synthetic_rows(rows, cfg, now_ms=now_ms)
    flags = derive_quality_flags(
        option_quotes=option_quotes,
        future=future,
        all_rows=rows,
        reliable_rows=reliable,
        config=cfg,
        now_ms=now_ms,
        expected_expiry_ts_ms=expected_expiry_ts_ms,
    )
    if not reliable:
        return ForwardConsistencyCheck(
            status="BAD_DATA",
            quality_flags=flags,
            detail="No reliable strike pairs with tight synthetic forward (missing quotes or wide bands).",
        )
    return check_forward_consistency(reliable[0], future, cfg, quality_flags=flags)


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
        "quality_flags": [flag.value for flag in check.quality_flags],
        "detail": check.detail,
    }
