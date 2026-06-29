"""Exposure path menu — pure types, catalog helpers, and path sorting (v0)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

InstrumentRail = Literal["spot_equity", "listed_options", "etf_proxy", "perp"]
ExposureDirection = Literal["long", "short", "neutral"]
LeverageShape = Literal["none", "defined", "high"]
TimeBound = Literal["none", "dated"]
LiquidityLabel = Literal["high", "medium", "low", "planned"]
TrustBadge = Literal["Live", "Thin chain", "Planned"]
HorizonChip = Literal["any", "3m", "12m"]

EXPOSURE_PATH_KIND = "exposure_paths"
RECOMMENDATION_STATUS = "path_not_recommendation"
FOOTER_COPY = "Paths for comparison only — simulation and research support, not trade recommendations."

EQUITY_OPTION_MULTIPLIER = 100


@dataclass(frozen=True)
class ExposurePathTemplate:
    path_id: str
    instrument_rail: InstrumentRail
    label: str
    direction: ExposureDirection
    headline: str
    capital_shape: str
    leverage: LeverageShape
    time_bound: TimeBound
    liquidity: LiquidityLabel
    sort_group: str
    pros: tuple[str, ...]
    cons: tuple[str, ...]
    recommendation_status: str = RECOMMENDATION_STATUS
    structure: str | None = None
    min_horizon_days: int | None = None
    max_horizon_days: int | None = None
    deep_link_rail: str | None = None
    status: str | None = None


@dataclass
class ExposurePath:
    path_id: str
    instrument_rail: InstrumentRail
    label: str
    direction: ExposureDirection
    headline: str
    capital_shape: str
    leverage: LeverageShape
    time_bound: TimeBound
    liquidity: LiquidityLabel
    trust_badge: TrustBadge
    pros: list[str]
    cons: list[str]
    recommendation_status: str = RECOMMENDATION_STATUS
    cost_hint_usd: float | None = None
    legs: list[dict[str, str]] = field(default_factory=list)
    deep_link: str | None = None
    sort_group: str = ""
    catalog_order: int = 0

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "path_id": self.path_id,
            "instrument_rail": self.instrument_rail,
            "label": self.label,
            "direction": self.direction,
            "headline": self.headline,
            "capital_shape": self.capital_shape,
            "leverage": self.leverage,
            "time_bound": self.time_bound,
            "liquidity": self.liquidity,
            "trust_badge": self.trust_badge,
            "pros": list(self.pros),
            "cons": list(self.cons),
            "recommendation_status": self.recommendation_status,
        }
        if self.cost_hint_usd is not None:
            out["cost_hint_usd"] = round(float(self.cost_hint_usd), 2)
        if self.legs:
            out["legs"] = list(self.legs)
        if self.deep_link:
            out["deep_link"] = self.deep_link
        return out


def parse_path_template(path_id: str, raw: dict[str, Any]) -> ExposurePathTemplate:
    pros = tuple(str(x) for x in (raw.get("pros") or []))
    cons = tuple(str(x) for x in (raw.get("cons") or []))
    min_h = raw.get("min_horizon_days")
    max_h = raw.get("max_horizon_days")
    return ExposurePathTemplate(
        path_id=str(path_id),
        instrument_rail=str(raw.get("instrument_rail") or "spot_equity"),  # type: ignore[arg-type]
        label=str(raw.get("label") or path_id),
        direction=str(raw.get("direction") or "long"),  # type: ignore[arg-type]
        headline=str(raw.get("headline") or ""),
        capital_shape=str(raw.get("capital_shape") or ""),
        leverage=str(raw.get("leverage") or "none"),  # type: ignore[arg-type]
        time_bound=str(raw.get("time_bound") or "none"),  # type: ignore[arg-type]
        liquidity=str(raw.get("liquidity") or "medium"),  # type: ignore[arg-type]
        sort_group=str(raw.get("sort_group") or path_id),
        pros=pros,
        cons=cons,
        recommendation_status=str(raw.get("recommendation_status") or RECOMMENDATION_STATUS),
        structure=(str(raw["structure"]) if raw.get("structure") else None),
        min_horizon_days=(int(min_h) if min_h is not None else None),
        max_horizon_days=(int(max_h) if max_h is not None else None),
        deep_link_rail=(str(raw["deep_link_rail"]) if raw.get("deep_link_rail") else None),
        status=(str(raw["status"]) if raw.get("status") else None),
    )


def template_to_path_shell(
    template: ExposurePathTemplate,
    *,
    catalog_order: int,
    trust_badge: TrustBadge,
) -> ExposurePath:
    deep_link = None
    if template.deep_link_rail == "strategy_lab":
        deep_link = None  # filled by orchestration with asset id
    return ExposurePath(
        path_id=template.path_id,
        instrument_rail=template.instrument_rail,
        label=template.label,
        direction=template.direction,
        headline=template.headline,
        capital_shape=template.capital_shape,
        leverage=template.leverage,
        time_bound=template.time_bound,
        liquidity=template.liquidity,
        trust_badge=trust_badge,
        pros=list(template.pros),
        cons=list(template.cons),
        recommendation_status=template.recommendation_status,
        sort_group=template.sort_group,
        catalog_order=catalog_order,
        deep_link=deep_link,
    )


def build_strategy_lab_deep_link(asset_id: str) -> str:
    return f"/strategy-lab?asset={str(asset_id or '').strip().upper()}"


def sort_group_rank(sort_group: str, sort_order: list[str]) -> int:
    try:
        return sort_order.index(sort_group)
    except ValueError:
        return len(sort_order)


def sort_exposure_paths(paths: list[ExposurePath], *, sort_order: list[str]) -> list[ExposurePath]:
    return sorted(
        paths,
        key=lambda p: (sort_group_rank(p.sort_group, sort_order), p.catalog_order, p.path_id),
    )


def snap_strike(avail_strikes: list[float], target: float) -> float:
    if not avail_strikes:
        return float(target)
    return float(min(avail_strikes, key=lambda k: abs(float(k) - float(target))))


def bull_call_spread_strikes(forward: float, avail_strikes: list[float]) -> tuple[float, float] | None:
    if not avail_strikes or forward <= 0:
        return None
    atm = snap_strike(avail_strikes, forward)
    width_hint = max(2_000.0 if forward >= 1_000 else forward * 0.10, abs(forward) * 0.10)
    short_k = snap_strike(avail_strikes, atm + width_hint)
    if short_k <= atm:
        return None
    return atm, short_k


def select_expiry_ts(
    expiries: list[dict[str, Any]],
    *,
    min_horizon_days: int | None = None,
    max_horizon_days: int | None = None,
    horizon: HorizonChip = "any",
    now_ms: int | None = None,
) -> int | None:
    """Pick one listed expiry matching template horizon constraints."""
    import time

    now = int(now_ms if now_ms is not None else time.time() * 1000)
    rows: list[tuple[int, int]] = []
    for row in expiries:
        ts = row.get("expiration_timestamp") or row.get("expiry_ts")
        if ts is None:
            continue
        try:
            expiry_ts = int(ts)
        except (TypeError, ValueError):
            continue
        days = max(0, int((expiry_ts - now) / 86_400_000))
        rows.append((expiry_ts, days))

    if not rows:
        return None

    min_d = min_horizon_days
    max_d = max_horizon_days
    if horizon == "3m":
        min_d = max(min_d or 0, 60)
        max_d = min(max_d or 200, 200)
    elif horizon == "12m":
        min_d = max(min_d or 0, 270)

    eligible = [
        (ts, days) for ts, days in rows if (min_d is None or days >= min_d) and (max_d is None or days <= max_d)
    ]
    if not eligible:
        eligible = rows

    if min_d is not None and min_d >= 180:
        return max(eligible, key=lambda pair: pair[1])[0]
    if max_d is not None and max_d <= 200:
        target = (min_d or 60 + max_d) // 2
        return min(eligible, key=lambda pair: abs(pair[1] - target))[0]
    return min(eligible, key=lambda pair: pair[0])[0]


def mark_lookup(marks: list[dict[str, Any]]) -> dict[float, float]:
    out: dict[float, float] = {}
    for row in marks:
        strike = row.get("strike")
        mark = row.get("mark_btc")
        if strike is None or mark is None:
            continue
        try:
            out[float(strike)] = float(mark)
        except (TypeError, ValueError):
            continue
    return out


def premium_to_usd(
    premium: float,
    *,
    forward_usd: float,
    premium_in_usd: bool,
    contract_multiplier: float = 1.0,
) -> float:
    unit = float(premium)
    if not premium_in_usd:
        unit *= float(forward_usd)
    return unit * float(contract_multiplier)


def format_leg(
    *,
    asset_id: str,
    instrument: str,
    side: str,
    strike: float,
    expiry_date: str,
) -> dict[str, str]:
    return {
        "side": side.upper(),
        "instrument": f"{asset_id.upper()} {instrument}",
        "strike": f"${strike:,.0f}" if strike >= 100 else f"${strike:,.2f}",
        "tenor": expiry_date,
    }


def resolve_trust_badge(
    *,
    planned: bool,
    thin_chain: bool,
) -> TrustBadge:
    if planned:
        return "Planned"
    if thin_chain:
        return "Thin chain"
    return "Live"


def count_live_paths(paths: list[ExposurePath]) -> int:
    return sum(1 for p in paths if p.trust_badge == "Live")
