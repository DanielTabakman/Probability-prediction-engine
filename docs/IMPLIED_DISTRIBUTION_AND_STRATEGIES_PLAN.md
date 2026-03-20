# Plan: Implied Probability Distribution Chart + Multi-Leg Strategies

**Goal:** (1) Build an **implied probability distribution** chart from derivatives (options) that looks like a clean bell curve (e.g. IB Probability Lab style). (2) When the distribution looks **anomalous** (weird shape, skew, bimodal), use **multi-leg options strategies** to reshape or exploit it so the result looks more like the desired distribution (or expresses a clear view).

---

## Part 1 — Implied Probability Distribution Chart

### 1.1 What we’re building

- **Chart type:** Bar chart / histogram of **risk-neutral probability density** (or “probability per 1 USD”).
- **X-axis:** Underlying price at expiry (e.g. “BTC price on Jun 18 ’26”), in USD.
- **Y-axis:** Probability density (e.g. “Probability per 1 USD”), 0% to ~30% (or scaled).
- **Optional:** Cumulative probabilities at key price levels (e.g. “18.99% below 24k”, “52.79% below 31k”) under the x-axis or in a second panel.
- **Controls:** Asset (BTC), expiry (e.g. “Jun 18 ’26”), and optionally toggle “Custom vs Market” if we add a custom vol/curve later.

### 1.2 Data and method

- **Source:** Deribit BTC options (we already have instruments + mark/ticker).
- **Method options:**
  - **A. From implied vols:** Get IV per strike from Deribit (ticker has `mark_iv`), build a smooth IV surface, then use Black–Scholes to get option prices and **Breeden–Litzenberger** (second derivative of call price w.r.t. strike) to get risk-neutral density. Gives a smooth curve.
  - **B. From option prices only:** Use Breeden–Litzenberger on observed call prices (or put/call combos) to get implied density at discrete strikes; interpolate for a smooth curve.
  - **C. Simple proxy:** Assume lognormal; use ATM IV (or average IV) and forward price to draw a single lognormal bell. Fast and robust; less accurate than A/B.

- **Recommendation:** Start with **C** (lognormal from forward + single vol) so we get a chart that “looks like the left” quickly; then add **A** or **B** for a market-implied distribution from real option data.

### 1.3 Forward price and volatility

- **Forward:** From Deribit (e.g. `index_price` or futures mark for that expiry) or from spot + cost of carry; we may already have this from futures forward curve.
- **Volatility:** From ATM option IV (`mark_iv` from ticker) for the chosen expiry, or average of a few strikes around ATM.

### 1.4 Output

- One chart: **Implied probability distribution** for chosen (asset, expiry).
- Optional second chart or same figure: **Cumulative distribution** (CDF) or just cumulative % at a few strike labels.

---

## Part 2 — “Anomalous” Charts and What We Mean

### 2.1 When is a chart “anomalous”?

We treat the distribution as anomalous when it **deviates** from a “normal” bell in a way that’s exploitable or worth correcting:

- **Heavy skew** (e.g. left or right tail much fatter than lognormal).
- **Bimodal / multi-peak** (e.g. two humps).
- **Very fat tails** (more probability far from the mean than a lognormal).
- **Odd bumps** at specific strikes (e.g. pin risk, supply/demand).

We can detect these by:

- Comparing implied density to a **reference lognormal** (same forward, same ATM vol): e.g. sum of squared differences, or KL divergence.
- Simple heuristics: skewness of the implied distribution, or “second peak” detection (local max far from the main peak).

### 2.2 What “turn it into something like the left” means

- **Interpretation 1 (hedging / smoothing):** Find a **multi-leg options strategy** such that your **combined position** (existing exposure + strategy) has an implied distribution that looks more like a clean bell (e.g. closer to lognormal). So we’re “correcting” the anomaly with options.

- **Interpretation 2 (expression / trade):** Find multi-leg strategies that **express a view** on the anomaly (e.g. “market is too skewed; sell the tail”) so the **strategy’s payoff** (or the market’s implied distribution after the trade) looks more like the desired shape.

We’ll support both by:

- Defining a **target distribution** (e.g. lognormal with forward + chosen vol).
- Defining a **distance** (e.g. L2 on density, or on CDF).
- **Strategy scanner:** Search over small multi-leg strategies (e.g. max 2–4 legs: spreads, straddles, condors) and score them by how much they **reduce the distance** between current implied and target (or by payoff shape vs target).

---

## Part 3 — Multi-Leg Options Strategies

### 3.1 Strategy set (to start)

- **Spreads:** Bull call, bear call, bull put, bear put (we already have bull spreads).
- **Straddle / strangle:** Long or short ATM (or OTM) call + put.
- **Butterfly / condor:** Three or four legs to “peak” or “flatten” the payoff around a range.

We’ll use **Deribit** option marks (and IVs when available) to price each leg and aggregate.

### 3.2 Strategy scanner (like “Build Strategy” on the right)

- **Inputs:** Current implied distribution, target distribution (e.g. lognormal), constraints (e.g. “Delta neutral”, “Max 2 legs”, “Include stock leg” = include spot/futures).
- **Process:**
  - Enumerate candidate strategies (e.g. all 2-leg combinations from a strike/expiry grid, or a fixed list of strategy types).
  - For each, compute **net cost** and **payoff at expiry** (and optionally implied distribution of “market + strategy” if we model it).
  - Score by “how much does this move implied distribution toward target?” (e.g. reduce L2 or KL distance) or by risk/reward (e.g. max loss, probability of profit).
- **Output:** Ranked list of strategies with expected payoff shape and “distance to target” or R:R.

### 3.3 UI

