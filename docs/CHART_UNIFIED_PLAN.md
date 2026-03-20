# Plan: One unified chart (price, targets, options) — less messy

**Goal:** One main chart where price, “will it hit” targets, and options feel like a single view, with clear toggles. Options as **heatmap** so you can see them at a glance. **Implied probability and payout** for both options and prediction markets. **Multiple futures**, each line one expiry, extending to that date so it feels like “seeing into the future.”

---

## 1. Single chart, layered

- **One chart** that can show (all optional via toggles):
  - **Layer 1 — Price:** BTC spot + **multiple futures** (one line per expiry; see §5).
  - **Layer 2 — Price targets:** Horizontal lines at strike with probability labels at resolution dates. Toggle per target.
  - **Layer 3 — Options:** **Heatmap** of options (expiry × strike), same x/y axes — readable at a glance (see §2).

- **Remove** the separate “Deribit BTC options – expiry vs strike” chart as the default. Options live only on this main chart (heatmap) or in tables below.

- **Sidebar toggles:** Spot, Futures (which expiries), Price targets (multiselect), Options heatmap (on/off, Calls/Puts), “Show probability labels above X%”.

---

## 2. Options as heatmap (at a glance)

- **Use a heatmap** (not scatter) so the whole options surface is visible in one look:
  - **X:** expiry date (bucketed by week or month).
  - **Y:** strike (bucketed, e.g. 5k or 10k steps).
  - **Color:** either (a) **implied probability** (e.g. derived from option mark / strike or delta), or (b) **mark price** of the option, or (c) count “has option” (density). Preferred: **(a) implied probability** so “at a glance” means “see where the market implies probability by strike/expiry.”
  - **Two heatmaps** if needed: one for calls (e.g. green scale), one for puts (e.g. red scale), or one heatmap with a sensible color scale and call/put toggle.

- **Implied probability (options):**
  - For each option we have mark price (from Deribit ticker). **Implied probability** (risk-neutral): for a call, approximate as delta or as (mark / (index - strike))-style; for binary “above strike at expiry” we can use a simple proxy (e.g. call price / discount factor) or document “approximate from mark/delta.” Exact formula depends on model (Black–Scholes-style with IV); we can start with a simple proxy and add proper IV/BS later.
  - **Payout:** show **expected payout** or **payoff at expiry**: e.g. “If BTC = X at expiry, payoff = max(0, X - K) for call.” Display in table/tooltip: “Mark $X → implied prob ≈ Y%; payout at expiry (if spot = Z) = $W.”

- **Strike range:** Y-axis = price + selected targets (option A from before). Heatmap only fills the visible band so the chart doesn’t stretch to 0–400k.

---

## 3. Implied probability and payout — prediction markets

- **Prediction markets (Polymarket)** already give **Yes %** = implied probability. Keep showing it.
  - **Payout:** “If you bet $1 on Yes at current price p, you receive $1/p if Yes (so profit = (1/p) - 1).” Show in the implied-value table: columns **Implied probability**, **Payout (multipler)** or **Profit per $1 if Yes**, and existing **Strike / Resolution**.

- So both **options** and **prediction markets** get:
  - **Implied probability** (options: from mark/delta/IV; prediction: Yes %).
  - **Payout** (options: payoff at expiry for given spot; prediction: multiplier or profit per $1 if Yes).

---

## 4. Reducing clutter on the one chart

- **Probability labels:**
  - Keep “Show probability labels above X%” (default e.g. 5%). Hide 0% and other tiny percentages by default.
  - Optional: show at most one label per (strike, date) and prefer the “most important” (e.g. highest prob or latest date) to avoid duplicate “0% Yes” on the same line.

- **Vertical lines:**
  - Only draw vertical “resolution date” lines for the **selected** price targets. No extra grid lines.
  - Style: very light (e.g. opacity 0.25–0.35), maybe only when “Show probability labels” is above 0% so the two feel tied together.

- **Horizontal lines:**
  - Only for **selected** targets. One dashed line per selected strike, with a clear “$X” label on the left. No extra horizontal lines.

- **Defaults:**
  - Fewer targets selected by default (e.g. 3–4), options heatmap off by default. User turns it on when they want that layer.

---

## 5. Multiple futures — one expiry per line, “seeing into the future”

