"""
Display labels and tooltips for implied-lab probability methods (legibility only; no math).
Canonical semantics: docs/SEMANTIC_CONTRACTS.md
"""
from __future__ import annotations

# Chart trace names (Plotly legend)
TRACE_MODEL_BELL = "Model bell (lognormal)"
TRACE_OPTIONS_CHAIN = "Options chain (Breeden–Litzenberger)"
TRACE_USER_BELIEF = "Your belief (subjective)"
TRACE_STRATEGY_PAYOFF = "Strategy P&L (exact strikes, this run)"

TRACE_MODEL_BELL_HELP = (
    "Risk-neutral bell from Deribit forward + ATM IV + time to expiry. "
    "Curve height is scaled density (peak → 25% on axis), not “% chance at this price.”"
)
TRACE_OPTIONS_CHAIN_HELP = (
    "Risk-neutral density from call option marks across strikes (Breeden–Litzenberger). "
    "Shows how the options chain prices probability shape. Y-axis is scaled for display."
)
TRACE_USER_BELIEF_HELP = (
    "Your subjective lognormal curve (peak + width you set). "
    "For comparison only — not from the market and not used for cross-market arb."
)

YAXIS_DENSITY_TITLE = "Density (display scale 0–30%)"
YAXIS_DENSITY_HELP = (
    "Taller = more probability mass packed near that price (density). "
    "Not cumulative probability and not “% chance at this exact dollar.”"
)

CUMULATIVE_CAPTION = (
    "Numbers under the axis: cumulative **P(price ≤ X)** from the lognormal model bell only "
    "(not from the orange options-chain curve)."
)

STRATEGY_PAYOFF_YAXIS_TITLE = "Strategy P&L (USD)"

METHOD_GLOSSARY_MARKDOWN = """
**Curve methods on this chart**

| Line | Method | What it means |
|------|--------|----------------|
| **Model bell (lognormal)** | Forward + ATM IV + time | Simple risk-neutral baseline bell |
| **Options chain (B–L)** | Call prices → 2nd derivative | Market-implied shape from the chain |
| **Your belief** | Your peak + width | Subjective overlay — not market data |

**Axis %** — scaled density for display (peak ≈ 25%). **Under-axis %** — real cumulative chance of finishing at or below that price (lognormal only).

**Strategy families** (belief panel) — rule-based *fit classes* from peak/width disagreement; not optimized tickets. **Green payoff line** — exact 4-leg trade from this run’s strikes and marks.
"""

BELIEF_STRATEGY_HOW_CALCULATED_MARKDOWN = """
**How strategy families are chosen**

1. **Your belief curve** — lognormal with peak = belief center and width = σ_ln you set.
2. **Market reference** — orange options-chain density when enough call marks exist; otherwise purple lognormal baseline.
3. **Peak alignment** — compare your peak to the reference modal price; outside tolerance → directional (bullish/bearish) disagreement.
4. **Width band** — compare your σ_ln to ATM-implied σ at this horizon; narrower / wider / similar.
5. **Category** — directional, width/vol, mixed, or aligned from peak + width rules (thresholds in Verification).
6. **Strategy families** — fixed lookup table for that category (e.g. call spread for bullish directional). **Illustrative only** — strikes are symbolic, not optimized from your curve.

**Not the same as:** the **green payoff line** or **Trade ticket** — those use exact K1–K4 strikes and live Deribit marks from this run.
"""

FAMILY_VS_TICKET_CAPTION = (
    "Strategy families below = illustrative *fit* from disagreement shape. "
    "Green chart line + Trade ticket = exact priced structure for this run."
)

# Polymarket / spread table
COL_PREDICTION_MARKET = "Prediction market (direct)"
COL_PREDICTION_MARKET_HELP = "Polymarket Yes price ≈ implied probability of the event."
COL_SPREAD_PROXY = "Options spread proxy (approx)"
COL_SPREAD_PROXY_HELP = (
    "Approx. P(above target) ≈ bull spread cost ÷ (K_high − K_low). "
    "Not the same as the orange options-chain curve on the implied lab chart."
)
COL_LOGNORMAL_ABOVE = "Lognormal P(> target)"
COL_LOGNORMAL_ABOVE_HELP = (
    "1 − CDF(strike) from forward + ATM IV at nearest option expiry. Risk-neutral; approx event match."
)
COL_OPTIONS_INTEGRATED_ABOVE = "Options-chain P(> target)"
COL_OPTIONS_INTEGRATED_ABOVE_HELP = (
    "Integral of Breeden–Litzenberger density above strike on the chart grid. Risk-neutral; approx."
)

FORBIDDEN_PHRASES = (
    "what the market truly believes",
    "recommended trade",
)

# Distribution summary table (on-screen stats; same fields as CSV export)
DIST_SUMMARY_TITLE = "Distribution summary"
DIST_SUMMARY_ANCHOR_ID = "distribution-summary"
DIST_HOW_TO_READ_MARKDOWN = """
**How to read this table**

Each row is one **expiry** and one **method** for terminal BTC price statistics (same numbers as the CSV download).

| Column | Meaning |
|--------|---------|
| **Risk-neutral mean** | Expected terminal price under that distribution |
| **Median (50th %)** | Half of implied outcomes below this price |
| **Lower / upper quartile** | 25th and 75th percentile of terminal price |
| **Implied range width** | Upper quartile minus lower quartile — wider = more uncertainty |
| **Method** | **Model bell (lognormal)** = forward + ATM vol baseline; **Options chain (B–L)** = shape from live call marks |

**Status** — when the options chain cannot be used honestly, the row shows *Skipped* (not enough marks or degenerate fit). Lognormal baseline rows always show computed stats.
"""

DIST_COL_EXPIRY = "Expiry"
DIST_COL_METHOD = "Method"
DIST_COL_MEAN = "Risk-neutral mean"
DIST_COL_Q25 = "Lower quartile"
DIST_COL_Q50 = "Median terminal price (50th %)"
DIST_COL_Q75 = "Upper quartile"
DIST_COL_RANGE = "Implied range width"
DIST_COL_STATUS = "Status"

DIST_LABEL_MEAN_HELP = "Expected terminal price under this distribution"
DIST_LABEL_Q50_HELP = "Half of implied outcomes below this price"
DIST_LABEL_Q25_HELP = "25th percentile of terminal price"
DIST_LABEL_Q75_HELP = "75th percentile of terminal price"
DIST_LABEL_RANGE_HELP = "q75 − q25; wider = more uncertainty"

DIST_METHOD_LOGNORMAL = "Model bell (lognormal)"
DIST_METHOD_LOGNORMAL_HELP = "Forward + ATM vol baseline"
DIST_METHOD_BL = "Options chain (B–L)"
DIST_METHOD_BL_HELP = "Shape from live option marks"

BL_STATUS_SKIPPED_INSUFFICIENT = "Skipped: not enough option marks"
BL_STATUS_SKIPPED_DEGENERATE = "Skipped: could not fit chain density"
BL_STATUS_COMPUTED = "From chain"


def contains_forbidden_phrase(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in FORBIDDEN_PHRASES)