- **Anomalous chart:** Same implied distribution chart as Part 1, but we **flag** it (e.g. “Anomalous: high skew” or “Bimodal”) when detection triggers.
- **Strategy scanner panel:** Checkboxes (e.g. “Delta neutral”, “Max 2 legs”, “Include stock leg”), “Build Strategy” button, list of suggested strategies with payoff and impact on distribution.
- **“Apply” or “Overlay”:** Optionally overlay the **resulting** implied distribution (after adding the strategy) so it “looks like the left”.

---

## Part 4 — Implementation Order and Checkpoints

### Phase 1 — Implied distribution chart (looks like the left)

1. **Data:** Reuse Deribit BTC options; add or confirm **forward price** and **ATM IV** for a chosen expiry (from ticker or book summary).
2. **Model:** Implement **lognormal implied distribution** from (forward, vol, expiry). Plot PDF (bar or line) with x = price at expiry, y = probability per 1 USD (or per bucket).
3. **UI:** One chart in the app: asset + expiry selector, then “Implied probability distribution” with optional cumulative % at a few strikes. **Check:** Chart looks like a single bell, axis labels match intent.
4. **(Optional)** Add **market-implied** density from Breeden–Litzenberger using Deribit option prices; compare to lognormal on the same chart.

### Phase 2 — Detect “anomalous” and show when chart is anomalous

1. **Reference:** Use same lognormal (forward, ATM vol) as reference.
2. **Detection:** Implement at least one of: (a) skewness of implied vs lognormal, (b) L2 distance of PDF to lognormal, (c) simple “second peak” check. Flag when above threshold.
3. **UI:** When we use market-implied density (Phase 1 optional), show a badge or caption “Anomalous” when detected; otherwise skip or use “Simulated anomalous” for demos.

### Phase 3 — Multi-leg strategy builder / scanner

1. **Strategy definitions:** Enumerate 2-leg (and optionally 3–4 leg) strategies (spreads, straddle, strangle, butterfly, condor) with strikes/expiry from Deribit.
2. **Pricing:** For each strategy, sum leg costs (mark from Deribit); compute payoff at expiry on a price grid.
3. **Scoring:** Define “distance to target” (e.g. L2 between (current implied + strategy payoff) and target PDF). Or simpler: rank by R:R or “probability of profit.”
4. **UI:** Panel “Strategy Scanner” with “Delta neutral”, “Max 2 legs”, “Build Strategy”; table or list of suggested strategies with cost, payoff sketch, and “distance to target” or R:R. **Check:** Suggested strategies are reasonable (e.g. delta-neutral straddle when vol is high).

### Phase 4 — “Turn anomalous into bell”

1. **Combined view:** When user selects a strategy from the scanner, show **updated implied distribution** (current implied + strategy payoff, normalized) so the chart “moves” toward the bell.
2. **Check:** For a synthetic “anomalous” input (e.g. bimodal), at least one suggested strategy makes the combined distribution closer to lognormal.

---

## Part 5 — Out of scope (for this plan)

- Full IV surface fitting (we can use one vol or simple smoothing first).
- Backtesting or live trading execution.
- Other assets (gold, silver) until BTC path is solid.

---

## Summary

| Part | Deliverable | Check |
|------|-------------|--------|
| 1 | Implied probability distribution chart (lognormal, then optionally market-implied) | Bell shape, correct axes, expiry selector |
| 2 | Anomaly detection (skew / bimodal / distance) | Badge “Anomalous” when we use market-implied and it’s non-lognormal |
| 3 | Multi-leg strategy scanner (2–4 legs, priced from Deribit) | List of strategies with cost, payoff, score |
| 4 | “Turn into bell”: overlay resulting distribution after strategy | Combined chart moves toward bell when strategy applied |

**Phase 1 (done):** Implied distribution chart implemented:
- `src/engine/implied_distribution.py`: `lognormal_pdf`, `lognormal_cdf`, `build_distribution_chart_data`
- `src/data/fetch_deribit.py`: `fetch_deribit_btc_option_expiries`, `fetch_deribit_forward_and_iv_for_expiry`
- App: section "Implied probability distribution" with expiry selector, forward + ATM IV from Deribit, bell chart + cumulative % labels

**Phase 2 (done):** Anomaly detection:
- `fetch_deribit_btc_option_marks_by_expiry(expiry_ts)`: call marks from `get_book_summary_by_currency` for one expiry
- `market_implied_density_breeden_litzenberger(strikes, call_prices_usd, price_grid)`: risk-neutral density from options
- `is_anomalous(prices, lognormal_pdf, market_pdf, threshold)`: L2 distance > threshold
- App: plot "Market-implied (options)" (orange dashed) alongside lognormal; title "— Anomalous" + st.warning when market differs from lognormal

**Phase 3 (done):** Multi-leg strategy scanner:
- `fetch_deribit_btc_option_marks_by_expiry_full(expiry_ts)`: returns `{"calls": [...], "puts": [...]}` (one book summary).
- `src/engine/strategy_scanner.py`: `build_strategies(forward, marks_calls, marks_puts, max_legs=2)` → straddle (ATM), strangle (OTM), bull call spread, bear call spread; each with cost_usd, max_loss, max_gain, rr_ratio.
- App: "Strategy scanner" section below implied distribution; table of Strategy, Legs, Cost (USD), Max loss, Max gain, R:R. Uses same expiry and book summary as the chart.

**Phase 4 (done):** Overlay strategy payoff on the distribution chart.
- `strategy_payoff_at_prices(strategy, prices)`: net P&L at expiry (payoff − cost) at each price.
- Each strategy stores `payoff_type` and strikes for payoff calculation.
- App: "Overlay strategy payoff" selectbox above the chart; when a strategy is selected, green payoff line on a **secondary y-axis** (right: "Strategy P&L (USD)") so distributions and payoff are visible together.
