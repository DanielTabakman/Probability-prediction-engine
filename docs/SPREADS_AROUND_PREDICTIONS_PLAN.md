# Plan: Create spreads around the predictions

**Goal:** Build option spreads (bull call spreads) that are **aligned with** Polymarket prediction questions (e.g. "Will Bitcoin hit $150k by Dec 31, 2026?"). So each spread is designed around a specific prediction: strikes near the target, expiry near the resolution date. This lets you compare the **options-implied** view vs the **prediction-market-implied** view for the same event.

---

## 1. What "spreads around predictions" means

For each Polymarket question we have:
- **Strike (target):** e.g. $150,000
- **Resolution date:** e.g. 2026-12-31
- **Yes probability:** e.g. 30% (from Polymarket)

We want to create a **bull call spread** that:
- **K_low:** strike at or below the target (e.g. $145k or $140k)
- **K_high:** the target itself (e.g. $150k) — so the spread "pays off" if we hit the target
- **Expiry:** Prefer nearest Deribit expiry **on or before** resolution date; if none, use nearest after (so option expires before/same as prediction resolves)

So the spread is **structurally tied** to the prediction: "If BTC > $150k by expiry, the spread pays (K_high - K_low)." We can then compare:
- **Prediction market:** 30% implied probability of hitting $150k
- **Options spread:** cost, max gain, max loss, and derived implied probability (if we back it out from the spread price)

---

## 2. Matching prediction → option spread

**Input:** List of btc_questions (from Polymarket) with strike, resolution_date, yes_probability.

**For each question:**
1. **Target strike** = question strike (e.g. $150k)
2. **Target date** = resolution_date (e.g. 2026-12-31)
3. **Find Deribit call options:**
   - Expiry: pick the Deribit expiry **closest** to target date (prefer before or same month; document the choice)
   - K_high = target strike (or nearest listed strike if exact match doesn't exist)
   - K_low = strike below K_high (e.g. K_high - 5k or 10k, or nearest listed strike)
4. **Fetch mark prices** for both calls (long K_low, short K_high)
5. **Compute:** cost, max loss, max gain, R:R (same as current tight bull spreads)
6. **Optional:** derive **approximate** implied probability: cost / (K_high - K_low). Label as "approx" in UI — it's a simplification (spread has payoff between strikes; ignores time value).

**Output:** List of "prediction-aligned spreads" — one per question (or subset if we can't find matching options for all).

---

## 3. Data requirements

- **Polymarket:** Already have btc_questions with strike, resolution_date, yes_probability.
- **Deribit:** Need call options at specific (expiry, strike) pairs. We have `fetch_deribit_btc_options_instruments` and `fetch_deribit_ticker`. For each question we:
  - Get all BTC calls, filter to expiries near resolution_date
  - Find instruments at K_low and K_high
  - Fetch ticker for each (2 ticker calls per question; rate limit ~0.2s between)
- **Limit:** If we have 10+ questions, that's 20+ ticker calls. We may want to cap (e.g. first 5 questions) or cache.

---

## 4. Spread structure options

**Option A — K_high = target (spread pays at target):**
- K_low = target - 5k or 10k (or nearest)
- K_high = target
- Spread pays (K_high - K_low) if BTC > target at expiry. Directly comparable to "will it hit target?"

**Option B — K_low and K_high bracket the target:**
- K_low = target - 5k, K_high = target + 5k
- Spread pays max if BTC > K_high; partial payoff between K_low and K_high. Less direct but captures "in the range."

**Recommendation:** Option A — K_high = target. Cleaner mapping: "prediction says X% chance to hit $150k; options spread costs $Y for payoff if we hit $150k."

---

## 5. Implied probability from the spread (optional)

For a bull spread (long K_low, short K_high):
- Cost = C(K_low) - C(K_high)
- Max gain = (K_high - K_low) - cost
- In a simple model, cost / (K_high - K_low) ≈ probability that spot > K_high at expiry (risk-neutral). So:
  - **Implied prob (options) ≈ cost / (K_high - K_low)**
- Compare to **Polymarket Yes %** for the same event. If options imply 25% and Polymarket says 30%, that's a potential edge (or different assumptions).

---

## 6. UI / display

- **Chart overlay:** For each prediction-aligned spread, draw the vertical segment at the **resolution date** (not option expiry if different) from K_low to K_high, with label e.g. "$150k pred: 30% | spread R:R 1:1.2". Or use resolution date for consistency with the question.
- **Table:** New section "Spreads around predictions" with columns:
  - Question (short)
  - Target (strike)
  - Resolution date
  - Polymarket Yes %
  - Spread: K_low / K_high
  - Option expiry (actual)
  - Cost, Max loss, Max gain, R:R
  - Implied prob (options) — if we compute it
  - Delta: Polymarket % vs options implied % (e.g. "30% vs 25%")
- **Sidebar:** Toggle "Show prediction-aligned spreads on chart" (separate from generic tight bull spreads).

---

## 7. Implementation order

1. **New fetcher:** `fetch_deribit_spreads_around_predictions(btc_questions, max_questions=5)` — for each question, find matching Deribit calls (expiry near resolution, strikes around target), fetch marks, compute cost/R:R, optionally implied prob.
2. **Strike/expiry matching logic:** Map resolution_date → nearest Deribit expiry; map target strike → nearest K_high, then K_low = K_high - 5k or 10k (or nearest).
3. **Table:** Add "Spreads around predictions" section with full comparison (Polymarket vs options).
4. **Chart overlay:** Add vertical segments for prediction-aligned spreads (or merge with existing bull spread overlay, but label differently so user can tell "this one is tied to the $150k question").
5. **Sidebar toggle:** "Show prediction-aligned spreads" vs "Show generic tight bull spreads" — user can choose one or both.

---

## 8. Edge cases & sanity checks

- **No matching options:** Some targets (e.g. $2,025) may have no Deribit calls at that strike. Skip or show "No options at this strike."
- **Odd targets:** Targets < $10k (e.g. $2,025) — skip; Deribit BTC strikes are typically 50k–200k+.
- **Already hit:** If spot > target, skip (prediction effectively resolved).
- **Expiry matching:** Prefer expiry ≤ resolution_date; if none, use nearest after. Small mismatch acceptable.
- **Very far dates:** Predictions for 2027+ may have no Deribit options yet. Skip.
- **Duplicate targets:** Multiple questions for same strike (e.g. $150k by different dates). Create one spread per question (different expiries).
- **Chart overlay:** Use **blue** for prediction-aligned spreads (distinct from **green** generic tight bull spreads).

---

## 9. Out of scope

- Other spread types (bear spreads, iron condors) — focus on bull spreads aligned with "will it hit" predictions.
- Trading execution — this is analysis/visualization only.

---

**Summary:** For each Polymarket "will it hit $X by date Y" question, build a bull call spread with K_high = X (or nearest) and expiry near Y. Compare options-implied probability vs Polymarket Yes %. Display in table and optionally overlay on chart. Toggle separate from generic tight bull spreads.
