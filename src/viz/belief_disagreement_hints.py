"""
Map belief-vs-market peak/width metrics to disagreement categories and
strategy-family hints (intuition only; no strike optimization).

Canonical contracts: structured disagreement + strategy families + one
example structure per family. Markdown is derived from the contract only.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from src.viz.disagreement_thresholds import (
    PEAK_ALIGN_ABS_MIN_USD,
    PEAK_ALIGN_REL_TO_MARKET_PEAK,
    WIDTH_NARROWER_RATIO,
    WIDTH_WIDER_RATIO,
    peak_alignment_tolerance_usd,
)

WidthBand = Literal["narrower", "wider", "similar"]
DisagreementCategoryId = Literal["directional", "width_vol", "mixed", "aligned"]
Direction = Literal["bullish", "bearish", "none"]
MarketReferenceKind = Literal["market-implied", "lognormal baseline"]
RiskExpression = Literal[
    "directional_upside",
    "directional_downside",
    "range_bound",
    "wider_tails",
    "narrower_tails",
    "mixed_direction_and_vol",
]

# Canonical “what view it expresses” labels (derived from risk_expression in the contract).
RISK_EXPRESSION_VIEW: dict[RiskExpression, str] = {
    "directional_upside": "Tilted to upside at expiry vs the reference modal view.",
    "directional_downside": "Tilted to downside at expiry vs the reference modal view.",
    "range_bound": "Range-bound / premium-style shape around a zone (not a naked directional bet).",
    "wider_tails": "More tail mass than the reference (long-vol / wing-heavy intuition).",
    "narrower_tails": "Less tail mass than the reference (short-vol / contained-range intuition).",
    "mixed_direction_and_vol": "Combines a peak disagreement with a width/tail disagreement.",
}

STRIKE_POLICY_ILLUSTRATIVE = (
    "Illustrative only: strikes are not optimized from your belief curve. "
    "Use Exact strikes or Target payoff below with listed option marks."
)

CONTRACT_SCHEMA_VERSION = "1"
StructureKind = Literal["illustrative_pattern"]


class ExampleStructureDict(TypedDict, total=False):
    structure_id: str
    structure_kind: StructureKind
    label: str
    construction_note: str
    why_it_fits: str
    strike_policy: str
    leg_pattern: list[list[str]]  # each [side, instrument, strike_ref], JSON-friendly


class StrategyFamilyDict(TypedDict, total=False):
    family_id: str
    label: str
    fit_rationale: str
    risk_expression: RiskExpression
    tradeoff_failure_mode: str
    recommendation_status: Literal["fit_not_recommendation"]
    example_structure: ExampleStructureDict


class ClassificationTraceDict(TypedDict, total=False):
    """Inputs and thresholds used to derive disagreement category (verification)."""

    center_usd: float
    market_peak_usd: float
    delta_peak_usd: float
    peak_tolerance_usd: float
    peak_aligned: bool
    bullish: bool | None
    sigma_user: float
    sigma_mkt: float
    width_band: WidthBand
    thresholds: dict[str, float]
    category_id: DisagreementCategoryId
    shape_gap_strength: str
    market_reference_kind: MarketReferenceKind


class BeliefDisagreementContract(TypedDict, total=False):
    """Canonical disagreement + strategy families for the implied lab."""

    contract_schema_version: str
    category_id: DisagreementCategoryId
    direction: Direction
    width_band: WidthBand
    shape_gap_strength: str
    market_reference_kind: MarketReferenceKind
    summary_lines: list[str]
    semantic_note: str
    strategy_families: list[StrategyFamilyDict]
    classification_trace: ClassificationTraceDict


def _example(
    structure_id: str,
    label: str,
    construction_note: str,
    why_it_fits: str,
    strike_policy: str = STRIKE_POLICY_ILLUSTRATIVE,
    leg_pattern: list[list[str]] | None = None,
) -> ExampleStructureDict:
    ex: ExampleStructureDict = {
        "structure_id": structure_id,
        "structure_kind": "illustrative_pattern",
        "label": label,
        "construction_note": construction_note,
        "why_it_fits": why_it_fits,
        "strike_policy": strike_policy,
    }
    if leg_pattern:
        ex["leg_pattern"] = leg_pattern
    return ex


def _family(
    family_id: str,
    label: str,
    fit_rationale: str,
    risk_expression: RiskExpression,
    tradeoff_failure_mode: str,
    example: ExampleStructureDict,
) -> StrategyFamilyDict:
    return {
        "family_id": family_id,
        "label": label,
        "fit_rationale": fit_rationale,
        "risk_expression": risk_expression,
        "tradeoff_failure_mode": tradeoff_failure_mode,
        "recommendation_status": "fit_not_recommendation",
        "example_structure": example,
    }


def width_band_from_sigmas(sigma_user: float, sigma_mkt: float) -> WidthBand:
    """Width vs ATM-implied σ using WIDTH_NARROWER_RATIO / WIDTH_WIDER_RATIO (see disagreement_thresholds)."""
    sm = max(sigma_mkt, 1e-12)
    if sigma_user < sm * WIDTH_NARROWER_RATIO:
        return "narrower"
    if sigma_user > sm * WIDTH_WIDER_RATIO:
        return "wider"
    return "similar"


def classify_disagreement(
    *,
    peak_aligned: bool,
    width_band: WidthBand,
) -> DisagreementCategoryId:
    width_similar = width_band == "similar"
    if not peak_aligned and not width_similar:
        return "mixed"
    if not peak_aligned and width_similar:
        return "directional"
    if peak_aligned and not width_similar:
        return "width_vol"
    return "aligned"


SEMANTIC_NOTE = (
    "Strategy families above are **fit classes** to inspect against this disagreement shape — "
    "exploration / decision-support only, **not recommendations or trade signals**."
)


def _families_directional_bullish() -> list[StrategyFamilyDict]:
    return [
        _family(
            "call_vertical_spread",
            "Call vertical spread",
            "Directional upside with defined risk vs naked long call.",
            "directional_upside",
            "Capped upside vs a naked long call; wrong if spot finishes below the spread body.",
            _example(
                "ex_call_vertical",
                "Bull call spread",
                "Long call at lower strike, short call at higher strike (same expiry).",
                "Caps premium while keeping upside bias when your mode is above the "
                "market-implied peak.",
                leg_pattern=[["long", "call", "K_lower"], ["short", "call", "K_higher"]],
            ),
        ),
        _family(
            "call_butterfly",
            "Call butterfly",
            "Concentrates exposure around a zone under your peak.",
            "directional_upside",
            "Pin risk at the short strike; sharp moves away can decay the structure.",
            _example(
                "ex_call_butterfly",
                "Long call butterfly",
                "Long 1× low K call, short 2× mid K calls, long 1× high K call.",
                "Peaks payoff near your modal view when width is similar to the reference.",
            ),
        ),
        _family(
            "broken_wing_bullish_butterfly",
            "Broken-wing bullish butterfly",
            "Directional with one wing extended for skew / asymmetry.",
            "directional_upside",
            "Asymmetry can leave one tail more exposed than a symmetric fly.",
            _example(
                "ex_broken_wing_bull_bf",
                "Broken-wing call butterfly",
                "Asymmetric wing widths so risk is shifted vs a symmetric fly.",
                "Useful when you want upside but not symmetric tail spend.",
            ),
        ),
    ]


def _families_directional_bearish() -> list[StrategyFamilyDict]:
    return [
        _family(
            "put_vertical_spread",
            "Put vertical spread",
            "Directional downside with defined risk.",
            "directional_downside",
            "Capped downside vs a naked long put; wrong if the market rallies away.",
            _example(
                "ex_put_vertical",
                "Bear put spread",
                "Long put at higher strike, short put at lower strike.",
                "Expresses lower mode vs market-implied peak with capped loss.",
                leg_pattern=[["long", "put", "K_higher"], ["short", "put", "K_lower"]],
            ),
        ),
        _family(
            "put_butterfly",
            "Put butterfly",
            "Concentrates exposure around a zone near your peak.",
            "directional_downside",
            "Pin risk at the short strike; large rallies can erode the thesis.",
            _example(
                "ex_put_butterfly",
                "Long put butterfly",
                "Long 1× high K put, short 2× mid K puts, long 1× low K put.",
                "Centers on your downside mode when dispersion is similar to reference.",
            ),
        ),
        _family(
            "bearish_broken_wing_butterfly",
            "Bearish broken-wing butterfly",
            "Directional with asymmetric wing risk.",
            "directional_downside",
            "Asymmetric wings can skew gap risk vs a standard fly.",
            _example(
                "ex_bear_broken_wing_bf",
                "Broken-wing put butterfly",
                "One wing wider than the other to tilt payoff under your mode.",
                "Matches a bearish peak without symmetric premium on both sides.",
            ),
        ),
    ]


def _families_width_wider() -> list[StrategyFamilyDict]:
    return [
        _family(
            "long_strangle_long_wings",
            "Long strangle / long wings",
            "Pays for large moves in either direction.",
            "wider_tails",
            "Bleeds premium if the market stays range-bound.",
            _example(
                "ex_long_strangle",
                "Long strangle",
                "Long OTM put + long OTM call (same expiry).",
                "Fits when you see more tail mass than the market-implied distribution.",
                leg_pattern=[["long", "put", "K_put_OTM"], ["long", "call", "K_call_OTM"]],
            ),
        ),
        _family(
            "long_vol_structures",
            "Long volatility structures",
            "Express a richer tail than ATM σ alone implies.",
            "wider_tails",
            "Long-vega cost: needs realized vol or a move to overcome decay.",
            _example(
                "ex_long_straddle",
                "Long straddle",
                "Long ATM call + long ATM put.",
                "Simple long-vega expression when you disagree on dispersion upward.",
            ),
        ),
        _family(
            "backspread_family",
            "Backspread-type ideas",
            "Asymmetric tail expression (conceptual family).",
            "wider_tails",
            "Ratio structures can have extreme tail risk if sizing is wrong.",
            _example(
                "ex_call_backspread",
                "Call ratio backspread (conceptual)",
                "Short lower-strike calls, long more higher-strike calls (ratio > 1).",
                "Illustrative tail-up shape; sizing must match your risk budget.",
            ),
        ),
    ]


def _families_width_narrower() -> list[StrategyFamilyDict]:
    return [
        _family(
            "short_vol_family",
            "Short-volatility structures",
            "Benefit if realized range stays tight vs implied.",
            "narrower_tails",
            "Tail/gap risk if realized range exceeds short strikes.",
            _example(
                "ex_short_strangle",
                "Short strangle (conceptual)",
                "Short OTM put + short OTM call — premium collection.",
                "Fits a narrower-than-market view; undefined risk must be managed.",
            ),
        ),
        _family(
            "iron_fly_iron_condor",
            "Iron fly / iron condor family",
            "Range-bound premium with capped risk.",
            "range_bound",
            "Wrong if price trends through short strikes (gamma shock).",
            _example(
                "ex_iron_condor",
                "Iron condor",
                "Short put spread + short call spread (four legs, boxed wings).",
                "Expresses stay-within-range vs a wider market-implied distribution.",
            ),
        ),
        _family(
            "condor_spreads",
            "Condor-type spreads",
            "Profit in a band when volatility is rich vs your range view.",
            "range_bound",
            "Still short premium at inner strikes — large trends hurt.",
            _example(
                "ex_condor",
                "Condor",
                "Wider body than a butterfly — two short strikes inner, long wings outer.",
                "Centered range play when your mode aligns but σ is too high.",
            ),
        ),
    ]


def _families_mixed_bullish_wider() -> list[StrategyFamilyDict]:
    return [
        _family(
            "call_spread_call_fly",
            "Call spread / call fly",
            "Directional bias with a volatility-rich view.",
            "mixed_direction_and_vol",
            "Blends two disagreements; can overpay if only one dimension is wrong.",
            _example(
                "ex_bull_call_spread",
                "Bull call spread + tail idea",
                "Vertical for direction; add wings conceptually for tail.",
                "Combines higher mode with wider tails than the reference.",
            ),
        ),
        _family(
            "risk_reversal_style",
            "Risk-reversal–style ideas",
            "Tilt directionally while expressing tail appetite.",
            "mixed_direction_and_vol",
            "Skew and margin context matter; not a one-size hedge.",
            _example(
                "ex_risk_reversal",
                "Risk reversal (conceptual)",
                "Long OTM call, short OTM put (or variant) for skewed exposure.",
                "Illustrative; balances premium vs directional tilt.",
            ),
        ),
        _family(
            "long_wings_strangle",
            "Long wings / strangle-type",
            "Combine upside bias with wider-than-market tails.",
            "mixed_direction_and_vol",
            "Premium stack: needs a move and/or vol to justify cost.",
            _example(
                "ex_long_wings_bull",
                "OTM call ladder + strangle sleeve",
                "Directional call structure plus extra long vega on wings.",
                "Fits mixed: peak higher and σ wider than market-implied.",
            ),
        ),
    ]


def _families_mixed_bullish_narrower() -> list[StrategyFamilyDict]:
    return [
        _family(
            "bull_debit_structures",
            "Bull call spread / debit call structures",
            "Upside with a tighter-than-market range view.",
            "mixed_direction_and_vol",
            "If tails are fatter than you think, short upper leg can cap badly.",
            _example(
                "ex_bull_call_vertical",
                "Bull call spread",
                "Long lower call, short higher call.",
                "Cheaper upside when you also think realized range will be tame.",
            ),
        ),
        _family(
            "call_butterfly_tight",
            "Call butterfly",
            "Peak near your mode with limited tail spend.",
            "mixed_direction_and_vol",
            "Narrow peak: large trend away from body can disappoint.",
            _example(
                "ex_call_fly_tight",
                "Call butterfly",
                "Symmetric fly around your target zone (three strikes).",
                "Concentrates payoff near your mode when you are bullish but expect a tighter range.",
            ),
        ),
        _family(
            "short_iron_condor_careful",
            "Short iron condor (careful)",
            "Range + upside bias — only if you accept short-gamma context.",
            "mixed_direction_and_vol",
            "Short premium: sharp moves through shorts are the main failure mode.",
            _example(
                "ex_skewed_iron_condor",
                "Skewed iron condor (conceptual)",
                "Shift short strikes to favor upside retention vs downside.",
                "Conceptual only; margin and tail risk require care.",
            ),
        ),
    ]


def _families_mixed_bearish_wider() -> list[StrategyFamilyDict]:
    return [
        _family(
            "put_spread_put_fly",
            "Put spread / put fly",
            "Directional downside with a volatility-rich view.",
            "mixed_direction_and_vol",
            "Mixed thesis can be expensive if only downside or only vol is wrong.",
            _example(
                "ex_bear_put_spread",
                "Bear put spread",
                "Long higher put, short lower put.",
                "Downside mode + fat tails vs market-implied.",
            ),
        ),
        _family(
            "bearish_risk_reversal",
            "Bearish risk-reversal–style ideas",
            "Downside tilt with tail expression.",
            "mixed_direction_and_vol",
            "Call leg can hurt in sharp rallies; skew matters.",
            _example(
                "ex_bear_rr",
                "Bearish risk reversal (conceptual)",
                "Long OTM put, short OTM call variant for skew.",
                "Tilts exposure lower while funding part of the put with call premium.",
            ),
        ),
        _family(
            "long_put_wide",
            "Long put + wide structures",
            "Hedge tail while expressing lower mode.",
            "mixed_direction_and_vol",
            "Long premium drag if the market grinds higher calmly.",
            _example(
                "ex_long_put_wings",
                "Long put + long OTM put",
                "Extra downside wing for gap risk.",
                "Layers tail protection when you are bearish and see fatter tails than implied.",
            ),
        ),
    ]


def _families_mixed_bearish_narrower() -> list[StrategyFamilyDict]:
    return [
        _family(
            "put_spread_tight",
            "Put spread / put fly",
            "Downside bias with a tighter-than-market range view.",
            "mixed_direction_and_vol",
            "Rallies hurt; narrow-range view can be wrong if tails realize wide.",
            _example(
                "ex_bear_put_vertical",
                "Bear put spread",
                "Long higher strike put, short lower strike put.",
                "Defined-risk downside when you are bearish but expect a narrower range than implied.",
            ),
        ),
        _family(
            "put_butterfly_tight",
            "Put butterfly",
            "Concentrate risk under your mode.",
            "mixed_direction_and_vol",
            "Sharp rallies away from the body erode the thesis.",
            _example(
                "ex_put_fly_tight",
                "Put butterfly",
                "Symmetric put fly around your downside target (three strikes).",
                "Peak P&L near your downside mode with capped wings.",
            ),
        ),
        _family(
            "bearish_condor_iron_fly",
            "Bearish condor / iron fly (contextual)",
            "Range-bound premium with downside lean — conceptual.",
            "mixed_direction_and_vol",
            "Short premium: large directional moves remain the main risk.",
            _example(
                "ex_bear_iron_fly",
                "Skewed iron fly (conceptual)",
                "Shift body to favor downside path vs upside.",
                "Illustrative premium harvest with downside lean; verify margin and tail risk.",
            ),
        ),
    ]


def _families_aligned(shape_gap_strength: str) -> list[StrategyFamilyDict]:
    gap_note = ""
    if shape_gap_strength == "High":
        gap_note = " Overall PDFs can still differ in detail — see largest gap in the summary."
    return [
        _family(
            "iron_condor_iron_fly_neutral",
            "Iron condor / iron fly family",
            "Neutral range trades when you have no strong tilt vs the reference peak.",
            "range_bound",
            "Short premium: trending markets through the body are painful.",
            _example(
                "ex_iron_condor_neutral",
                "Iron condor",
                "Sell inner strangle, buy outer wings — premium with cap.",
                "Fits low peak/width disagreement at this horizon." + gap_note,
            ),
        ),
        _family(
            "butterfly_neutral",
            "Butterfly (neutral)",
            "Fine-tune exposure around a central strike.",
            "range_bound",
            "Peaked payoff: large moves away from center underperform.",
            _example(
                "ex_neutral_butterfly",
                "Long iron butterfly (conceptual)",
                "Symmetric body around ATM or near forward.",
                "Fine-tunes around the forward when peak/width disagreement is low.",
            ),
        ),
        _family(
            "calendar_diagonal",
            "Calendar / diagonal ideas",
            "Play term structure without a strong directional gap.",
            "range_bound",
            "Term-structure trades carry vega/theta path risk across dates.",
            _example(
                "ex_calendar",
                "Call calendar (conceptual)",
                "Long dated call, short nearer call at nearby strike.",
                "Illustrative term-structure expression; not a strike optimizer.",
            ),
        ),
    ]


def build_classification_trace(
    *,
    center_usd: float,
    market_peak: float,
    sigma_user: float,
    sigma_mkt: float,
    shape_gap_strength: str,
    market_reference_kind: MarketReferenceKind,
    category_id: DisagreementCategoryId,
    bullish: bool | None,
    width_band: WidthBand,
) -> ClassificationTraceDict:
    delta = float(center_usd) - float(market_peak)
    tol = peak_alignment_tolerance_usd(market_peak)
    peak_aligned = abs(delta) < tol
    return {
        "center_usd": float(center_usd),
        "market_peak_usd": float(market_peak),
        "delta_peak_usd": float(delta),
        "peak_tolerance_usd": float(tol),
        "peak_aligned": peak_aligned,
        "bullish": bullish,
        "sigma_user": float(sigma_user),
        "sigma_mkt": float(sigma_mkt),
        "width_band": width_band,
        "thresholds": {
            "peak_align_abs_min_usd": float(PEAK_ALIGN_ABS_MIN_USD),
            "peak_align_rel_to_market_peak": float(PEAK_ALIGN_REL_TO_MARKET_PEAK),
            "width_narrower_ratio": float(WIDTH_NARROWER_RATIO),
            "width_wider_ratio": float(WIDTH_WIDER_RATIO),
        },
        "category_id": category_id,
        "shape_gap_strength": shape_gap_strength,
        "market_reference_kind": market_reference_kind,
    }


def build_belief_disagreement_contract(
    *,
    category_id: DisagreementCategoryId,
    bullish: bool | None,
    width_band: WidthBand,
    shape_gap_strength: str,
    market_reference_kind: MarketReferenceKind,
    classification_trace: ClassificationTraceDict | None = None,
) -> BeliefDisagreementContract:
    """
    Build canonical disagreement + strategy families from classification inputs.
    """
    summary_lines: list[str]
    families: list[StrategyFamilyDict]

    if category_id == "directional":
        b = bool(bullish)
        tilt = "bullish" if b else "bearish"
        title = f"**Hypothesis to inspect:** Directional peak shift ({tilt})"
        if b:
            interp = (
                "You place more probability mass higher than the market-implied modal price, "
                "while your uncertainty width is roughly similar to the market at this horizon."
            )
            families = _families_directional_bullish()
        else:
            interp = (
                "You place more probability mass lower than the market-implied modal price, "
                "while your uncertainty width is roughly similar to the market at this horizon."
            )
            families = _families_directional_bearish()
        summary_lines = [title, "", interp]

    elif category_id == "width_vol":
        if width_band == "wider":
            title = "**Hypothesis to inspect:** Width / volatility (wider than market reference)"
            interp = (
                "Your modal view aligns with the market, but you expect more tail risk than "
                "the market-implied distribution at this horizon."
            )
            families = _families_width_wider()
        else:
            title = "**Hypothesis to inspect:** Width / volatility (narrower than market reference)"
            interp = (
                "Your modal view aligns with the market, but you see less dispersion than "
                "the market-implied distribution at this horizon."
            )
            families = _families_width_narrower()
        summary_lines = [title, "", interp]

    elif category_id == "mixed":
        b = bool(bullish)
        tilt = "bullish" if b else "bearish"
        wlab = "wider" if width_band == "wider" else "narrower"
        title = f"**Hypothesis to inspect:** Mixed peak + width ({tilt} peak, {wlab} than market)"
        interp = (
            "You disagree with the market on **both** where probability peaks and how wide "
            "the distribution is at this horizon."
        )
        summary_lines = [title, "", interp]
        if b and width_band == "wider":
            families = _families_mixed_bullish_wider()
        elif b and width_band == "narrower":
            families = _families_mixed_bullish_narrower()
        elif not b and width_band == "wider":
            families = _families_mixed_bearish_wider()
        else:
            families = _families_mixed_bearish_narrower()

    else:
        title = "**Disagreement type:** Aligned — low disagreement"
        interp = (
            "Your belief peak and width are close to the market reference at this horizon."
        )
        if shape_gap_strength == "High":
            interp += (
                " *Overall PDFs can still differ in detail — see largest gap above.*"
            )
        summary_lines = [title, "", interp]
        families = _families_aligned(shape_gap_strength)

    direction: Direction
    if category_id == "aligned":
        direction = "none"
    elif category_id == "width_vol":
        direction = "none"
    elif bullish is None:
        direction = "none"
    else:
        direction = "bullish" if bullish else "bearish"

    out: BeliefDisagreementContract = {
        "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        "category_id": category_id,
        "direction": direction,
        "width_band": width_band,
        "shape_gap_strength": shape_gap_strength,
        "market_reference_kind": market_reference_kind,
        "summary_lines": summary_lines,
        "semantic_note": SEMANTIC_NOTE,
        "strategy_families": families,
    }
    if classification_trace is not None:
        out["classification_trace"] = classification_trace
    return out


def markdown_from_disagreement_contract(contract: BeliefDisagreementContract) -> str:
    """Render markdown from the canonical contract (single source of truth)."""
    lines: list[str] = []
    lines.extend(contract["summary_lines"])
    lines.append("")
    lines.append("**Strategy families that fit this disagreement**")
    lines.append("")
    lines.append("*Fit is not recommendation.*")
    lines.append("")
    for fam in contract["strategy_families"]:
        ex = fam["example_structure"]
        re = fam["risk_expression"]
        view = RISK_EXPRESSION_VIEW.get(re, str(re))
        tfm = fam.get("tradeoff_failure_mode") or "—"
        lines.append(f"**{fam['label']}**")
        lines.append(f"- **Why it fits:** {fam['fit_rationale']} *Pattern:* {ex['why_it_fits']}")
        lines.append(f"- **View:** {view}")
        lines.append(f"- **Tradeoff / failure mode:** {tfm}")
        lines.append(
            "- **Illustrative only:** "
            f"**{ex['label']}** — {ex['construction_note']} "
            f"(*Strike policy:* {ex.get('strike_policy', STRIKE_POLICY_ILLUSTRATIVE)})"
        )
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(contract["semantic_note"])
    lines.append("")
    lines.append(
        "*These are family labels for intuition only. Strikes and sizing are not optimized from your belief.*"
    )
    return "\n".join(lines)


def build_disagreement_strategy_hints_markdown(
    *,
    category_id: DisagreementCategoryId,
    bullish: bool | None,
    width_band: WidthBand,
    shape_gap_strength: str,
    market_reference_kind: MarketReferenceKind,
) -> str:
    """Backward-compatible: build contract then render markdown."""
    c = build_belief_disagreement_contract(
        category_id=category_id,
        bullish=bullish,
        width_band=width_band,
        shape_gap_strength=shape_gap_strength,
        market_reference_kind=market_reference_kind,
        classification_trace=None,
    )
    return markdown_from_disagreement_contract(c)


def belief_disagreement_hints_payload(
    *,
    center_usd: float,
    market_peak: float,
    sigma_user: float,
    sigma_mkt: float,
    shape_gap_strength: str,
    market_reference_kind: MarketReferenceKind,
) -> dict[str, Any]:
    """Category id, canonical contract, and markdown for chart helpers / UI."""
    delta = center_usd - market_peak
    tol = peak_alignment_tolerance_usd(market_peak)
    peak_aligned = abs(delta) < tol
    wb = width_band_from_sigmas(sigma_user, sigma_mkt)
    cat_id = classify_disagreement(peak_aligned=peak_aligned, width_band=wb)
    bullish: bool | None = None if peak_aligned else (delta > 0.0)
    trace = build_classification_trace(
        center_usd=center_usd,
        market_peak=market_peak,
        sigma_user=sigma_user,
        sigma_mkt=sigma_mkt,
        shape_gap_strength=shape_gap_strength,
        market_reference_kind=market_reference_kind,
        category_id=cat_id,
        bullish=bullish,
        width_band=wb,
    )
    contract = build_belief_disagreement_contract(
        category_id=cat_id,
        bullish=bullish,
        width_band=wb,
        shape_gap_strength=shape_gap_strength,
        market_reference_kind=market_reference_kind,
        classification_trace=trace,
    )
    md = markdown_from_disagreement_contract(contract)
    return {
        "category_id": cat_id,
        "belief_disagreement": contract,
        "markdown": md,
    }


def belief_disagreement_hints_markdown(
    *,
    center_usd: float,
    market_peak: float,
    sigma_user: float,
    sigma_mkt: float,
    shape_gap_strength: str,
    market_reference_kind: MarketReferenceKind,
) -> str:
    """Compute category from peak/width metrics and return the full hints markdown."""
    return belief_disagreement_hints_payload(
        center_usd=center_usd,
        market_peak=market_peak,
        sigma_user=sigma_user,
        sigma_mkt=sigma_mkt,
        shape_gap_strength=shape_gap_strength,
        market_reference_kind=market_reference_kind,
    )["markdown"]


def _digest_peak_line(trace: dict[str, Any]) -> str:
    """Plain scan line: belief mode vs reference modal (uses classification_trace only)."""
    mrk = str(trace.get("market_reference_kind") or "")
    ref_short = (
        "market-implied modal on the chart grid"
        if mrk == "market-implied"
        else "lognormal baseline modal on the chart grid"
    )
    center = float(trace.get("center_usd") or 0.0)
    mpeak = float(trace.get("market_peak_usd") or 0.0)
    if trace.get("peak_aligned"):
        return (
            f"Your belief peak (mode) is **aligned** with the reference modal "
            f"(~${center:,.0f} vs ~${mpeak:,.0f}; {ref_short})."
        )
    bull = trace.get("bullish")
    if bull is True:
        return (
            f"Your belief peak sits **above** the reference modal "
            f"(~${center:,.0f} vs ~${mpeak:,.0f}; {ref_short})."
        )
    if bull is False:
        return (
            f"Your belief peak sits **below** the reference modal "
            f"(~${center:,.0f} vs ~${mpeak:,.0f}; {ref_short})."
        )
    return (
        f"Your belief peak vs reference modal: ~${center:,.0f} vs ~${mpeak:,.0f} "
        f"({ref_short})."
    )


def _digest_width_line(width_band: str | None) -> str:
    wb = str(width_band or "")
    if wb == "wider":
        return (
            "Your uncertainty width at this horizon is **wider** than the "
            "market-implied width (σ at horizon vs ATM-implied σ)."
        )
    if wb == "narrower":
        return (
            "Your uncertainty width at this horizon is **narrower** than the "
            "market-implied width (σ at horizon vs ATM-implied σ)."
        )
    if wb == "similar":
        return (
            "Your uncertainty width at this horizon is **similar** to the "
            "market-implied width (σ at horizon vs ATM-implied σ)."
        )
    return "Your uncertainty width vs the market-implied width: —"


def _digest_main_line(
    *,
    category_id: str | None,
    width_band: str | None,
    bullish: bool | None,
) -> str:
    """Single headline for disagreement category — interpretive, matches contract meanings."""
    cat = str(category_id or "—")
    wb = str(width_band or "")
    prefix = "**Hypothesis (interpretive):** "
    if cat == "aligned":
        return (
            prefix
            + "labeled **aligned** — peak and width are close to the market reference at this horizon "
            "(still a model comparison, not certainty)."
        )
    if cat == "directional":
        tilt = "bullish" if bullish is True else "bearish" if bullish is False else "directional"
        return (
            prefix
            + f"**directional ({tilt})** — peak shifted vs the reference modal while width is similar."
        )
    if cat == "width_vol":
        wlab = "wider tails / dispersion" if wb == "wider" else "narrower / contained range" if wb == "narrower" else "width differs"
        return (
            prefix
            + f"**width / volatility** — peak aligns with the reference modal; your view is {wlab} vs the market-implied distribution."
        )
    if cat == "mixed":
        tilt = "bullish" if bullish is True else "bearish" if bullish is False else "shifted"
        wlab = "wider" if wb == "wider" else "narrower" if wb == "narrower" else "different width"
        return (
            prefix
            + f"**mixed** — a **{tilt}** peak shift **and** **{wlab}** uncertainty vs the market reference."
        )
    return prefix + f"category **{cat}** (see Verification for thresholds)."


def build_disagreement_scan_payload(
    belief_disagreement: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Sprint 004: ordered plain-language digest + fit-family bridge for the glance card.

    Derived only from the canonical belief_disagreement contract and classification_trace.
    No new categories; no recommendation language.
    """
    if not belief_disagreement or not isinstance(belief_disagreement, dict):
        return None
    trace = belief_disagreement.get("classification_trace")
    if not isinstance(trace, dict):
        return None
    families = belief_disagreement.get("strategy_families")
    if not isinstance(families, list):
        families = []

    category_id = belief_disagreement.get("category_id") or trace.get("category_id")
    width_band = trace.get("width_band") or belief_disagreement.get("width_band")
    bullish = trace.get("bullish")

    digest_lines: list[str] = [
        _digest_peak_line(trace),
        _digest_width_line(str(width_band) if width_band is not None else None),
        _digest_main_line(
            category_id=str(category_id) if category_id is not None else None,
            width_band=str(width_band) if width_band is not None else None,
            bullish=bool(bullish) if bullish is not None else None,
        ),
        (
            "*Labels use fixed thresholds on peak and width; they are guides for exploration, "
            "not predictions.*"
        ),
    ]

    fit_bridge_intro = (
        "The **strategy family** rows in the belief section below are **illustrative fit classes** "
        "for this **hypothesis shape**. They are **not** recommendations, **not** ranked, and "
        "**not** trade signals — inspect whether the pattern fits your view."
    )
    fit_bridge_bullets: list[str] = []
    for fam in families:
        if not isinstance(fam, dict):
            continue
        label = str(fam.get("label") or "").strip()
        rationale = str(fam.get("fit_rationale") or "").strip()
        if not label:
            continue
        fit_bridge_bullets.append(
            f"- **{label}:** {rationale}" if rationale else f"- **{label}**"
        )

    return {
        "digest_lines": digest_lines,
        "fit_bridge_intro": fit_bridge_intro,
        "fit_bridge_bullets": fit_bridge_bullets,
    }

