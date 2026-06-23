"""Display-only curve legend labels for MSOS charts (SSOT — no math here)."""

from __future__ import annotations

# Purple / market reference curve on MSOS display.json is lognormal_reference (forward + ATM IV).
MARKET_VIEW_SHORT = "Market view"
MARKET_VIEW_METHOD = "Black–Scholes lognormal"

BELIEF_VIEW_SHORT = "Your view"
BELIEF_VIEW_METHOD = "Belief lognormal"

PAYOFF_SHORT = "Payoff at expiry"
PAYOFF_METHOD = "Structure P&L"


def curve_legend(short: str, method: str) -> str:
    return f"{short} [{method}]"


def build_curve_display_labels() -> dict[str, str]:
    return {
        "market_legend": curve_legend(MARKET_VIEW_SHORT, MARKET_VIEW_METHOD),
        "belief_legend": curve_legend(BELIEF_VIEW_SHORT, BELIEF_VIEW_METHOD),
        "payoff_legend": curve_legend(PAYOFF_SHORT, PAYOFF_METHOD),
        "market_method": MARKET_VIEW_METHOD,
        "belief_method": BELIEF_VIEW_METHOD,
        "payoff_method": PAYOFF_METHOD,
    }
