# Jensen–November | Stage-2 Options Market Landscape walkthrough (pilot run 1)

**Date:** Friday, 2026-11-20, after US market close (Toronto time)  
**Scope:** Walk through the newly mandatory *guided market picture* stage and then perform a conditional, apples-to-apples stage-3/4 scenario check. **Documentation only; no live application UI, executable option quote, paper fill, trade, or persistence service created.**  
**Companion:** [MSOS Strategy Session Pilot v0.3, Stage-2 amendment](./MSOS_STRATEGY_SESSION_PILOT_V0_3.md). Draft PR #5524 remains open and unmerged.

## 1. Thesis in (user-provided; accepted, not independently debated)

- Underlying: **NVDA**.
- Belief: recovery to **approximately $200 by November 2027** (target presentation anchored to Friday **2027-11-19**); the word **'by'** can mean touch at least once or finish at/above, so both must be shown rather than silently conflated.
- Soft capital budget: **~$1,000 USD**; maximum acceptable loss not yet established (no inference of permission to lose the entire budget).
- Intended scenario comparison/exit: **2027-11-19**. Option structures previously considered use **2028-01-21** expiration (63 days remaining at intended exit). No trading authorization.

## 2. Market data provenance and integrity check

- Reported NVDA close on **2026-11-20: $125.53 USD** (Google Finance: https://www.google.com/finance/quote/NVDA:NASDAQ ; Yahoo historical: https://finance.yahoo.com/quote/NVDA/history/). This is a stock closing reference, not a synchronized stock/option order book.
- OptionCharts public page (https://optioncharts.io/options/NVDA/expected-move?expiration_dates=all&option_type=all&strike_range=all) displayed **November 19, 2027 IV ~47.61%** and an **indicative expected-move band $86.60–$183.89**. That symmetric band is centered at **$135.245**, NOT at the verified $125.53 closing reference; the page is internally using a different market snapshot. It cannot be combined with the closing stock price as if synchronized.
- The data source lists relevant expiries including 2027-06-17, 2027-09-17, 2027-11-19, 2027-12-17, and 2028-01-21; available listed expiries, liquidity, IV and prices still need source-specific timestamp verification.
- **Status:** historical/indicative landscape; **not executable**. Do not call these figures current synchronized broker quotes.

## 3. Guided visual market map — transparent illustrative calculation

A transparent Black–Scholes/GBM **model illustration** re-anchors all ranges consistently to **$125.53** spot using one *assumed* flat **47% annual volatility**, **4%** annual risk-free interest, **zero dividends**, continuous diffusion, calendar-day year fraction /365.25, no fees, and valuation date 2026-11-20. This intentionally avoids pretending the mismatched option-chain timestamps are a calibrated volatility surface. Ranges below are the model's **16th–84th percentiles** (approximate central 68% under these assumptions), NOT provider quotes, calibrated densities, or objective 68% forecasts. **Modeled terminal probabilities are risk-neutral.**

| Illustrative date | Time from 2026-11-20 | Approx. modeled central 68% finish-price range | Modeled P(finish ≥ $200) | Modeled P(touch $200 at least once by date) |
|---|---:|---:|---:|---:|
| 2027-06-17 | 209 days | **$84.50–$172.05** | **7.7%** | **16.3%** |
| 2027-09-17 | 301 days | **$77.31–$181.48** | **11.0%** | **23.6%** |
| **2027-11-19 (thesis anchor)** | **364 days** | **$73.20–$187.08** | **12.7%** | **27.5%** |
| 2028-01-21 | 427 days | **$69.55–$192.17** | **14.0%** | **30.8%** |

For terminal range: ln(S_T/S_0) ~ Normal[(r - 0.5 sigma^2)T, sigma sqrt(T)] and the ±1 sigma log-price quantiles give the reported bounds. For P(finish ≥ 200): Phi((ln(S0/200)+(r - 0.5 sigma²)T)/(sigma sqrt(T))). For P(touch 200): the standard reflection-principle first-passage formula for a continuous drifted GBM log-price barrier; **far more model-dependent than a vanilla option-implied terminal probability**. Volatility jumps, skew, dividends, borrow, jumps/gaps, non-constant IV, rate changes, and event dynamics could alter both estimates greatly.

### How the user should interpret the map

- $200 is **+59.3% from $125.53**. On this flat-volatility illustration, it lies **above** the modeled upper central-68% price bound at the Nov-2027 thesis date ($187.08), but it is **not impossible**. The modeled probability of touching $200 sometime within a year (~27.5%) differs materially from ending above $200 (~12.7%).
- Later horizons widen the price range and raise target-reaching probabilities **in this particular model**. Those percentages are **not an objective market forecast** and do not validate/disprove the user's thesis.
- Illustrative upside exposure cost (model, 2028-01-21 expiry): a single **$180 call** at ~$12.03/share or **~$1,203/100-share contract**, and **$200 call** at ~$8.88/share or **~$888/contract**. These are model values, not bids/asks, fills, or commissions; the precise cost-of-expression requires synchronous quotes and liquidity checks.
- **Stage-2 exit:** Can the user see the horizon-specific ranges, find their $200 target on the plot, distinguish *touch vs finish*, and appreciate quote quality and hypothetical cost? Status **illustrative-market-read**; user experience/understanding not yet confirmed in interactive pilot.

## 4. Stage 3–4: conditional identical-exit comparison (not a substitute for stage 2)

All candidates below use **same 2027-11-19 sale date** and same modeled **2028-01-21 expiration** for options. Option entry values are *internally consistent* Black–Scholes values at 47% vol, 4% rates, no dividends/fees; option exit values use that same flat IV with 63 calendar days remaining. **Not observed premium quotes, and not directly comparable with premiums recorded in the preceding session**. Price scenarios are underlying NVDA on 2027-11-19.

| Candidate | Illustrative entry capital | Max loss at final expiry / to zero | P/L at $100 | P/L at $170 | P/L at $200 | P/L at $250 | Upside |
|---|---:|---:|---:|---:|---:|---:|---|
| **8 NVDA shares** | $1,004.24 | $1,004.24 | -$204 | +$356 | **+$596 (+59.3%)** | +$996 | Uncapped stock-price upside; no expiry |
| **2028-01 $180/$200 debit call spread** | ~$314 | ~$314 premium | -$314 | +$216 | **+$836 (~266%)** | +$1,490 | **Capped at expiration**, but pre-expiry residual time value remains |
| **2028-01 $170/$200 debit call spread** | ~$512 | ~$512 premium | -$510 | +$432 | **+$1,366 (~267%)** | +$2,246 | **Capped at expiration**, target-focused |
| **2028-01 long $180 call** | ~$1,203 | ~$1,203 premium | -$1,202 | -$240 | **+$1,568 (~130%)** | +$5,993 | **Uncapped** stock-price upside, premium/time risk |

Precise modeled underlying inputs: 2026-11-20 spot $125.53; one standard US equity contract 100 shares; option Jan-2028 T=427/365.25; Nov-2027 residual time=63/365.25; mark-to-model valuations, not expiry intrinsic payoffs. Rounded displayed values can differ by ~$1. 8 shares cost slightly above the ~$1,000 soft budget; a long $180 call exceeds it more substantially. No fees, FX, bid/ask slippage, taxes, stock dividends, contract adjustment, or transaction validation incorporated.

**Do not claim a final winner.** The narrower $180/200 spread requires less premium but has less absolute target profit; the $170/200 spread has more target dollars at risk and more target dollars of profit; stock has no expiry and long call remains uncapped. At $250 the uncapped call has much higher modeled profit, illustrating why target-ROI ranking should never hide tail exposure. The stage-2 read did not need to force the user into any one of these choices.

## 5. Findings and proposed modifications from pilot run 1 — provisional, user review pending

1. **Provenance/compatibility control is essential.** A provider one-sigma band centered $135.245 and verified stock close $125.53 cannot be overlaid as a single contemporaneous read. The UI needs a visible **quote snapshot mismatch indicator** and a clean fallback to an explicitly modeled scenario, not a hidden blend.
2. **Touch-versus-finish is a first-class control.** 'By November 2027' materially changes interpretation. Ask once only when it changes strategy choice; meanwhile show both where defensibly modeled. Touch probability requires stronger modeling assumptions than vanilla terminal pricing.
3. **Visual and semantics:** Market map should identify the user's price/date directly, make percentages conditional on date and model, show actual listed expiries, and distinguish **intended sale date** from **option expiration**.
4. **Exposure pricing must be per share AND per contract**, with the user's capital/maximum-loss limits beside it; use real bid/ask only when synchronized.
5. **Range display cannot be a naked single 'expected move' label.** Explain whether the range is symmetric dollar expected move or lognormal model percentile interval, which need not have identical endpoints.
6. **Validation needed:** run real UI with a trader; confirm that the visual helps them explain market-versus-thesis disagreement *before* options structures are proposed. Test other assets/horizons; verify IV surface/quote provenance; model stress and executable spread/volume filters before treating stage 2 as hardened.

## State

- **Protocol amended on draft PR:** Yes.
- **Jensen walkthrough:** Run as a documented **model-assisted dry run**; awaiting actual user-guided reaction to the map, not a validated interactive product UX.
- **Potential modifications:** Proposed above; not yet frozen as core product requirements or merged into main.
- **Paper/live trading:** None.

## 6. Interactive user test — 2026-11-21 (run 2, feedback)

**Nature of test:** Simulated Jensen dialogue about the market picture, not production UI testing or a live option-chain extraction. The user role-played/investigated the thesis without authorizing an order. Keep the earlier run-1 **47%-assumed** distribution and later verbalized **50.44% IV / ~$133.54 forward / ~15% finish-above-$200** simplified calculation as **distinct, unverified model snapshots** rather than silently combining them.

**Observed behavior and corrections:**
1. The trader welcomed five proposed reporting lenses — expiry-aligned IV, finish-above target probability, full terminal distribution, smile/skew, and term structure — but asked **"paint the picture"** instead of listing metrics without interpretation. The model read needs a visual distribution *first*, and supporting mechanics second.
2. A spoken statement that options priced **"zero chance"** of reaching $200 was wrong. The assistant corrected it to approximately **15% finishing above $200** under its simplified, assumption-dependent model; that number should **not** be described as a verified chain-derived probability, real-world forecast, or an estimate of *touching* $200.
3. The trader wanted to know **"what does the options market think Nvidia will look like in one year?"** before choosing touching-versus-finishing or discussing trades. The product should orient with a full range, median versus forward, and tails; keep risk-neutral versus objective uncertainty in view without requiring the trader to master jargon first.
4. On hearing "high volatility," the trader asked whether they could **do less volatility**. This was ambiguous between predicting lower realized volatility (possible short-premium hypothesis) and wanting less sensitivity to option-premium/IV movements. The assistant's initial branch to iron condors/credit spreads was premature. Ask the distinction conversationally **after** the market map.
5. The trader then described **high realized volatility but finishing in the higher half**, followed by preference for **uncapped upside**, possibly at least **25% appreciation**. These ideas are exploratory and do not replace the earlier $200-by-November-2027 thesis as a committed statement. At the dated $125.53 reference spot, 25% appreciation is ~$156.91. The median ("upper half") of a risk-neutral pricing model is not automatically a profitable edge.
6. The trader identified why a credit spread with capped upside does not serve a desire to benefit from very large gains. Mandatory **underlying shares** and, subject to budget/quotes, **long-call** alternatives belong in candidate comparisons. Shares offer uncapped price appreciation and no option-IV premium, **but not low stock-price volatility or downside protection**. Long calls are uncapped above break-even but add premium, time decay, IV and expiration risk. If 100-share option contracts exceed the ~$1,000 soft budget, state infeasibility instead of suggesting synthetic fills.
7. The user concluded the deep discussion was valuable for serious participants but expressly requested **a simple, retail-friendly path** using the same underlying facts.

**Resulting change:** Added [Stage-2 refinement from interactive Jensen test](./MSOS_STRATEGY_SESSION_PILOT_V0_3.md#stage-2-refinement-from-interactive-jensen-test--2026-11-21) to draft pilot workflow with **simple default / optional deep dive**, five metrics as explanatory layers, explicit data-provenance labels, and a clarified market-read → thesis interpretation → strategy construction → execution order.

**Gate/status after run 2:** `illustrative-market-read` only. **No verified chain-derived risk-neutral density; no executable options quote; no tested production interface; no validated performance or profitability advantage; no chosen strategy; no paper/live trade.** Next implementation slice should be tested with a nontechnical user for comprehension and with an advanced user for market data provenance, model integrity, liquidity and probability-method accuracy.


## 7. Position lifecycle dry-run fixture — 2026-11-27 (not yet user-tested)

Reuse the original exploratory $200-by-November-2027 thesis, ~$1,000 soft budget, unresolved max acceptable loss and touch/finish choice; no final strategy or trade. Use the internally consistent section 4 model fixture, not the different premium estimates in the pilot protocol.

For illustration only, consider one Jan 21, 2028 $170/$200 debit call spread at modeled ~$512 debit. At expiration its maximum gross value is $3,000; maximum original loss is ~$512 (assuming the intact spread and no costs/assignment complications). At the planned Nov 19, 2027 exit with NVDA at $200, section 4 estimates a model value of ~$1,878 (= $512 + $1,366 P/L), with 63 days to expiration. No bid/ask or actual trade is implied. Closing at that model mark would realize ~$1,366 gross profit; continuing to expiry exposes ~$1,878 of foregone liquidation value to potential loss, for at most ~$1,122 additional gross payoff at expiry. These are bounds relative to modeled liquidation today, not expected returns, guarantees or actual executable proceeds. Do not confuse original risk with remaining exposure.

Guided questions: If NVDA touches $200 much earlier, is that a sale trigger or a review? If price falls but the thesis survives, is the remaining exposure attractive and within risk limits? If target is reached at the planned date, what justifies extending beyond it? Is preserving gains, retaining upside, or pursuing another thesis the priority? Reassess using synchronized quotes or clearly hypothetical marks and updated user beliefs, compare closing/holding/restructuring and shares baseline; one contract cannot be fractionally reduced. The example does not assume the user wants capped upside, a specific stop, or a deadline extension. No actual order, paper fill or live price claim. Record the user's answers only after the next interactive dry run.
