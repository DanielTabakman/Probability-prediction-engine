# MSOS Strategy Session Pilot — v0.3 (Jensen — November)

**Date:** 2026-11-20  
**Status:** Pilot protocol and retrospective; proposed documentation awaiting review/merge. **Not** a shipped MSOS feature, broker execution, or a validated options-pricing engine.  
**Scope:** Strategy-session product design for MSOS/Strategy Lab. This document does not change existing PPE mathematical contracts, production routes, or build/frontier selection.

## Product boundary

**Trader supplies the thesis; MSOS helps translate it into an options-market-informed expression.** The core guided flow should not require independent fundamental-research or counterfactual validation. A trader may bring research from elsewhere. Market-derived probabilities are **risk-neutral/model-implied**, not forecasts that the thesis is correct.

## Reusable guided workflow and stage gates

| Stage | Question / input | Required output | Exit gate |
|---|---|---|---|
| 1. Optional starting route: thesis-first **or** market-first | User may state target/timing first to avoid market anchoring, or choose an underlying and hear the independent market briefing before specifying a thesis; budget/maximum loss gathered before sizing | Original thesis (if supplied first) preserved separately from post-briefing revisions; market-first route need not invent a target | Route selected without forced thesis-first ordering |
| 2. **Options Market Landscape — mandatory guided exploration** | User's target/horizon from stage 1 plus available expirations, spot, option chains, bid/ask, IV/skew/term structure, liquidity, quote timestamps | **User-facing horizon-specific market picture**: market-implied outcome ranges across relevant dates, user's thesis target/trajectory overlay, selectable expiry/details, implied target probability (only where supported), indicative exposure cost and reliability flags | User can explain the market/pricing picture and divergence from their thesis; mark **simulation-only / incomplete** if reliable market inputs are missing. No strategy construction before the **conceptual landscape read**; illustrative downstream dry-run remains permitted with explicit limitations |
| 3. Candidate construction | What are the practical expressions within constraints? | **Mandatory buy-and-hold underlying benchmark** plus 2–3 reasonable options structures (where applicable), with contract details and sizing | All candidates dimensionally valid and costed from compatible data |
| 4. Outcome comparison | Same entry/exit assumptions and price scenarios for all candidates; vol/skew/time stress; trading costs | Decision cards: capital, max loss, target P/L and ROI, partial-success/flat/downside cases, capped or uncapped upside, breakevens, sensitivities, liquidity, model probabilities only when justified | Comparable scenarios and assumptions disclosed, no claim of objective 'best' without objective function |
| 5. Select and save | Which tradeoff fits user's chosen priority? | Reproducible strategy record, rationale, alternative rejection reasons, snapshot provenance, unresolved risks | User selects or explicitly defers; saving confirmed by actual persistence |
| 6. Theoretical execution (separate) | Paper/order simulation with entry assumptions and hypothetical exit rules | Paper-trade record clearly marked **simulated, not placed**, with simulated fill assumptions | Persistent paper-trade service and tracking are **future work**, not implied by this conversation |
| Future: live execution | Separate permissions, venue integration, pricing, and order confirmation | Executed order acknowledgment only when broker/venue verifies | Not authorized or built in this pilot |

**Navigation:** state current stage and what's done, next, blocked; do not imply all stages are sequentially blocked by quotes: stages 3/4 can be run as **historical/conditional dry runs** while stage 2 remains provisional. Mark all stage transitions and snapshot versions.

## Stage 2: Options Market Landscape — guided, adaptive market map (pilot amendment, 2026-11-20)

**Product requirement:** Deliver a visible, guided understanding of what the options market is pricing across relevant horizons **before the user implements or executes strategies**, regardless of whether the user states their thesis first or reads the market first. The user may deliberately choose the order to avoid anchoring bias. Do not silently skip the market briefing just because the backend has retrieved a chain or because another stage references implied volatility.

