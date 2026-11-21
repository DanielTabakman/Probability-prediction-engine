# MSOS — Market Read First: first external-tester runbook v0.1

**Date:** 2026-11-21  
**Status:** **Ready to run as a guided human-facilitated research session** using clearly labeled reference/model data. **Not** a deployed end-to-end product or proof of market-data correctness.  
**Related:** [Pilot workflow](./MSOS_STRATEGY_SESSION_PILOT_V0_3.md) · [Jensen run-2 findings](./JENSEN_NOV_2026_LANDSCAPE_WALKTHROUGH.md) · [Engineering build packet](./MSOS_MARKET_READ_FIRST_IMPLEMENTATION_PACKET_V0_1.md).

## What we are actually testing

**Primary hypothesis:** A new user can understand a dated distribution of option-*pricing-implied* terminal outcomes, locate their own investment view relative to it, and identify a meaningful strategy tradeoff without needing to understand five technical indicators first.

**Secondary hypothesis:** An options-experienced user can inspect assumptions, volatility, skew, term structure and data provenance instead of being forced into an oversimplified flow.

**Not under test:** Live execution, a paper-trading ledger, profitability, brokerage suitability, a calibrated NVDA volatility surface, the factual correctness of a trader's fundamental thesis, or that the web app actually enforces the mandatory stage. The run is **concierge roleplay**, not code acceptance testing. Do not take or send real orders.

### Who and what to recruit

- **Tester A:** someone comfortable with everyday investing but **not** professionally fluent in options.
- **Tester B:** someone who can meaningfully challenge option probability, expiration, IV/skew/term-structure and payoff assumptions. Different participants if feasible; friends are acceptable but record the relationship.
- A tester may bring a **real investment question** or elect a **fictional example**. Never ask them to disclose account numbers, holdings, credentials, total wealth, health data, or other personal financial information. Do not infer loss tolerance from a budget.
- If the chosen asset/horizon lacks reliable synchronized quotes, **do not improvise actual-market odds**. Offer the labeled Jensen NVDA model fixture below (or a verified supported dataset). State clearly that this tests the *experience*, not that a real market is available for that asset.

### Minimal invitation (copyable)

> I'm testing an early guided investing experience for MSOS. You don't need to buy anything or know options. I'd like to watch you explore what options prices imply about possible future prices, and see where the explanation becomes confusing. This is a guided prototype, not a live trading app or investment advice. Would you try a 20–30-minute session and tell me what works and what doesn't?

## Preparation and consent (facilitator)

1. Choose **one** dated, internally consistent, replayable snapshot/fixture for the entire run. Record asset, currency, dated spot, valuation time, expiry, source, assumptions, whether the graph is **calibrated**, **indicative**, or **model illustration**, and any missing metrics. **Do not combine** separately dated prices/IV quotes. The market-read API at `/v1/options-market-read` is **BTC-only** in the inspected v1.3 code; NVDA examples must not be represented as API-verified NVDA reads.
2. Have one visible distribution chart (price at expiry × probability mass/density), a correct plain-English summary, and a separately accessible **Deep dive** notes page. Ensure units and target horizon/expiry are labeled. If no authentic graphic exists for a chosen asset, say so and use the clearly marked test fixture rather than narrating unverified probabilities.
3. Explain: participation is voluntary; no real order, money movement or personalized trade recommendation; note-taking by default is **anonymous/minimal**. Ask permission separately before audio/video recording or using verbatim quotes. Avoid collecting identifiable financial details. Ask if the tester prefers a hypothetical example.
4. Do not pre-teach probability terminology or the correct answer; log each time the facilitator steps in. If an answer is unknown, say so without filling it with imaginary quotes.

## 20–30 minute guided session (one question at a time)

| Phase | Facilitator action | Observe rather than coach |
|---|---|---|
| **0. Entry (~2 min)** | “Tell me an asset or investment idea you’re curious about, or choose a fictional example. Is there a date that matters to you?” Accept **market-first** with no thesis. | Can they start without knowing options? Are date and target unintentionally required? |
| **1. Market picture (~5 min)** | Show **distribution first**. Say: “Here is the range of *end prices* this model/options snapshot prices for this specific date. It isn't a forecast.” Explain center, spread, and tails in 2–4 sentences. | Ask **afterward**: “In your own words, what is this picture saying?” Record their phrasing before correction. |
| **2. Belief overlay (~4 min)** | If they have a view, plot/describe their price and horizon on the same chart. Distinguish terminal-above from first-touch **only if relevant**. | “Where does your belief differ from these priced outcomes?” Can they articulate the distinction without being told they have an edge? |
| **3. Depth choice (~3 min)** | Offer “Keep it simple” or “Explore why.” If they pick deep, show the **five lenses** *only where actually supported*: horizon IV, expiry-specific finish probability, full distribution, skew/smile, term structure. Unsupported metrics show “Not available”. | Does advanced content clarify or create false confidence? Can they return to simple without losing context? |
| **4. Strategy tradeoffs (~5 min)** | Ask what they want to optimize: upside participation, downside cap, affordable capital, premium income, or lower option-IV sensitivity. Compare **buy shares** with up to two suitable options archetypes *if priced appropriately*. Show cap/uncapped, maximum plausible loss, expiration, path/vol sensitivity and cost per 100-share contract where relevant. | Do they grasp why a capped spread differs from shares or a long call? If they say “lower volatility,” does facilitator clarify **lower expected price movement** versus **less option IV exposure**? |
| **5. Close (~3 min)** | Say **no trade selected or executed**. Ask: “What was most useful? What confused you? What would you need to trust this enough to use it again?” | Capture spontaneous questions and what they expected next. **Do not solicit a real trade.** |

