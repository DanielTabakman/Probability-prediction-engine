# SEMANTIC CONTRACTS

## Purpose
This file defines the meaning of the main concepts in the product so UI, code, and explanations do not drift apart.

---

## 1. Market-implied pricing distribution
Definition:
A distribution inferred from market prices of options/futures at a given timestamp and expiry.

Important note:
This is **not** the market's pure belief.
It is a **priced / risk-neutral distribution**, affected by supply-demand, volatility pricing, hedging pressure, and market microstructure.

Allowed UI phrases:
- Market-implied pricing distribution
- Risk-neutral distribution
- Priced market distribution

Disallowed UI phrase:
- “What the market truly believes”

---

## 2. User belief
Definition:
A user-specified subjective distribution or directional view about future outcomes.

Examples:
- center higher than market forward
- wider than ATM-implied width
- narrower than market
- left-tail risk larger than priced
- bimodal view (future phase)

Important note:
User belief is subjective and can differ from priced market distribution.

---

## 3. Disagreement
Definition:
The structured difference between user belief and market-implied pricing distribution.

Current disagreement dimensions:
- location / center
- width / dispersion
- strongest gap region

Future disagreement dimensions:
- skew
- tail asymmetry
- modality

Disagreement is descriptive, not prescriptive.

---

## 4. Strategy family
Definition:
A conceptual trade family that tends to fit a given disagreement pattern.

Examples:
- long call spread
- put spread
- iron butterfly
- long strangle
- ratio spread
- backspread

Important note:
A strategy family is not yet an exact trade ticket.
It is a **fit class**.

Allowed phrase:
- “Strategy families to explore”

Disallowed phrase:
- “Recommended trade” unless a later advisory layer is explicitly built

---

## 5. Illustrative family pattern (per strategy family)
Definition:
A **pattern-level** example tied to a strategy family row: labels, construction wording, optional symbolic legs (e.g. long call at K_lower, short call at K_higher).

Important notes:
- This is **not** a live-priced Deribit ticket and **not** strike-optimized from the user’s belief curve.
- Strikes are symbolic references (K_low, K_OTM, etc.), not selected market strikes.
- Use for education / exploration under “strategy families that fit this disagreement,” not as execution instructions.

Distinguish from **Exact priced structure (lab)** (§6): the green payoff line and trade summary use actual strikes and marks from the current run.

---

## 6. Exact priced structure (BTC implied lab — universal 4-leg)
Definition:
A fully specified trade **in this app** with exact strikes taken from user input or the target-payoff solver, direction, size, expiry context, and premiums from the current snapshot.

Includes:
- leg list with numeric strikes
- premiums used (marks × forward)
- net cost / credit
- max gain / loss
- breakevens
- payoff chart (green line)

---

## 7. Exact strikes mode
Definition:
User directly sets strike levels / leg inclusion and the app computes resulting payoff and analysis.

This mode is strike-first.

---

## 8. Target payoff mode
Definition:
User specifies desired payoff characteristics and the system solves for approximate strikes/legs under current market conditions.

This mode is payoff-first.

Important note:
This is an approximation / fitting process subject to market strike availability and pricing.

---

## 9. Verification
Definition:
Every major displayed output should be traceable to:
- source data
- timestamp
- formula or transformation
- assumptions
- resulting value

Verification must exist for:
- implied distribution inputs
- leg premiums
- net debit / credit
- max gain / loss
- breakevens
- payoff curve
- strategy fit explanation

---

## 10. Fit vs recommendation
Fit:
A structure shape that matches the disagreement pattern.

Recommendation:
A stronger claim that the user should actually place the trade.

Current product state:
We provide **fit**, not recommendation.

---

## 11. Sign conventions
Long option:
- user pays premium
- premium contributes positive cost

Short option:
- user receives premium
- premium contributes negative cost

Net debit:
- positive total cost

Net credit:
- negative total cost

This convention must remain consistent across:
- charts
- trade ticket
- calculations
- analysis text

---

## 12. Source hierarchy
Reference preference:
1. live market data used in current calculation
2. displayed reference tables/panels
3. derived outputs from internal models

Any mismatch between displayed reference values and derived calculation inputs must be surfaced, not hidden.

---

## 13. Current product boundary
This product currently provides:
- market legibility
- user belief expression
- disagreement interpretation
- structure exploration
- verification tooling

This product currently does not provide:
- guaranteed profitable trades
- full portfolio advice
- execution advice
- certainty about market mispricing