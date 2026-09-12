"""Pure market-proposal and hedge-capacity preview calculations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Comparator = Literal["above", "below"]
ReadinessState = Literal["SHAREABLE_DESIGN", "REVIEW_ONLY", "NOT_SAFELY_HEDGEABLE"]
HedgeStatus = Literal["SUPPORTED", "REVIEW_ONLY", "NOT_SAFELY_HEDGEABLE"]

SCHEMA_VERSION = "MarketProposalHedgeCapacityPreviewV0"
REVIEW_STOP = (
    "Preview only. No prediction market, hedge, order, venue submission, "
    "capital reservation, customer outreach, pilot or arbitrage claim is authorized."
)
PREVIEW_WARNING = "PREVIEW ONLY - NO MARKET OR HEDGE HAS BEEN CREATED OR TRADED"
SETTLEMENT_PROVENANCE = [
    "https://support.deribit.com/hc/en-us/articles/29734325712413-Settlement",
    "https://support.deribit.com/hc/en-us/articles/31424939096093-Inverse-Options",
    "https://docs.deribit.com/api-reference/market-data/public-get_instruments",
    "https://docs.deribit.com/api-reference/market-data/public-get_order_book",
    "https://support.deribit.com/hc/en-us/articles/25944746248989-Fees",
]


@dataclass(frozen=True)
class RequestedTerminalEvent:
    underlying: str
    comparator: Comparator
    requested_threshold_usd: float
    selected_expiry_utc: str
    requested_payout_usd: float
    max_depth_levels: int
    max_slippage_bps: float


@dataclass(frozen=True)
class ProposedTerminalContract:
    question: str
    resolution_language: str
    proposed_threshold_usd: float
    threshold_delta_usd: float
    settlement_source: str
    settlement_method: str
    expiry_utc: str
    yes_payout: str = "$1"
    no_payout: str = "$0"


@dataclass(frozen=True)
class ConsumedLevel:
    price_btc: float
    amount: float
    cumulative_amount: float


@dataclass(frozen=True)
class HedgeLeg:
    instrument_name: str
    action: Literal["buy", "sell"]
    option_type: Literal["call", "put"]
    strike: float
    expiry_utc: str
    contract_multiplier: float
    min_trade_amount: float
    settlement_currency: str
    book_timestamp: str
    levels_consumed: list[ConsumedLevel]
    vwap_btc: float | None
    executable_amount: float


@dataclass(frozen=True)
class PayoffRamp:
    lower_strike_usd: float
    upper_strike_usd: float
    binary_threshold_usd: float
    zero_payoff_region: str
    linear_ramp_region: str
    full_payoff_region: str
    maximum_binary_replication_error_usd: float
    ramp_width_usd: float
    ramp_width_pct_of_threshold: float


@dataclass(frozen=True)
class CostStack:
    observed_long_leg_premium_btc: float
    observed_short_leg_proceeds_btc: float
    net_observed_premium_btc: float
    current_index_usd: float
    observed_premium_usd: float
    option_fees_btc: float
    option_fees_usd: float
    legging_reserve_usd: float
    stale_sync_reserve_usd: float
    settlement_currency_basis_reserve_usd: float
    prediction_venue_fees: str
    collateral_requirement: str


@dataclass(frozen=True)
class CapacityLevel:
    level: int
    spread_amount: float
    capacity_usd: float
    long_leg_vwap_btc: float | None
    short_leg_vwap_btc: float | None
    net_premium_btc: float | None


@dataclass(frozen=True)
class HedgeCapacitySide:
    exposure: Literal["YES", "NO"]
    status: HedgeStatus
    legs: list[HedgeLeg]
    strike_width_usd: float
    top_of_book_capacity_usd: float
    policy_capacity_usd: float
    requested_payout_usd: float
    supported_payout_usd: float
    unsupported_payout_usd: float
    synthetic_cost_per_1_usd: float | None
    observed_premium: dict[str, float | str]
    fees: dict[str, float | str]
    reserves: dict[str, float | str]
    payoff_ramp: PayoffRamp | None
    residual_risk: dict[str, float | str]
    capacity_levels: list[CapacityLevel]
    book_snapshot: dict[str, Any]
    flags: list[str]


@dataclass(frozen=True)
class MarketProposalHedgeCapacityPreviewV0:
    schema_version: str
    as_of_utc: str
    requested_event: RequestedTerminalEvent
    proposed_contract: ProposedTerminalContract
    settlement_spec: dict[str, Any]
    threshold_adjustment: dict[str, float]
    requested_payout_usd: float
    yes_hedge: HedgeCapacitySide
    no_hedge: HedgeCapacitySide
    capacity_summary: dict[str, Any]
    cost_stack: dict[str, Any]
    residual_risk: dict[str, Any]
    constraints: list[str]
    unknowns: list[str]
    readiness_state: ReadinessState
    provenance: dict[str, Any]
    review_stop: str = REVIEW_STOP
    preview_warning: str = PREVIEW_WARNING


class MarketProposalError(ValueError):
    """Raised when a preview cannot be constructed from deterministic inputs."""


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_preview_from_fixture(path: Path) -> MarketProposalHedgeCapacityPreviewV0:
    return build_preview(load_fixture(path))


def build_preview(data: dict[str, Any]) -> MarketProposalHedgeCapacityPreviewV0:
    requested = _parse_requested_event(data["requested_event"])
    _validate_requested_event(requested)
    instruments = list(data.get("instruments") or [])
    books = dict(data.get("order_books") or {})
    settlement = dict(data.get("settlement_metadata") or {})
    as_of = str(data.get("as_of_utc") or _utc_now())
    current_index = float(data["index_price_usd"])
    reserve_policy = {
        "legging_reserve_bps": float(data.get("reserve_policy", {}).get("legging_reserve_bps", 15.0)),
        "stale_sync_reserve_bps": float(data.get("reserve_policy", {}).get("stale_sync_reserve_bps", 10.0)),
        "settlement_currency_basis_reserve_bps": float(
            data.get("reserve_policy", {}).get("settlement_currency_basis_reserve_bps", 25.0)
        ),
    }
    proposed_threshold = select_proposed_threshold(
        instruments,
        requested.selected_expiry_utc,
        requested.requested_threshold_usd,
    )
    contract = generate_contract(requested, proposed_threshold, settlement)
    yes_side = build_hedge_side(
        exposure="YES",
        requested=requested,
        proposed_threshold=proposed_threshold,
        instruments=instruments,
        order_books=books,
        current_index_usd=current_index,
        reserve_policy=reserve_policy,
    )
    no_side = build_hedge_side(
        exposure="NO",
        requested=requested,
        proposed_threshold=proposed_threshold,
        instruments=instruments,
        order_books=books,
        current_index_usd=current_index,
        reserve_policy=reserve_policy,
    )
    readiness = decide_readiness(contract, yes_side, no_side)
    supported = max(yes_side.supported_payout_usd, no_side.supported_payout_usd)
    constraints = [
        "Read-only public-data preview; no order entry or account access.",
        "Capacity is a snapshot from displayed book depth, not a guaranteed fill.",
        "Finite vertical spreads create a visible payoff ramp rather than exact binary replication.",
        "BTC inverse options settle premium and exercise value in BTC; preview normalizes terminal payoff to USD.",
    ]
    unknowns = [
        "Prediction venue fees and listing rules are UNKNOWN_NOT_SELECTED in v0.",
        "Customer demand, market-maker interest and legal/terms approval are unknown.",
        "Collateral/margin for short spread legs is account-specific and not reserved.",
    ]
    return MarketProposalHedgeCapacityPreviewV0(
        schema_version=SCHEMA_VERSION,
        as_of_utc=as_of,
        requested_event=requested,
        proposed_contract=contract,
        settlement_spec={
            "expiry_utc": requested.selected_expiry_utc,
            "source": contract.settlement_source,
            "method": contract.settlement_method,
            "settlement_currency": "BTC",
            "currency_basis": "Deribit inverse BTC options quote and settle in BTC; payout display is normalized to USD.",
        },
        threshold_adjustment={
            "requested_threshold_usd": requested.requested_threshold_usd,
            "proposed_threshold_usd": proposed_threshold,
            "threshold_delta_usd": proposed_threshold - requested.requested_threshold_usd,
        },
        requested_payout_usd=requested.requested_payout_usd,
        yes_hedge=yes_side,
        no_hedge=no_side,
        capacity_summary={
            "requested_payout_usd": requested.requested_payout_usd,
            "max_supported_payout_usd": supported,
            "unsupported_remainder_usd": max(0.0, requested.requested_payout_usd - supported),
            "yes_policy_capacity_usd": yes_side.policy_capacity_usd,
            "no_policy_capacity_usd": no_side.policy_capacity_usd,
        },
        cost_stack={"YES": _side_cost_export(yes_side), "NO": _side_cost_export(no_side)},
        residual_risk={"YES": yes_side.residual_risk, "NO": no_side.residual_risk},
        constraints=constraints,
        unknowns=unknowns,
        readiness_state=readiness,
        provenance={
            "data_mode": str(data.get("data_mode") or "fixture"),
            "source_artifact": str(data.get("source_artifact") or ""),
            "deribit_public_api": "public/get_instruments, public/get_order_book, public/ticker",
            "official_specification_references": settlement.get("provenance", SETTLEMENT_PROVENANCE),
            "book_timestamps": _book_timestamps(books),
        },
    )


def select_proposed_threshold(instruments: list[dict[str, Any]], expiry_utc: str, requested_threshold: float) -> float:
    strikes = sorted(
        {
            float(row["strike"])
            for row in instruments
            if _inst_expiry_utc(row) == expiry_utc and row.get("strike") is not None
        }
    )
    if not strikes:
        raise MarketProposalError("No listed strikes for selected expiry")
    return min(strikes, key=lambda strike: (abs(strike - requested_threshold), strike))


def generate_contract(
    requested: RequestedTerminalEvent,
    proposed_threshold_usd: float,
    settlement: dict[str, Any],
) -> ProposedTerminalContract:
    if not settlement.get("settlement_method"):
        raise MarketProposalError("Settlement method provenance is required")
    comparator_text = "strictly above" if requested.comparator == "above" else "strictly below"
    date_text = _human_expiry(requested.selected_expiry_utc)
    question = (
        f"Will the official Deribit BTC delivery price for the option expiry at 08:00 UTC "
        f"on {date_text} be {comparator_text} ${proposed_threshold_usd:,.0f}? YES pays $1 and NO pays $0."
    )
    resolution = (
        f"Resolution uses the official Deribit BTC delivery price for the selected option expiry "
        f"at {requested.selected_expiry_utc}. The delivery price is the 30-minute TWAP of the "
        f"Deribit BTC index from 07:30 to 08:00 UTC, using snapshots every 4 seconds as described "
        f"by the recorded Deribit settlement provenance. YES pays $1 if the delivery price is "
        f"{comparator_text} ${proposed_threshold_usd:,.0f}; otherwise NO pays $1."
    )
    return ProposedTerminalContract(
        question=question,
        resolution_language=resolution,
        proposed_threshold_usd=proposed_threshold_usd,
        threshold_delta_usd=proposed_threshold_usd - requested.requested_threshold_usd,
        settlement_source=str(settlement.get("settlement_source") or "Deribit BTC Index"),
        settlement_method=str(settlement["settlement_method"]),
        expiry_utc=requested.selected_expiry_utc,
    )


def build_hedge_side(
    *,
    exposure: Literal["YES", "NO"],
    requested: RequestedTerminalEvent,
    proposed_threshold: float,
    instruments: list[dict[str, Any]],
    order_books: dict[str, Any],
    current_index_usd: float,
    reserve_policy: dict[str, float],
) -> HedgeCapacitySide:
    option_type = _option_type_for_exposure(requested.comparator, exposure)
    try:
        lower, upper = adjacent_strikes(instruments, requested.selected_expiry_utc, proposed_threshold)
        if option_type == "call":
            long_strike, short_strike = lower, upper
        else:
            long_strike, short_strike = upper, lower
        long_inst = _find_instrument(instruments, requested.selected_expiry_utc, long_strike, option_type)
        short_inst = _find_instrument(instruments, requested.selected_expiry_utc, short_strike, option_type)
        long_leg = _build_leg(long_inst, "buy", order_books, requested)
        short_leg = _build_leg(short_inst, "sell", order_books, requested)
        levels = capacity_ladder(long_leg, short_leg, upper - lower, requested.max_depth_levels)
        policy_amount = min(long_leg.executable_amount, short_leg.executable_amount)
        policy_capacity = policy_amount * (upper - lower) * min(
            long_leg.contract_multiplier,
            short_leg.contract_multiplier,
        )
        top_capacity = levels[0].capacity_usd if levels else 0.0
        supported = min(requested.requested_payout_usd, policy_capacity)
        unsupported = max(0.0, requested.requested_payout_usd - supported)
        cost = compute_cost_stack(
            long_leg=long_leg,
            short_leg=short_leg,
            spread_amount=policy_amount,
            current_index_usd=current_index_usd,
            reserve_policy=reserve_policy,
        )
        gross_cost_usd = (
            cost.observed_premium_usd
            + cost.option_fees_usd
            + cost.legging_reserve_usd
            + cost.stale_sync_reserve_usd
            + cost.settlement_currency_basis_reserve_usd
        )
        synthetic_cost = (gross_cost_usd / policy_capacity) if policy_capacity > 0 else None
        ramp = payoff_ramp(lower, upper, proposed_threshold)
        flags = _leg_validation_flags(long_leg, short_leg, requested)
        status: HedgeStatus = "SUPPORTED" if policy_capacity > 0 and not flags else "REVIEW_ONLY"
        if policy_capacity <= 0:
            flags.append("policy_capacity_below_minimum_executable_size")
            status = "NOT_SAFELY_HEDGEABLE"
        return HedgeCapacitySide(
            exposure=exposure,
            status=status,
            legs=[long_leg, short_leg],
            strike_width_usd=upper - lower,
            top_of_book_capacity_usd=round(top_capacity, 8),
            policy_capacity_usd=round(policy_capacity, 8),
            requested_payout_usd=requested.requested_payout_usd,
            supported_payout_usd=round(supported, 8),
            unsupported_payout_usd=round(unsupported, 8),
            synthetic_cost_per_1_usd=round(synthetic_cost, 8) if synthetic_cost is not None else None,
            observed_premium={
                "net_observed_premium_btc": round(cost.net_observed_premium_btc, 10),
                "observed_premium_usd": round(cost.observed_premium_usd, 8),
                "current_index_usd": current_index_usd,
            },
            fees={
                "option_fees_btc": round(cost.option_fees_btc, 10),
                "option_fees_usd": round(cost.option_fees_usd, 8),
                "prediction_venue_fees": cost.prediction_venue_fees,
            },
            reserves={
                "legging_reserve_usd": round(cost.legging_reserve_usd, 8),
                "stale_sync_reserve_usd": round(cost.stale_sync_reserve_usd, 8),
                "settlement_currency_basis_reserve_usd": round(cost.settlement_currency_basis_reserve_usd, 8),
            },
            payoff_ramp=ramp,
            residual_risk={
                "finite_vertical_spread": "visible ramp; not an exact digital payoff",
                "maximum_binary_replication_error_usd": ramp.maximum_binary_replication_error_usd,
                "ramp_width_usd": ramp.ramp_width_usd,
                "ramp_width_pct_of_threshold": ramp.ramp_width_pct_of_threshold,
                "currency_basis": "Premium and exercise settlement are in BTC; event payout display is USD-normalized.",
            },
            capacity_levels=levels,
            book_snapshot={
                "long_leg_timestamp": long_leg.book_timestamp,
                "short_leg_timestamp": short_leg.book_timestamp,
                "top_of_book_capacity_usd": round(top_capacity, 8),
                "policy_depth_levels": requested.max_depth_levels,
                "policy_slippage_bps": requested.max_slippage_bps,
            },
            flags=flags,
        )
    except MarketProposalError as exc:
        return _unsupported_side(exposure, requested, str(exc))


def adjacent_strikes(
    instruments: list[dict[str, Any]],
    expiry_utc: str,
    threshold: float,
) -> tuple[float, float]:
    strikes = sorted(
        {
            float(row["strike"])
            for row in instruments
            if _inst_expiry_utc(row) == expiry_utc and row.get("strike") is not None
        }
    )
    if threshold in strikes:
        lower_candidates = [strike for strike in strikes if strike < threshold]
        upper_candidates = [threshold]
    else:
        lower_candidates = [strike for strike in strikes if strike <= threshold]
        upper_candidates = [strike for strike in strikes if strike > threshold]
    if not lower_candidates or not upper_candidates:
        raise MarketProposalError("Threshold is outside adjacent listed strikes")
    return max(lower_candidates), min(upper_candidates)


def capacity_ladder(
    long_leg: HedgeLeg,
    short_leg: HedgeLeg,
    strike_width: float,
    max_levels: int,
) -> list[CapacityLevel]:
    rows: list[CapacityLevel] = []
    for level in range(1, max_levels + 1):
        long_rows = long_leg.levels_consumed[:level]
        short_rows = short_leg.levels_consumed[:level]
        if not long_rows or not short_rows:
            continue
        amount = min(long_rows[-1].cumulative_amount, short_rows[-1].cumulative_amount)
        long_vwap = _vwap_for_amount(long_rows, amount)
        short_vwap = _vwap_for_amount(short_rows, amount)
        net = None if long_vwap is None or short_vwap is None else long_vwap - short_vwap
        rows.append(
            CapacityLevel(
                level=level,
                spread_amount=round(amount, 8),
                capacity_usd=round(amount * strike_width, 8),
                long_leg_vwap_btc=round(long_vwap, 10) if long_vwap is not None else None,
                short_leg_vwap_btc=round(short_vwap, 10) if short_vwap is not None else None,
                net_premium_btc=round(net, 10) if net is not None else None,
            )
        )
    return rows


def compute_cost_stack(
    *,
    long_leg: HedgeLeg,
    short_leg: HedgeLeg,
    spread_amount: float,
    current_index_usd: float,
    reserve_policy: dict[str, float],
) -> CostStack:
    long_premium = (long_leg.vwap_btc or 0.0) * spread_amount
    short_proceeds = (short_leg.vwap_btc or 0.0) * spread_amount
    net_btc = long_premium - short_proceeds
    observed_usd = net_btc * current_index_usd
    long_fee = min(0.0003, 0.125 * (long_leg.vwap_btc or 0.0)) * spread_amount
    short_fee = min(0.0003, 0.125 * (short_leg.vwap_btc or 0.0)) * spread_amount
    fees_btc = long_fee + short_fee
    fees_usd = fees_btc * current_index_usd
    return CostStack(
        observed_long_leg_premium_btc=long_premium,
        observed_short_leg_proceeds_btc=short_proceeds,
        net_observed_premium_btc=net_btc,
        current_index_usd=current_index_usd,
        observed_premium_usd=observed_usd,
        option_fees_btc=fees_btc,
        option_fees_usd=fees_usd,
        legging_reserve_usd=observed_usd * reserve_policy["legging_reserve_bps"] / 10000.0,
        stale_sync_reserve_usd=observed_usd * reserve_policy["stale_sync_reserve_bps"] / 10000.0,
        settlement_currency_basis_reserve_usd=observed_usd
        * reserve_policy["settlement_currency_basis_reserve_bps"]
        / 10000.0,
        prediction_venue_fees="UNKNOWN_NOT_SELECTED",
        collateral_requirement="UNKNOWN_ACCOUNT_SPECIFIC_FOR_SHORT_LEG",
    )


def payoff_ramp(lower: float, upper: float, threshold: float) -> PayoffRamp:
    width = upper - lower
    if width <= 0:
        raise MarketProposalError("Strike width must be positive")
    return PayoffRamp(
        lower_strike_usd=lower,
        upper_strike_usd=upper,
        binary_threshold_usd=threshold,
        zero_payoff_region=f"delivery <= ${lower:,.0f}",
        linear_ramp_region=f"${lower:,.0f} < delivery < ${upper:,.0f}",
        full_payoff_region=f"delivery >= ${upper:,.0f}",
        maximum_binary_replication_error_usd=round(width, 8),
        ramp_width_usd=round(width, 8),
        ramp_width_pct_of_threshold=round(width / threshold * 100.0, 8),
    )


def decide_readiness(
    contract: ProposedTerminalContract,
    yes_side: HedgeCapacitySide,
    no_side: HedgeCapacitySide,
) -> ReadinessState:
    if not contract.question or not contract.resolution_language:
        return "NOT_SAFELY_HEDGEABLE"
    if yes_side.status == "SUPPORTED" or no_side.status == "SUPPORTED":
        return "SHAREABLE_DESIGN"
    if yes_side.status == "REVIEW_ONLY" or no_side.status == "REVIEW_ONLY":
        return "REVIEW_ONLY"
    return "NOT_SAFELY_HEDGEABLE"


def to_dict(preview: MarketProposalHedgeCapacityPreviewV0) -> dict[str, Any]:
    return asdict(preview)


def export_json(preview: MarketProposalHedgeCapacityPreviewV0, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_dict(preview), indent=2, sort_keys=True), encoding="utf-8")
    return path


def export_markdown(preview: MarketProposalHedgeCapacityPreviewV0, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(preview), encoding="utf-8")
    return path


def render_markdown(preview: MarketProposalHedgeCapacityPreviewV0) -> str:
    lines = [
        "# Market Proposal + Hedge Capacity Preview v0",
        "",
        f"**Readiness:** `{preview.readiness_state}`",
        f"**As of:** {preview.as_of_utc}",
        "",
        f"**{preview.preview_warning}**",
        "",
        "## Proposed Question",
        preview.proposed_contract.question,
        "",
        "## Resolution",
        preview.proposed_contract.resolution_language,
        "",
        "## Thresholds",
        f"- Requested threshold: ${preview.threshold_adjustment['requested_threshold_usd']:,.0f}",
        f"- Proposed listed-strike threshold: ${preview.threshold_adjustment['proposed_threshold_usd']:,.0f}",
        f"- Delta: ${preview.threshold_adjustment['threshold_delta_usd']:,.0f}",
        "",
        "## Requested And Supported Payout",
        f"- Requested maximum event payout: ${preview.requested_payout_usd:,.2f}",
        f"- YES hedge supported payout: ${preview.yes_hedge.supported_payout_usd:,.2f}",
        f"- NO hedge supported payout: ${preview.no_hedge.supported_payout_usd:,.2f}",
        f"- Unsupported remainder at best side: ${preview.capacity_summary['unsupported_remainder_usd']:,.2f}",
        "",
        "## Hedge Candidates",
    ]
    for side in (preview.yes_hedge, preview.no_hedge):
        lines.extend(_side_markdown(side))
    lines.extend(
        [
            "## Constraints",
            *[f"- {item}" for item in preview.constraints],
            "",
            "## Unknowns",
            *[f"- {item}" for item in preview.unknowns],
            "",
            "## Provenance",
            f"- Data mode: {preview.provenance.get('data_mode')}",
            f"- Deribit sources: {preview.provenance.get('deribit_public_api')}",
            f"- Settlement references: {', '.join(preview.provenance.get('official_specification_references') or [])}",
            "",
            "## Review Stop",
            preview.review_stop,
            "",
        ]
    )
    return "\n".join(lines)


def _side_markdown(side: HedgeCapacitySide) -> list[str]:
    lines = [
        f"### {side.exposure} Hedge - `{side.status}`",
        f"- Strike width: ${side.strike_width_usd:,.0f}",
        f"- Top-of-book capacity: ${side.top_of_book_capacity_usd:,.2f}",
        f"- Policy capacity: ${side.policy_capacity_usd:,.2f}",
        f"- Synthetic cost per $1 maximum payout: {side.synthetic_cost_per_1_usd}",
        f"- Unsupported requested payout: ${side.unsupported_payout_usd:,.2f}",
    ]
    for leg in side.legs:
        lines.append(
            f"- {leg.action.upper()} {leg.instrument_name} ({leg.option_type}, strike ${leg.strike:,.0f}) "
            f"using {'asks' if leg.action == 'buy' else 'bids'}"
        )
    if side.payoff_ramp:
        lines.extend(
            [
                f"- Payoff ramp: {side.payoff_ramp.linear_ramp_region}",
                f"- Maximum local mismatch: ${side.payoff_ramp.maximum_binary_replication_error_usd:,.2f}",
            ]
        )
    if side.flags:
        lines.append(f"- Flags: {', '.join(side.flags)}")
    lines.append("")
    return lines


def _parse_requested_event(row: dict[str, Any]) -> RequestedTerminalEvent:
    return RequestedTerminalEvent(
        underlying=str(row["underlying"]).upper(),
        comparator=str(row["comparator"]).lower(),  # type: ignore[arg-type]
        requested_threshold_usd=float(row["requested_threshold_usd"]),
        selected_expiry_utc=str(row["selected_expiry_utc"]),
        requested_payout_usd=float(row["requested_payout_usd"]),
        max_depth_levels=int(row["max_depth_levels"]),
        max_slippage_bps=float(row["max_slippage_bps"]),
    )


def _validate_requested_event(event: RequestedTerminalEvent) -> None:
    if event.underlying != "BTC":
        raise MarketProposalError("v0 supports BTC only")
    if event.comparator not in {"above", "below"}:
        raise MarketProposalError("Comparator must be above or below")
    if event.requested_threshold_usd <= 0 or event.requested_payout_usd <= 0:
        raise MarketProposalError("Threshold and payout must be positive")
    if event.max_depth_levels <= 0:
        raise MarketProposalError("max_depth_levels must be positive")


def _option_type_for_exposure(comparator: Comparator, exposure: Literal["YES", "NO"]) -> Literal["call", "put"]:
    if comparator == "above":
        return "call" if exposure == "YES" else "put"
    return "put" if exposure == "YES" else "call"


def _find_instrument(
    instruments: list[dict[str, Any]],
    expiry_utc: str,
    strike: float,
    option_type: str,
) -> dict[str, Any]:
    for row in instruments:
        if (
            _inst_expiry_utc(row) == expiry_utc
            and float(row.get("strike") or -1) == strike
            and row.get("option_type") == option_type
        ):
            return row
    raise MarketProposalError(f"Missing {option_type} instrument at strike {strike}")


def _build_leg(
    instrument: dict[str, Any],
    action: Literal["buy", "sell"],
    order_books: dict[str, Any],
    requested: RequestedTerminalEvent,
) -> HedgeLeg:
    name = str(instrument["instrument_name"])
    book = order_books.get(name)
    if not isinstance(book, dict):
        raise MarketProposalError(f"Missing order book for {name}")
    side_name = "asks" if action == "buy" else "bids"
    levels = _consume_levels(
        list(book.get(side_name) or []),
        action=action,
        max_depth_levels=requested.max_depth_levels,
        max_slippage_bps=requested.max_slippage_bps,
    )
    if not levels:
        raise MarketProposalError(f"Missing executable {side_name} for {name}")
    best_bid = _first_price(book.get("bids"))
    best_ask = _first_price(book.get("asks"))
    if best_bid is not None and best_ask is not None and best_bid >= best_ask:
        raise MarketProposalError(f"Crossed or locked book for {name}")
    amount = levels[-1].cumulative_amount
    return HedgeLeg(
        instrument_name=name,
        action=action,
        option_type=str(instrument["option_type"]),  # type: ignore[arg-type]
        strike=float(instrument["strike"]),
        expiry_utc=_inst_expiry_utc(instrument),
        contract_multiplier=float(instrument.get("contract_size") or 1.0),
        min_trade_amount=float(instrument.get("min_trade_amount") or 0.0),
        settlement_currency=str(instrument.get("settlement_currency") or instrument.get("quote_currency") or "BTC"),
        book_timestamp=_book_timestamp(book),
        levels_consumed=levels,
        vwap_btc=_vwap_for_amount(levels, amount),
        executable_amount=amount,
    )


def _consume_levels(
    raw_levels: list[Any],
    *,
    action: Literal["buy", "sell"],
    max_depth_levels: int,
    max_slippage_bps: float,
) -> list[ConsumedLevel]:
    if not raw_levels:
        return []
    first = float(raw_levels[0][0])
    limit = first * (1.0 + max_slippage_bps / 10000.0) if action == "buy" else first * (
        1.0 - max_slippage_bps / 10000.0
    )
    cumulative = 0.0
    consumed: list[ConsumedLevel] = []
    for raw in raw_levels[:max_depth_levels]:
        price = float(raw[0])
        amount = float(raw[1])
        if action == "buy" and price > limit:
            break
        if action == "sell" and price < limit:
            break
        cumulative += amount
        consumed.append(ConsumedLevel(price_btc=price, amount=amount, cumulative_amount=round(cumulative, 8)))
    return consumed


def _vwap_for_amount(levels: list[ConsumedLevel], amount: float) -> float | None:
    if amount <= 0 or not levels:
        return None
    remaining = amount
    total = 0.0
    for level in levels:
        previous = level.cumulative_amount - level.amount
        available = max(0.0, min(level.amount, amount - previous))
        if available <= 0:
            continue
        take = min(remaining, available)
        total += take * level.price_btc
        remaining -= take
        if remaining <= 1e-9:
            break
    if remaining > 1e-7:
        return None
    return total / amount


def _leg_validation_flags(long_leg: HedgeLeg, short_leg: HedgeLeg, requested: RequestedTerminalEvent) -> list[str]:
    flags: list[str] = []
    amount = min(long_leg.executable_amount, short_leg.executable_amount)
    if amount < max(long_leg.min_trade_amount, short_leg.min_trade_amount):
        flags.append("below_min_trade_amount")
    try:
        t1 = _parse_dt(long_leg.book_timestamp)
        t2 = _parse_dt(short_leg.book_timestamp)
        skew = abs((t1 - t2).total_seconds())
        if skew > 30:
            flags.append("book_timestamp_skew_over_30s")
    except Exception:
        flags.append("book_timestamp_unparseable")
    if long_leg.settlement_currency != "BTC" or short_leg.settlement_currency != "BTC":
        flags.append("non_inverse_btc_settlement_out_of_scope")
    if len(long_leg.levels_consumed) > requested.max_depth_levels or len(short_leg.levels_consumed) > requested.max_depth_levels:
        flags.append("depth_policy_violation")
    return flags


def _unsupported_side(
    exposure: Literal["YES", "NO"],
    requested: RequestedTerminalEvent,
    reason: str,
) -> HedgeCapacitySide:
    return HedgeCapacitySide(
        exposure=exposure,
        status="NOT_SAFELY_HEDGEABLE",
        legs=[],
        strike_width_usd=0.0,
        top_of_book_capacity_usd=0.0,
        policy_capacity_usd=0.0,
        requested_payout_usd=requested.requested_payout_usd,
        supported_payout_usd=0.0,
        unsupported_payout_usd=requested.requested_payout_usd,
        synthetic_cost_per_1_usd=None,
        observed_premium={},
        fees={"prediction_venue_fees": "UNKNOWN_NOT_SELECTED"},
        reserves={},
        payoff_ramp=None,
        residual_risk={"reason": reason},
        capacity_levels=[],
        book_snapshot={},
        flags=[reason],
    )


def _side_cost_export(side: HedgeCapacitySide) -> dict[str, Any]:
    return {
        "observed_premium": side.observed_premium,
        "fees": side.fees,
        "reserves": side.reserves,
        "synthetic_cost_per_1_usd": side.synthetic_cost_per_1_usd,
    }


def _inst_expiry_utc(row: dict[str, Any]) -> str:
    if row.get("expiry_utc"):
        return str(row["expiry_utc"])
    ts = row.get("expiration_timestamp")
    if ts is None:
        raise MarketProposalError("Instrument missing expiration timestamp")
    return datetime.fromtimestamp(float(ts) / 1000.0, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _book_timestamp(book: dict[str, Any]) -> str:
    if book.get("timestamp_utc"):
        return str(book["timestamp_utc"])
    ts = book.get("timestamp")
    if ts is not None:
        return datetime.fromtimestamp(float(ts) / 1000.0, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )
    return _utc_now()


def _book_timestamps(books: dict[str, Any]) -> dict[str, str]:
    return {name: _book_timestamp(book) for name, book in books.items() if isinstance(book, dict)}


def _first_price(levels: Any) -> float | None:
    if not levels:
        return None
    try:
        return float(levels[0][0])
    except (TypeError, ValueError, IndexError):
        return None


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _human_expiry(value: str) -> str:
    return _parse_dt(value).strftime("%Y-%m-%d")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