**Optional interruption test:** At any point, let the tester say “I don't know,” ask for a simpler explanation, or change their thesis. The facilitator must not restart, insist on a questionnaire, or overwrite the original answer without marking a revision.

### Reproducible *model-only* Jensen fixture (USD, not a live NVDA options quote)

- Dated reference spot: **NVDA $125.53**, reported Nov 20, 2026 close.
- Illustrative Nov 19, 2027 finish-price distribution from a **single-volatility lognormal model** using **50.44% annualized IV**, **$133.54 assumed forward**, and **364/365.25 years**. **Unverified chain synchronization and shape; not an objective forecast.**
- Terminal price bins (rounded): **below $100 ~37.3%; $100–$150 ~31.2%; $150–$200 ~16.9%; above $200 ~14.6%**. Median **~$117.64**, middle 50% **~$83.76–$165.22**, central 80% **~$61.70–$224.29**, forward/mean **$133.54**. Rounding can shift tenths. Bins partition 100% before rounding.
- **Touch $200 before the date:** **not calculated from this fixture**. Do not say the ~14.6% terminal probability is a touching probability, and do not claim touching probability is precisely twice finishing probability.
- Alternative pilot in the walkthrough used **assumed 47% flat vol and 4% rates**, giving different ranges and ~12.7% finish-above-$200. **Do not mix** it with the 50.44% fixture in one “market snapshot”.
- Example thesis: “NVDA about **$200 by November 2027**.” It was **not confirmed** whether “by” means *touch* or *finish above*. An exploratory **+25%** target would be **~$156.91** from $125.53; it is not an approved replacement thesis. Soft capital **~$1,000** is **not** permission to lose $1,000.
- Without synchronized verified option premiums, **do not show an executable iron-condor, put-spread, or call price**. If discussing structures, explain payoff geometry with clearly hypothetical premiums and do not call the market “expensive” purely because IV is high.

## Evidence capture sheet (duplicate one per session)

```text
Test ID / date:
Participant: novice / options-experienced (pseudonym only)
Mode: concierge / actual software (this runbook = concierge)
Starting route: thesis-first / market-first
Asset, time horizon and data source:
Model method + snapshot timestamp + quality flag:
Original thesis (if offered), including touch/finish status:
Any revised thesis (explicitly marked):
Selected depth: simple / deep / switched
First unaided description of the distribution:
Did they distinguish price range vs one expected number? yes / partial / no
Did they distinguish pricing-implied odds from forecast? yes / partial / no
Did they understand where their target falls? yes / partial / no / n/a
Did they distinguish capped from uncapped payoff? yes / partial / no / not tested
Did they understand potential loss and expiration? yes / partial / no / not tested
Number and nature of facilitator hints:
Confusing phrase or moment (exact words only with consent):
Most useful part / least useful part:
Data/provenance concern:
Suggested flow change (hypothesis, not approved feature):
Any accidental trading claim or misleading quote? yes / no (stop and fix if yes)
Consent to store notes: yes / no
No order, paper fill, recommendation or profit claim recorded: confirmed / problem
```

**Scoring rule:** A session is **informative**, not “validated,” if the tester actually saw the distribution and was allowed to talk through it without excessive coaching. Do not count a correct answer given only after several facilitator hints as unaided understanding. A session fails the **safety/trust** gate if an unsupported probability is represented as a market-derived fact, a fake option quote appears executable, or any trade is represented as placed. Stop that path, correct the statement, and log it.

## Findings review and decision gate

After Tester A and Tester B, produce a **two-column comparison of observed confusion vs proposed remedy**. Preserve raw, anonymized observations separately from hypotheses. Prioritize issues that *block comprehension* or *misstate data*, then issues in the Simple → Deep handoff, then optional polish. Do not generalize market acceptance from two users.

**Exit from concierge test to development:** We can identify the exact chart/copy behavior that let each tester describe the price range, locate a target, and interpret pricing-implied vs forecast, *or* the specific failures preventing those outcomes. That is enough to refine/implement Slice A. It **does not** validate calculated distributions, data licensing, automated workflow persistence, or paper trading.

**Deferred:** paper-trading design, execution authorization, real-money order routing, social sharing, strategy recommendation optimization, full equity options integration. Preserve the Jensen exercise as a **test case**, not as proof of a real investment edge.