**Flexible entry / mandatory convergence:**
- **Thesis-first:** Trader supplies a directional view, target and timeframe without seeing the options market; MSOS then delivers an independent, relevant market briefing and overlays the supplied thesis. Preserve the user's original, pre-briefing thesis so that later revisions are identifiable.
- **Market-first:** Trader selects an underlying or theme and receives an editorial-style, self-contained snapshot: what the options market is pricing across meaningful, adaptable horizons; prevailing volatility/skew, pricing of upside versus downside, ranges, changing expectations across expiries, liquidity and uncertainty. The trader can then formulate or revise a thesis and overlay it on the snapshot.
- **Either route:** Before the strategy construction/comparison sequence progresses to selection and any simulated or actual execution, MSOS must show the market read, discuss its implications relative to the thesis if one exists, label all data/probability limitations, and log that the briefing was presented. Strategy ideation is permitted earlier, but no implementation/execution should bypass the briefing. A model-only or stale-data briefing does **not** authorize executable trade claims.

**Briefing presentation:** Think of a fintech reporter providing an accessible *options-market situation report*, not a probability calculator activated only by a user's price target. It should stand alone before the user gives a target, be comprehensible as a narrative plus market map, and adapt horizons to the underlying's available expirations and the trader's interests. A useful briefing explains what is priced, what changed if historical comparisons are reliable, what is unusual only when benchmarked, and what remains unknowable from options prices. Do not imply market consensus on future real-world returns from risk-neutral pricing.

**Jensen clarification:** The user's $200 NVDA thesis means *touching $200 at any point by November 2027*, not requiring the stock to close or finish at/above that level. Show any touching estimates as strongly model-dependent and do not equate them with terminal option-implied probabilities.

**Horizon selection is adaptive, not a fixed 6/12/18-month schedule.** Anchor on the trader's stated timing, flexibility, target and the expiries actually listed. Include useful nearer/later expiries to expose timing sensitivity; note gaps. A three-week thesis should not receive the same timeline as a two-year thesis. Distinguish option **expiry** from the trader's planned **exit** (positions may still have residual time value when exited).

**Default interaction, subject to real data and product feasibility:**
1. Present an intuitive market map: horizontal axis = time/expiry, vertical axis = underlying price; display labeled market-implied price ranges/distributions. Overlay the trader's target price or expected trajectory and date. Where distributions cannot be robustly inferred, show IV-derived **illustrative** ranges with conspicuous assumptions instead of fabricating an estimated density.
2. Permit selection of relevant dates/expiries to inspect details: available strikes and bid/ask/size, IV, skew, tenor, open interest/volume, indicative premium for relevant target exposure (per share *and* per 100-share contract), and snapshot timestamps.
3. Show a properly qualified **risk-neutral/implied** probability of finishing above/below the target at a specified option expiry only if the quote surface and model support it. Never equate this with objective likelihood, probability of *touching* the target before a date, or a probability of achieving a planned earlier exit.
4. Narrate where the thesis sits relative to the implied distribution; how time, implied volatility, skew and prices affect exposure; whether the target is relatively far into the implied tail; and what inputs are missing or stale.
5. Check user comprehension in normal conversation: *'What is the market pricing around my horizon, how is that different from my expectation, and what does it cost to express that difference?'* Don't demand an unnecessary quiz or force the trader to agree with the market.

**Data-quality behavior:** Timestamp all spot and option inputs, state their source, distinguish bids/asks from midpoints and modeled values, and display currency. Never call snapshots executable without synchronized, broker-verifiable quotes. Where inputs are stale, absent, inconsistent, illiquid, or do not support a defensible distribution, show a **clearly labeled conceptual/illustrative landscape** and its limits. The user can then proceed to *conditional* strategy comparisons, but do not claim a validated market read or recommend/execute a live order.

**Stage-2 exit condition:** A presented, horizon-specific visual market picture plus a concise explanation of its implications, with the trader's thesis overlaid and data quality acknowledged. Record stage status as `confirmed-market-read`, `illustrative-market-read`, or `blocked-unavailable`. Preserve selected horizon, inspected expiries, assumed inputs and the user's interpretation in the process log. Strategy construction is a subsequent, distinct stage.

**Jensen–November pilot acceptance test:** For NVDA ~$200 by November 2027, ~$1,000 soft budget and no trading authorization, first orient around the actual November-2027 target and listed expiries bracketing it (e.g. November 19, 2027 if confirmed listed, and January 21, 2028), render the thesis overlay, explain market ranges and target probability only to the extent data supports, and inspect cost/quote reliability. Only *afterwards* revisit the shares/long-call/call-spread comparison using the same planned November-2027 exit and the original provisional assumptions. Treat this design as experimental: observe confusion and modify after the walkthrough rather than freezing the template now.

