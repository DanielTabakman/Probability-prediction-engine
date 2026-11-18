# MSOS Concierge Research Pilot v0 — Human-operated Investable

**Status:** SELECTED PILOT DIRECTION (founder conversation, 2026-11-18); operational design proposal on a **draft PR**. Not an authorization for securities advice, live execution, fees, or production deployment.
**Business:** MSOS / Market Structure OS
**Mechanism:** Deliver the MSOS research loop personally with real traders; log each repeated step; automate only the parts that reliably create value.
**Near-term offer:** Free **MSOS Educational Research Session** — "Bring one market idea. Together we'll clarify it, look at what the market implies, explore hypothetical options structures, and understand the risks and trade-offs. You decide what, if anything, to do."

## Why this is the pilot, not a sales campaign or a software feature

The immediate unit of value is **one completed research loop per trader per thesis**, with a dated educational brief and a later check-in. We do not need the full Investable UI to deliver this manually. We do need a reproducible outcome and a way to see which steps clients want repeated. The eventual Guided experience automates these steps; Advanced uses the same underlying records and analytics.

Do not confuse three separate hypotheses:
1. **Service value** — does the participant leave with meaningfully clearer understanding?
2. **Product value** — can repeatable steps become a usable self-serve workflow?
3. **Business value** — does repeat behavior support monetization and a sustainable acquisition channel? A free research pilot alone does not establish #3.

## Customer and invitation

**First cohort:** 3 participants, then expand to 8–12 if early signal is positive. At least one active trader interested in options, one options-experienced trader able to challenge mechanics, and one further trader from an independent introduction. Avoid treating agreeable friends as demand evidence.

**Ask:** one real (or hypothetical) market idea, permission for a 30–45-minute educational session, permission to take minimal notes, and an optional 7–14-day follow-up. No account access, confidential positions, financial suitability details or promises of profitable trades.

## The full product loop, operated by hand

| Loop station | What facilitator does in pilot | Artifact/output | What eventually automates |
| --- | --- | --- | --- |
| 0. Develop thesis | Capture original idea verbatim. Clarify asset, direction/volatility interpretation, horizon, evidence, uncertainty; do not force numbers | **Thesis v0**: original and structured version, unresolved questions, participant confirmation | Guided adaptive interview, editable thesis |
| 1. Build | Show **illustrative**, supported structures for the view; let user manipulate key legs/assumptions; include no-strategy outcome | 1–3 example structures, entry/exit questions and limitations | Structure builder / editor |
| 2. Understand & test | Using actual available PPE/MSOS calculations where verified, compare historical/current market-implied context, scenarios, payoff, risks, costs, freshness and gaps. Never invent prices or imply unsupported backtests | **Dated scenario comparison** and clear assumptions | Options engine, scenario visualizations, provenance |
| 3. Share | Participant optionally talks through their thesis and report to facilitator. Public sharing is **not** part of this pilot; no publication without informed permission | Private recap, no public URL | Later: explicit publish/share surface |
| 4. Discover & adapt | Ask how they would evaluate a different trader's thesis; show an anonymized/hypothetical sample only where permitted; modify scenario under new assumptions | Notes on desirable discovery/copy/rebuild workflow | Later: search, adaptation, fresh-market rebuild |
| 5. Execute / decide | Participant makes their own decision, including no trade. MSOS neither advises a personalized transaction nor routes orders. Discuss conceptual difference between planning, orders and fills | Educational decision journal: questions and uncertainties, **not** execution state | Later: independently selected venue/execution, separate regulatory and technical gate |
| 6. Monitor & improve | Schedule an optional follow-up after a meaningful interval; check how market/thesis changed and what they learned. Don't equate right market call with strategy profitability | **Review v1**: original snapshot, new timestamp and market context, lessons and next idea | Monitor/review loop and product feedback |

**Success means completing the loop honestly**, even if data is missing, no structure fits, or the participant decides not to trade. This is a market-research exercise with educational output, not personal portfolio consulting.

