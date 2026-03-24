"""
Sprint 3A: map belief-vs-market peak/width metrics to disagreement categories and
static strategy-family hints (intuition only; no strike optimization).
"""

from __future__ import annotations

from typing import Literal

WidthBand = Literal["narrower", "wider", "similar"]
DisagreementCategoryId = Literal["directional", "width_vol", "mixed", "aligned"]


def width_band_from_sigmas(sigma_user: float, sigma_mkt: float) -> WidthBand:
    """Same bands as implied_lab_derive belief width lines (0.92 / 1.08)."""
    sm = max(sigma_mkt, 1e-12)
    if sigma_user < sm * 0.92:
        return "narrower"
    if sigma_user > sm * 1.08:
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


def _family_block_lines(
    families: list[tuple[str, str]],
) -> list[str]:
    out = ["**Strategy families to explore (hints, not recommendations):**"]
    for name, why in families:
        out.append(f"- **{name}** — {why}")
    out.append("")
    out.append("---")
    out.append("")
    out.append(
        "*These are family labels for intuition only. Strikes and sizing are not optimized from your belief.*"
    )
    return out


def build_disagreement_strategy_hints_markdown(
    *,
    category_id: DisagreementCategoryId,
    bullish: bool | None,
    width_band: WidthBand,
    shape_gap_strength: str,
) -> str:
    """
    Full markdown block for the right-panel belief hints.
    `bullish` is used when category is directional or mixed (peak not aligned); else ignored.
    """
    lines: list[str]

    if category_id == "directional":
        b = bool(bullish)
        tilt = "bullish" if b else "bearish"
        title = f"**Disagreement type:** Directional ({tilt})"
        if b:
            interp = (
                "You place more probability mass higher than the market’s modal price, "
                "while your uncertainty width is roughly similar to the market at this horizon."
            )
            families = [
                ("Call vertical spread", "directional upside with defined risk."),
                ("Call butterfly", "concentrates exposure around a zone under your peak."),
                ("Broken-wing bullish butterfly", "directional with one wing extended for skew."),
            ]
        else:
            interp = (
                "You place more probability mass lower than the market’s modal price, "
                "while your uncertainty width is roughly similar to the market at this horizon."
            )
            families = [
                ("Put vertical spread", "directional downside with defined risk."),
                ("Put butterfly", "concentrates exposure around a zone near your peak."),
                ("Bearish broken-wing butterfly", "directional with asymmetric wing risk."),
            ]
        lines = [title, "", interp, ""] + _family_block_lines(families)

    elif category_id == "width_vol":
        if width_band == "wider":
            title = "**Disagreement type:** Width / volatility disagreement (wider than market)"
            interp = (
                "Your modal view aligns with the market, but you expect more tail risk than "
                "the market-implied distribution at this horizon."
            )
            families = [
                ("Long strangle / long wings", "pays for large moves in either direction."),
                ("Long volatility structures", "express a richer tail than ATM σ implies."),
                ("Backspread-type ideas", "asymmetric tail expression (conceptual family)."),
            ]
        else:
            title = "**Disagreement type:** Width / volatility disagreement (narrower than market)"
            interp = (
                "Your modal view aligns with the market, but you see less dispersion than "
                "the market-implied distribution at this horizon."
            )
            families = [
                ("Short-volatility structures", "benefit if realized range stays tight."),
                ("Iron fly / iron condor family", "range-bound premium with capped risk."),
                ("Condor-type spreads", "profit in a band when volatility is overpriced vs your view."),
            ]
        lines = [title, "", interp, ""] + _family_block_lines(families)

    elif category_id == "mixed":
        b = bool(bullish)
        tilt = "bullish" if b else "bearish"
        wlab = "wider" if width_band == "wider" else "narrower"
        title = f"**Disagreement type:** Mixed ({tilt} peak, {wlab} than market)"
        interp = (
            "You disagree with the market on **both** where probability peaks and how wide "
            "the distribution is at this horizon."
        )
        if b and width_band == "wider":
            families = [
                ("Call spread / call fly", "directional bias with a volatility-rich view."),
                ("Risk-reversal–style ideas", "tilt directionally while expressing tail appetite."),
                ("Long wings / strangle-type", "combine upside bias with a wider-than-market tail."),
            ]
        elif b and width_band == "narrower":
            families = [
                ("Bull call spread / debit call structures", "upside with a tighter-than-market range view."),
                ("Call butterfly", "peak near your mode with limited tail spend."),
                ("Short iron condor (careful)", "range + upside bias — only if you accept short-gamma context."),
            ]
        elif not b and width_band == "wider":
            families = [
                ("Put spread / put fly", "directional downside with a volatility-rich view."),
                ("Bearish risk-reversal–style ideas", "downside tilt with tail expression."),
                ("Long put + wide structures", "hedge tail while expressing lower mode."),
            ]
        else:
            families = [
                ("Put spread / put fly", "downside bias with a tighter-than-market range view."),
                ("Put butterfly", "concentrate risk under your mode."),
                ("Bearish condor / iron fly (contextual)", "range-bound premium with downside lean — conceptual."),
            ]
        lines = [title, "", interp, ""] + _family_block_lines(families)

    else:
        title = "**Disagreement type:** Aligned — low disagreement"
        interp = (
            "Your belief peak and width are close to the market reference at this horizon."
        )
        if shape_gap_strength == "High":
            interp += (
                " *Overall PDFs can still differ in detail — see largest gap above.*"
            )
        families = [
            ("Iron condor / iron fly family", "neutral range trades when you have no strong tilt."),
            ("Butterfly (neutral)", "fine-tune exposure around a central strike."),
            ("Calendar / diagonal ideas", "play term structure without a strong directional gap."),
        ]
        lines = [title, "", interp, ""] + _family_block_lines(families)

    return "\n".join(lines)


def belief_disagreement_hints_payload(
    *,
    center_usd: float,
    market_peak: float,
    sigma_user: float,
    sigma_mkt: float,
    shape_gap_strength: str,
) -> dict[str, str]:
    """Category id plus full hints markdown for chart helpers / UI."""
    delta = center_usd - market_peak
    peak_aligned = abs(delta) < max(1.0, 0.002 * market_peak)
    wb = width_band_from_sigmas(sigma_user, sigma_mkt)
    cat_id = classify_disagreement(peak_aligned=peak_aligned, width_band=wb)
    bullish: bool | None = None if peak_aligned else (delta > 0.0)
    md = build_disagreement_strategy_hints_markdown(
        category_id=cat_id,
        bullish=bullish,
        width_band=wb,
        shape_gap_strength=shape_gap_strength,
    )
    return {"category_id": cat_id, "markdown": md}


def belief_disagreement_hints_markdown(
    *,
    center_usd: float,
    market_peak: float,
    sigma_user: float,
    sigma_mkt: float,
    shape_gap_strength: str,
) -> str:
    """Compute category from peak/width metrics and return the full hints markdown."""
    return belief_disagreement_hints_payload(
        center_usd=center_usd,
        market_peak=market_peak,
        sigma_user=sigma_user,
        sigma_mkt=sigma_mkt,
        shape_gap_strength=shape_gap_strength,
    )["markdown"]