## Stage-2 refinement from interactive Jensen test — 2026-11-21

**Status:** User-observed product-design feedback added to this **draft documentation branch**. Not a shipped screen, verified option chain, production probability model, or approval to trade. Supersedes neither model contracts nor the existing provisional first-run walkthrough.

### Presentation order: picture before metrics, strategies before execution

Both thesis-first and market-first entry routes converge on the same sequence:

1. **Independent market picture first.** Answer the user's natural question, *"What outcomes are options pricing for this underlying at my horizon?"* Show a comprehensible terminal-price distribution or clearly illustrative proxy **before** asking the user to pick an options strategy. When the user already supplied a thesis, overlay it only after the independent distribution is intelligible; keep the original thesis distinct.
2. **Explain the picture.** State center versus spread, upside/downside tails, where a target lies, and uncertainty. A forward/mean is not a unique "market prediction," and the risk-neutral distribution is not the market's objective beliefs. Do **not** prompt a technical touch-versus-finish quiz before answering what the full distribution looks like.
3. **Offer five supporting lenses**, initially summarized in plain language and available for drill-down: (i) **horizon-matched ATM implied volatility** and assumptions; (ii) **expiry-specific risk-neutral probabilities** such as finish above/below a selected price, with touch/barrier outcomes separate and explicitly more model-dependent; (iii) **entire terminal price distribution** (bins or density, central quantiles, median, forward/mean, downside and upside tails); (iv) **put/call skew or volatility smile**, explaining relative option pricing without treating skew as proof of direction; (v) **implied-volatility term structure** over relevant listed expirations, explaining nearby versus later uncertainty without a fixed 6/12/18-month schedule.
4. **User thesis overlay and reflection.** Display user's target and date, any evolving alternatives, and where they sit in the distribution; explain the difference between market pricing and their conviction. Ask at most one clarifying question at a time only when it alters the analysis (e.g., touching versus finishing, maximum affordable loss); accept "I don't know" and offer a guided example.
5. **Separate strategy discovery and comparison.** A user can express multiple independent views: directional terminal outcome, path/realized volatility, implied-volatility richness, desired price participation, capital at risk, and expiration sensitivity. Don't infer "I think it will be volatile" means the user should sell options; do not infer "less volatility" means the user predicts low realized volatility rather than wanting lower strategy vega.
6. **Execution only afterward** as its own separate stage, first hypothetical and only with separate verified tools/authorization for live orders.

### Two depths, same calculations and safety standards

**Simple (default / retail):** Lead with one readable graphic and ~2–4 short sentences: current reference spot and date, selected forecast/expiry horizon, intuitive price-outcome distribution with target marker, one plain-English takeaway, and one concise "priced odds are not forecasts" caveat. Translate unfamiliar jargon ("the market prices a wide range") and optionally offer "Why does this look like this?" or "Explore strategies." Avoid making the user interpret five naked statistics, probability theory, a form, or a menu of structures before understanding the picture.

**Deep dive (opt-in / serious trader):** Use the *same* provenance-bound snapshot and distribution, then expand all five lenses: date-specific quantiles and bins/tail mass, forward versus median, expected-move method, volatility smile/skew at comparable deltas/strikes, term structure, bid/ask and spread widths, volumes/open interest, confidence/data-quality flags, dividends/rates, model/surface assumptions, touch versus finish, and scenario sensitivity. Experts may adjust horizon/strike/model views, but never silently replace market inputs with unverifiable ones. Let the user switch modes without losing answers or restarting.

**Both modes:** Display **data status** prominently: synchronized-calibrated / indicative-snapshot / illustrative model / unavailable. State source, as-of timestamp, currency, horizon, and whether statistics are risk-neutral. When a coherent, sufficiently liquid, arbitrage-checked option chain isn't available, show a **model illustration**, its spot/forward/rates/dividends/IV/tenor assumptions, and refrain from saying the resulting density was "read directly from the market." Never merge the prior **47%-assumed model** and later **50.44%-reported IV / $133.54 forward** into one verified chain-derived distribution; those are different inputs with unverified synchronization. Reconcile and recalculate before publication. Explicitly correct any "zero chance" wording: a simplified **~15% finish-above-$200** illustration was discussed, not a verified real-world probability and not a "touch $200" probability.

### Distribution and comprehension acceptance tests