- **More than one futures contract:** Show **multiple** BTC futures (e.g. 3–6 expiries), not just the front month.
- **One line per expiry:** Each futures contract is **one line** that corresponds to **that contract’s expiry**. The line should **extend to that expiry date** on the x-axis so it feels like we’re “seeing into the future” — e.g. “Mar 2026 futures” runs until Mar 2026, “Jun 2026 futures” until Jun 2026.
- **How to plot:**
  - **Option A:** For each contract, we have a **time series of its price** (e.g. daily) until **today**. Draw that time series and **stop the line at today**; the contract’s **expiry date** is shown as a label or vertical marker so the viewer sees “this line is the Mar 2026 contract, and it expires here.” So the line doesn’t literally extend into the future (we don’t have future prices), but the **expiry date** is clearly marked and the line runs up to “now,” making the time axis feel like we’re looking toward those expiries.
  - **Option B (stronger “future” feel):** For each contract, plot a **single point or short segment at (expiry_date, last_trade_or_mark_price)**. So we see “today” on the left (spot + maybe front-month), and to the right we see **points at future dates** for Jun 2026, Sep 2026, etc. That’s a “forward curve” in one chart: spot and futures prices at their respective expiry dates. Then we can optionally connect “today’s spot” to “Mar 2026 futures price at Mar 2026” with a dashed line or leave as points. User said “the futures contracts line to be one expiry” — so each contract = one logical “line” or “curve to that expiry.”
- **Data:**
  - **Deribit:** `get_instruments(currency=BTC, kind=future)` gives multiple futures (BTC-28MAR26, BTC-27JUN26, etc.). We can get **mark price** or **last** per instrument and **expiration_timestamp** so we have (expiry_date, price). That fits Option B (forward curve) or we build short time series if Deribit provides history.
  - **Yahoo:** CME codes like BTCF2026 (Jan), BTCH2026 (Mar), BTCK2026 (May), etc. If Yahoo returns history per symbol, we get one time series per contract (Option A). Need to verify symbols (e.g. `BTC=F` vs `BTCH26`).
- **Recommendation:** Prefer **Option B** for clarity: x-axis = date (from “today” out to furthest expiry). Spot = line or point at “today”; each futures contract = **point at (expiry_date, current_mark_price)**. So we see “where the market is pricing BTC at future dates” in one view. If we add history later, we can add Option A (time series per contract) as an alternative view.

---

## 6. Tabs vs one scroll

- **Recommended:** Single scrollable page:
  - One unified chart at top (price + optional targets + optional options).
  - Below: “Implied value” table, then “BTC options & futures” summary, then raw “Prediction markets” table. So “together” = one chart; details stay below.

- **Alternative:** Tabs “Chart” | “Tables” so the chart can be full-width and tables don’t compete for space. Still only one chart; we’re not splitting chart into two.

---

## 7. Implementation order (when we do it)

1. **Remove** the separate “Deribit BTC options” chart block (or make it optional “full grid” only).
2. **Multiple futures:** Add Deribit (or Yahoo) fetch for **multiple** BTC futures; plot as **one point per contract at (expiry_date, mark_price)** so the chart shows a “forward curve” and feels like seeing into the future. Toggle which expiries to show.
3. **Single-figure logic:** Build one Plotly figure. Order: (1) spot, (2) futures (multiple expiries), (3) optional **options heatmap** (implied prob or mark by expiry × strike), (4) horizontal target lines, (5) vertical date lines, (6) probability annotations. Y-axis = price + selected targets.
4. **Options heatmap:** Aggregate options into (expiry_bucket, strike_bucket) grid; color by implied probability (or mark). Add implied probability + payout in table/tooltip (and in implied-value section for prediction markets).
5. **Implied probability & payout:**  
   - **Options:** Compute approximate implied prob (and payoff at expiry) from mark/delta; show in options table and/or heatmap hover.  
   - **Prediction markets:** Add column “Payout (multiplier)” or “Profit per $1 if Yes” to implied-value table.
6. **Clutter:** “Labels above X%”, fewer default targets, options heatmap off by default. Keep “Download as png.”

---

## 8. Out of scope for this plan

- Multiple charts (e.g. “Chart 1: price only”, “Chart 2: options only”) — we’re explicitly moving to one main chart.
- Changing data sources (Yahoo, Polymarket, Deribit) or calculation of implied value.
- Backtesting or trading logic.

---

**Summary:** One chart with layers: spot, **multiple futures (one per expiry, “forward curve” so we see into the future)**, optional **options heatmap** (at a glance), and price targets + labels. **Implied probability and payout** for both options and prediction markets (tables + heatmap/hovertooltip). Toggles control what’s visible. Separate options chart removed as default.