## Run of show (first 45-minute session)

- **0–5 min — Context:** how they currently trade and use options; most frustrating decision step.
- **5–12 min — Thesis:** choose their idea; note original wording, asset, horizon, uncertainty; have participant confirm your interpretation.
- **12–25 min — Build and test:** illustrate one or two supported structures, compare adverse/upside/sideways outcomes, risk, max loss where defined, IV/time/path sensitivity, quote and data limitations.
- **25–35 min — Brief:** write a plain-English scenario comparison; ask participant to explain the biggest risks and what they still do not know.
- **35–40 min — Sharing/adaptation prompt:** would they show this to a peer? Would they want to explore someone else's version? No public publishing in v0.
- **40–45 min — Feedback and next loop:** what was useful; which step they would repeat; invite follow-up when the market changes.

## The tangible deliverable: one-page Educational Scenario Brief

- Date, asset, data as-of timestamp, source and availability limitations.
- Original thesis (participant wording), structured restatement, confidence/uncertainty, what could falsify the thesis.
- What current options data suggests versus the participant's belief; distinguish *implied market pricing* from *forecast*.
- 1–3 **hypothetical** option structures, leg assumptions and expiry, payoff/risk/cost comparisons, major sensitivities, tradeoffs and when no strategy is compelling.
- At least three scenario outcomes and what assumptions drive them; quote freshness and model uncertainty explicitly.
- Unanswered questions; participant's own takeaways.
- Follow-up date if agreed, and what changed at the review.
- Educational-scope statement: no specific recommendation, no suitability assessment, no execution. This language does **not** create an exemption from registration requirements.

## What to capture for product development (separate internal tracker)

For each session: anonymous participant ID and segment, original wording (with consent), current research tools, time spent per stage, each facilitator action, copied calculation or unavailable feature, exact comprehension/confusion moment, desired repeat feature, whether they requested a second session, whether they actually returned. Keep only necessary data; protect confidentiality.

**Automation backlog rule:** score a step only after it occurs in multiple sessions and saves substantial effort or improves participant understanding. Automate **clarification and recordkeeping first** if supported by evidence; never build a second options engine in the chat layer.

## Decision gates

- **After 3 sessions:** every participant leaves with a documented comparison or documented no-data/no-trade; record top recurring blockers and choose one small automation candidate. If the sessions merely entertain but do not clarify decisions, revise the offer.
- **After 6 observed loops:** proposed evidence bar: at least 4 understand and explain key trade-offs without prompting; 3 independently request or complete a second loop. These are directional qualitative thresholds, not statistical validation.
- **Before paid personalized work:** Ontario securities counsel reviews the actual script, outputs, potential compensation and crypto derivatives. Determine whether adviser/dealer registration, exemptions, permitted research characterization, licensed partnership, client disclosures, insurance and data practices are necessary. The service's actual content, not its title or disclaimer, drives analysis.
- **Before automation beyond a prototype:** check that users repeat an identifiable workflow, that necessary market data rights and reliability exist, and that current GitHub product-direction/worker queue are reconciled.

## Next three concrete actions

1. Invite today's trader to one free research session; bring one market hypothesis. No sales pitch or promise that the software already handles the full loop.
2. Prepare one sample scenario brief from the capabilities that **actually** run in existing MSOS. Label all hypothetical data and unsupported legs.
3. Complete the first session, capture its output and a precise manual-work log, then identify the first automation candidate. Recruit two additional testers and repeat.

## Relationship to GitHub charter

This pilot is the operating experiment associated with [MSOS_INVESTABLE_V1_CHARTER_AND_EXECUTION_PLAN.md](MSOS_INVESTABLE_V1_CHARTER_AND_EXECUTION_PLAN.md) and its G0.5 market-proof gate. It does **not** change ACTIVE_PRODUCT_DIRECTION.json, PHASE_QUEUE.json or production behavior; a separate founder-selection/steering reconciliation is needed to promote engineering implementation.