- The main illustration shows a **price-at-expiry distribution** with price-labeled ranges (bins must be mutually exclusive and sum to ~100% after rounding), a clear plotted user-target marker when known, and a horizon label; supply quantiles/median/forward as separate concepts. Do not label a volatility-only band as a calibrated density or an expected move without its definition.
- Explain in ordinary language: the distribution is broad, its median is not its mean/forward, and "upper half" simply means above the modeled median; that alone is **not** evidence of edge. Option premiums depend on more than a single binary terminal-probability estimate.
- If a user asks about a **25% gain with open-ended upside**, calculate the target from the *dated reference spot*, then explore the underlying-share benchmark and affordable uncapped-upside calls; do not present credit spreads as if they preserve unlimited upside. For shares, avoid saying the user "avoids volatility": shares avoid paying an option's implied-volatility premium, **not** market price volatility. For calls, include option premium, expiry, time decay, implied-volatility exposure and 100-share multiplier.
- Before proposing a structure, capture whether the user's priority is **more upside exposure**, **limited downside/capital**, **lower sensitivity to option IV**, **income from premium**, or something else. Do not optimize only target-ROI or probability of profit. Show the stock baseline and all candidates on the same intended exit date.
- Test comprehension naturally: can a nontechnical user tell us (a) the range rather than a single prediction, (b) where their target falls, (c) priced vs objective probability, and (d) capped versus uncapped payout? A serious trader can additionally inspect inputs, skew, surface quality, touch/finish math and stress tests.
- No quote or math validation implied by the pilot. Real-time premiums, suitability, orders, saved paper trades and live execution require separate work.

### Feedback captured during the second Jensen simulation

The user liked the **five metrics**, but asked to **paint the whole distribution first**. The user corrected a spoken **"zero chance"** mistake, asked how probabilities distribute across price outcomes, explored trading a volatile path versus choosing an exposure with less IV sensitivity, then expressed a tentative **~25% price-recovery / uncapped-upside** preference. These were **exploration prompts**, not a final replacement of the earlier $200 thesis, no confirmed trading instruction, and no objective finding that option premiums are overpriced. The user explicitly requested an expert-depth conversation **and** a simpler mode for ordinary retail users.

## Required candidate: underlying shares (new from user review)

The baseline must be **buy the underlying and plan to exit at the trader's horizon**. It is not optional decoration; it is the control against which options' incremental value and risk must be explained.

Required stock card: share count (integer/fractional availability), cost, same-date P/L and return, dollar loss under a drop, no fixed expiry or time decay, uncapped price upside, full downside to zero, opportunity cost/capital, currency and any FX effects. Shares can be held beyond the proposed exit, unlike expiring options. Clarify that shares are not 'safe', and that **both stock and long calls have theoretically uncapped upside**, but calls offer leveraged convex exposure at premium/expiration/volatility cost.

Normalize options contracts to **100 shares per standard U.S. equity options contract** (unless adjusted) and show cost per share **and** per contract; do not confuse $13.25/share with $13.25/contract.

## Jensen — November pilot record

**Input:** NVDA recovery to about **$200 by November 2027**, approximately **$1,000 soft capital budget**, user's research/thesis accepted as supplied. January 21, 2028 options evaluated to give ~2 extra months beyond target exit. No real trade placed. These figures are USD.

**Provenance caveat:** Prior session reported NVDA Friday **closing price $125.53**; separately cited Friday **displayed options** of approximately $645 for 170/200 spread, $400 for 180/200 spread, and $1,310 for a 180 call. The stock-close and option premiums are **not a verified common-timestamp executable snapshot**. Do **not** publish those as a broker quote or declare a final trade recommendation.

**New mandatory stock example:** 8 shares at Friday $125.53 reported close = **$1,004.24**; at a $200 exit, proceeds $1,600 and **+$595.76 / +59.3%** before costs/FX/dividends. A $170 exit = +$355.76; a $100 exit = -$204.24; complete loss to $0 = -$1,004.24. Stock has no expiration and also uncapped upside.

**Conditional illustrative option comparisons:** An estimated November 19, 2027 exit with Jan 21, 2028 expiration, 47% constant IV, 4% interest and no dividends/fees (simple Black–Scholes model) gives:

| Candidate | Stated illustrative debit | At NVDA $170 (P/L) | At NVDA $200 (P/L) | Maximum loss / structural limit |
|---|---:|---:|---:|---|
| 8 NVDA shares at $125.53 close | $1,004.24 | +$355.76 | +$595.76 | $1,004.24 to zero; upside uncapped |
| $180–$200 Jan 2028 call debit spread | ~$400 | +$130 | +$751 | $400 premium; upside capped at expiration |
| $170–$200 Jan 2028 call debit spread | ~$645 | +$300 | +$1,233 | $645 premium; upside capped at expiration |
| Long $180 Jan 2028 call | ~$1,310 | -$347 | +$1,461 | $1,310 premium; leveraged upside uncapped |

**Important:** These are model-generated scenario values for comparing payoff geometry, not expected profits or fill quotes; exit volatility, volatility skew, time, exercise/assignment specifics, liquidity and trading costs can materially alter results. No model-implied probabilities were reliably calculated for the pilot. The $170/200 spread is a **provisional target-focused candidate**, not an objectively optimal recommendation. A soft budget is **not** the same as consent to lose the full amount.

## Strategy cards: labels must explain tradeoffs

Suggested dynamically assigned labels: **lower capital at risk**, **target-focused payoff**, **leveraged uncapped upside**, and **share ownership benchmark**. Labels are descriptive, not a fixed menu; do not present 'safe' versus 'aggressive' without explicit variables. Every card must show:
- Total cost/capital or buying power; maximum loss; relevant margin/assignment risks for complex structures.
- Same-scenario **dollar profit and ROI** and **profit per dollar at risk**; distinguish payout ratio from real probability of profit.
- What happens if the thesis is only partly right, wrong, late, or overshoots.
- Capped/uncapped upside and **why** that changes capital efficiency.
- Time decay, future IV/skew exposure, expiry versus planned exit, and liquidity/spreads/fees.
- Source timestamp, simulated/indicative/executable status, and currency.

## Product learning: preserve and correct

**Worked:** trader-stated thesis accepted; conversation recovered prior answers instead of restating all questions; stage structure reduced confusion; evaluating multiple capped and uncapped structures produced useful choice; early-exit and volatility stress revealed genuine tradeoffs.

**Needs hardening:** failed to include underlying shares until user requested it; too much research on whether thesis was true; confusion between stages 2/3/4; premature 'optimal' and 'aggressive' labels; uneven market data quality; output that sounded executable with unsynchronized prices; missing source/quote timestamps; accidental conflation of question-flow spec with persisted app functionality.

**Questions to log for each step:** prompt/why, supplied answer (or already known), normalized state delta, assumptions, evidence/tool input, computation/version, decision made or deferred, source of confusion, next branch, stage gate status. Keep a parallel **process log** separate from **strategy records**.

## Explicit backlog, not part of current session

1. Saveable **paper-trade ledger**: immutable hypothesis/market snapshots; simulated entry assumptions; mark-to-market & exit; reason-for-trade versus realized outcome; true hypothetical fill convention; user ownership and private/public access control.
2. Community sharing after a successful pilot: opt-in strategy/publication state, e.g. Telegram channel or group, with paper-only badges, standardized return bases, timestamps and anti-cherry-picking rules. **Not built or committed to as a launch platform.**
3. Objective archetypes to revisit later: target-return efficiency, low capital loss, probability of profit, maximum uncapped upside, drawdown sensitivity; don't silently optimize on one metric.
4. Implementation planning requires a separate selected build slice, acceptance tests, market-data license/venue feasibility, privacy/security review, and snapshot provenance tests.

## Immediate acceptance tests for v0.3

- A second user brings a new asset/price/date: system remembers prior answers, shows stage and next step.
- It always generates a properly sized **underlying buy/hold baseline** when tradable, and explains if infeasible.
- All candidates use identical target-date and price scenarios; options have expiration and implied-volatility stress, stock does not.
- Mixed timestamp quotes trigger **indicated simulation**, not executable prices.
- Labels show capital, loss, target payout, partial success, capped/uncapped upside and side-by-side stock comparison.
- No trade is marked paper-filled, saved, live, or published without a verified corresponding persistent event.

**Bottom line:** the **interview/decision spec** is reusable at v0.3; the **implemented and tested workflow** is not yet hardened. Run another complete pilot and verify calculations before promoting this into controlling product canon.
