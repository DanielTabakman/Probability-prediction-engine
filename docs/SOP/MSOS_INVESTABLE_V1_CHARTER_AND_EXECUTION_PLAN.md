# MSOS Investable v1 — Product charter and executable plan

**Status:** PROPOSED / DRAFT FOR FOUNDER SELECTION · 2026-11-18
**Scope:** MSOS product decision and bounded build charter, not authorization to deploy, route live orders, or replace active relay priorities.
**Repository:** DanielTabakman/Probability-prediction-engine
**Inputs:** Product discussion and v0.8 working blueprint (18 Nov 2026), read-only repository audit, existing market-thesis v1 workflow and MSOS steering documents.

## Near-term operating plan: founder-selected concierge pilot

The **current company experiment** is the human-operated [MSOS Concierge Research Pilot v0](MSOS_CONCIERGE_RESEARCH_PILOT_V0.md): bring one trader's market idea through the research loop; deliver a dated educational scenario brief; follow up; log and prioritize repeatable steps for Investable automation. Start with three participants, not a software-first launch. Keep the advisory/registration boundary explicit and get Ontario legal review before paid, individualized advice. This operational pilot does not itself promote engineering work in the existing relay queue.

## 1. Executive decision

**Recommendation: CONDITIONAL GO for a small Investable validation slice, NOT a new platform rewrite.**

The core product promise is: a trader brings an intuition or directly specifies a trade; MSOS helps articulate the belief, compare it against available market evidence, construct an appropriate options expression, understand risks and costs, and save a decision. No trade is an acceptable outcome.

**Investable is the guided UX across existing domain modules.** Advanced exposes their underlying controls. Both modes operate on the SAME canonical owner-scoped thesis, strategy and analysis versions, pricing services and permissions. A mode switch is presentation state, not economic state. Experienced traders can begin with option legs and no thesis.

The product can ultimately include creator profiles, thesis sharing, strategy showcases, current-market rebuilding and independent execution, but those are not prerequisites for this first validation milestone.

### Why this makes sense

1. It closes a genuine novice-to-expert usability gap without duplicating the PPE quantitative engine.
2. It preserves the serious options product: sophisticated traders retain direct access, and the model separates a **market thesis**, a **strategy's legs and management rules**, **analysis** and **execution authority**.
3. It makes a testable claim: a real trader can move from an ambiguous intuition to an understood, independently editable paper plan using trustworthy market context.
4. It reuses tangible existing capabilities instead of treating the earlier codebase as disposable.

**Confidence:** ~85% in architectural coherence, based on the contract separation and existing code paths. **Customer demand is not validated** and must not be inferred from this charter.

### Material product risks / controls

- **Thesis becomes a distraction from actual trading:** require an analysis + editable strategy outcome in the first test, not merely a pretty chatbot.
- **AI overpromises precision:** user beliefs, market evidence and model assumptions must be separately labeled; no invented probability, quote or threshold.
- **False claims of tradeability:** availability and data freshness are explicit. The user must be able to stop at draft, watch-only, or no suitable trade.
- **Mode divergence:** one canonical record and services; id/version-parity tests before release.
- **Unauthorized user data:** server-derived ownership, deny-by-default on legacy/orphan records, cross-account negative tests, and no publication-by-default.
- **Unbounded first release:** start with a BTC happy path supported by actual analytics; don't promise generic six-leg optimization, all thesis types, full AI dialogue or brokerage access in v1.

## 1A. Company-level red team and market proof (added 2026-11-18)

**Separate architecture confidence from company confidence.** The ~85% earlier number described coherent modular architecture, not the probability of product-market fit, durable differentiation, customer acquisition, or venture economics. Business viability is **unverified**.

**Real competitive substitution exists:**
- OptionStrat already sells strategy building, payoff visualization and IV/time sensitivity: https://optionstrat.com/tutorials/options-builder
- Option Alpha already offers no-code options automation and public/private bot-template sharing: https://optionalpha.com/bots
- OptionsPlay guides traders through ideas and strategy comparisons: https://www.optionsplay.com/
- Robinhood Agents (rolling out to eligible US customers) supports natural-language trading research/strategy refinement and, with controls, options and crypto orders: https://robinhood.com/us/en/support/articles/robinhood-agents-overview/ . This does **not** establish that it offers the same crypto-options workflow, but general "AI trading assistant" is not a defensible standalone claim.

**Defensible wedge hypothesis to TEST, not assume:** intermediate, self-directed BTC/ETH options traders with a real market view but without a satisfactory workflow to compare that view with options-implied probabilities, evaluate multiple leg structures and management rules, and preserve an auditable decision record. Do not attempt to target novice options learners and highly advanced quants simultaneously for acquisition just because Guided and Advanced can coexist in the product.

**Company promise under test:** "Turn a market view into a transparent options trade plan, or discover why there is no good trade." Guided input is the access path, not the moat. Depth, trustworthy quantitative evidence, source freshness, decision records, and eventually market-relevant strategy rebuilding are potential differentiators that require comparison to alternatives.

### G0.5 — Pre-build commercial validation gate (before G2/G3 expansion)

Use the existing MSOS analytics and a clickable/conciege guided flow (human-guided where useful) rather than first building a generic AI agent.

1. Recruit **10–12** identifiable target traders with options experience (not friends giving courtesy opinions). Document current workflow and which competitor/tool substitutes.
2. Observe **5–6** traders on their own thesis with current market conditions. Require an independently understood saved plan, explicit no-trade capability and a baseline comparison to their current tool.
3. Invite each to return unprompted in ~7–14 days with a second real thesis; count actual repeat usage. Do not claim usage without returning evidence.
4. Ask for a concrete paid pilot, paid reservation, or usage-based commitment, with explicit price and delivery expectations. "Sounds cool" is not willingness-to-pay evidence.
5. Record likely reach/acquisition channel, data cost, options-market coverage, and legal/compliance review need (especially if positioning evolves into individualized recommendations or broker routing).

**Provisional go/no-go learning thresholds (not statistical proof):** at least 4/6 complete a useful plan without handholding, 3/6 independently return with another idea, and 2 credible paid-pilot commitments or comparable costly commitments. If results miss, diagnose segment/value promise before expanding BUILD. A genuine failure to differentiate from OptionStrat/Option Alpha/Robinhood should trigger a segment or positioning change, not a larger feature backlog.

**Revised sequence:** G0 founder selection and canon reconciliation → **G0.5 market proof with low-code/conciege tools** in parallel with G1 ownership/security verification and limited G2 prototype → then full G2/G3 engineering → G4 integrated witness → G5 expanded trader validation → G6 share/rebuild by evidence → G7 live execution via dedicated safety/legal gate. G0.5 may guide *which* of G2/G3 to build, not merely rubber-stamp them.

**Principal company risks to quantify:** customer acquisition/distribution, monetization vs broker-subsidized free tools, third-party market-data quality and rights, trust in model outputs, regulatory characterization of guidance, and whether crypto options is a big enough initial segment. Do not call the current design a proven company until those are measured.

---

## 2. Existing code and gaps — verified by reading source, NOT runtime

**Reuse candidates:**
- apps/msos-web/src/lib/strategyLabWorkflow.ts: Compare → Confirm → Plan.
- apps/msos-web/src/lib/marketThesis.ts and apps/msos-web/src/app/api/theses/market-thesis/route.ts: versioned market-thesis.v1, sync and comparison.
- apps/msos-web/src/lib/msosWorkflowStore.ts and related thesis/expression routes: owner-scoped persistence and paper records.
- apps/msos-web/src/components/ExpressionPlanningPanel.tsx: current paper-plan UI.
- src/engine/market_thesis.py and existing Python options analysis/display contracts: retain math authority.

**Unproven or missing:** complete adaptive-guidance UX; confirmed Guided/Advanced parity; flexible truly editable option contracts/leg quantities and rule-driven analysis; public publish → second-person rebuild flow; live multi-leg execution. Existing expression records may use preset structures and simulation labels; do not describe them as proven live trading.

**Security finding to address:** apps/msos-web/src/lib/snapshotReview.ts ownerMatches presently permits a match if the owner column, request owner or stored owner is absent. This is a possible access-boundary weakness, **not an established exploit**. Review its callers, legacy data and identity provisioning before expanding cross-user surfaces.

## 3. Canon and sequencing conflict — do not silently override

The repository's ACTIVE_PRODUCT_DIRECTION.json and MSOS_FRONTIER.md currently steer trader-workflow-integration-v1 (as of 2026-06-30) and the older 15-second market-implied-view promise. PRODUCT_THESIS.md and PRODUCT_FOCUS_PLAYBOOK_V1.md also constrain AI assistants and auto recommendations. The proposed Investable guided flow is a meaningful direction expansion, and should be chosen explicitly by the founder before promoting it into the active build queue.

The default is **this PR is proposed charter only**. Do not alter ACTIVE_PRODUCT_DIRECTION.json, PHASE_QUEUE.json, relay manifests, active worker leases, or production behavior in the charter PR. After founder selection, the authorized control-plane steward must run PRODUCT_DIRECTION_PIVOT_V1.md procedures, reconcile overlap with existing issue #5491, and create bounded implementation tasks. Do not create duplicate BUILD work.

## 4. Thin vertical slice (first credible Investable experience)

**One happy path:** user enters a rough BTC directional view, clarifies target and horizon, reviews a clearly labeled market comparison, confirms an editable thesis, chooses/edits an actually supported two-leg BTC options structure, receives source-dated payoff/risk analysis, saves a paper plan, and opens the same saved records in Advanced mode.

**One ambiguity/safety path:** user says “BTC volatility will go up.” Guided distinguishes larger realized price moves from more expensive options (implied volatility), allows “I don't know,” and preserves an unresolved draft rather than silently manufacturing a forecast or trade.

**Advanced-first path:** user starts from option legs without a thesis wizard and can analyze the same supported structure. No artificial thesis requirement.

This first slice is **not** an unrestricted multi-leg builder, automated order engine, personalized recommendation, public feed or full conversational agent. Suggested prompts can be deterministic and typed initially; any LLM assistance must be separately bounded by prompt-injection/privacy policy and must not hold trading authority.

## 5. Gate-based implementation sequence

| Gate | Deliverable / owner lane | Required acceptance evidence | Dependency |
| --- | --- | --- | --- |
| G0 — Direction & contract | Founder selects this wedge; control-plane steward reconciles current canon, issue #5491, authorizes bounded BUILD; schema owner maps old thesis/expression to canonical ID/version | No conflicting accepted product direction; migration fixtures, no duplicate writable records | FIRST; no production code until selected |
| G1 — Secure owner + persistence | Backend lane: owner identity and history boundaries; invalid/missing owner denied; private drafts; version semantics and provenance | Auth negative tests (two accounts, anonymous, orphaned rows), save/reload/version tests; snapshot review owner audit documented | G0; may overlap UX prototyping |
| G2 — Guided thesis | UX lane: free-text start, one useful clarification at a time, editable summary and explicit user confirmation | BTC directional happy path plus volatility ambiguity and “I don't know”; no invented precision; preserve original text | G0/G1 contracts |
| G3 — Strategy + analysis | Quant/UI lane: one genuinely editable supported two-leg structure; existing Python math; cost/risk/market freshness; no-trade outcome | Cross-mode leg/assumption ID parity, real quotes or clearly labeled unavailable state, risk/payoff regression tests, paper-save witness | G1/G2 |
| G4 — Cross-mode witness | Integration/test lane: Guided ↔ Advanced over identical IDs/versions; Advanced-first; errors/reload/paper history | Automated regression + staging manual walkthrough, screenshots; no user data bleed, no orders | G1–G3 |
| G5 — Trader validation | Product lane: five representative trader sessions, note completion/friction and whether the analysis changed decisions | At least 4/5 reach understandable saved analysis without developer intervention; at least 3/5 distinguish thesis from market belief and trade; documented failure reasons and demand signals | G4 |
| G6 — Share & rebuild (separate next chapter) | Sharing lane: immutable thesis publication; dated strategy showcase; second account opens and rebuilds a NEW private position using new market data | Cross-account authorization tests, stale/expired-contract guards, provenance and explicit new user decisions | Selected only after G5 |
| G7 — Live execution (later chapter) | Exchange lane: opt-in account permission, quote limits, bundled fill behavior, idempotency, reconciliation | Dedicated design/security/reliability gate and broker/venue witness; never inferred from G4 | Separate founder selection |

**Release decision after G5:** proceed to public Share/Rebuild only if traders complete and value the core workflow. If they do not, simplify or change the UX, rather than expanding to social infrastructure. Tester targets are proposed learning thresholds, not promises of traction.

## 6. Hard invariants

- Thesis = user-stated market belief and its provenance; user-owned original wording and confirmation preserved.
- Strategy = option legs plus entry/exit/management rules; a rule trigger is an attempt, never proof of fill.
- Analysis = dated risk/payoff model under documented assumptions; cannot overwrite thesis or silently imply tradeability.
- Execution = separate per-trader permission, venue, order limits and fills; not inherited from copying/showcasing.
- Guided and Advanced = one canonical truth and one auth model; presentation switch cannot silently rewrite economic meaning.
- Sharing is thesis-first, with dated historical strategy showcase; rebuilding creates new owner-owned contracts, not a literal stale copy.
- Records are private by default; optional future profiles/reputation are separate and deferred.

## 7. Engineering handoff packet template (for the first selected BUILD)

**Goal:** Ship G0–G2 without expanding into a second engine or public publication.

**Relevant code:** marketThesis.ts; market-thesis route; msosWorkflowStore.ts; msosWorkflowAuth.ts; snapshotReview.ts; StrategyLabInteractivePanel.tsx; ThesisConfirmationPanel.tsx; Python market_thesis.py and schema; current tests under tests/.

**Required behavior:** preserve existing market-thesis.v1 data, add backwards-compatible typed draft/confirmation semantics, prompt disambiguation, owner-safe save/reload, Guided/Advanced identical IDs, and no runtime trade authorization.

**Non-goals:** replace PPE math, new brokerage credential flow, recommendation engine, broad thesis taxonomy, social directory, scoring/badges, auto trading.

**Validation:** existing focused pytest and Next.js build witnesses plus newly added auth/version/guidance/parity tests; staging human walkthrough with evidence. Follow repo pushable gate and ownership/worker-lease rules for code changes.

**Ownership overlap:** market-thesis workflow issue #5491 and ACTIVE_PRODUCT_DIRECTION steering documents. Confirm one writer per file/queue and avoid duplicate chapters.

## 8. Coordination status and founder executive decision

- **Agreement:** Partial. The new product architecture is internally coherent and compatible in principle with existing code, but not yet adopted into GitHub's older active strategy.
- **Compared:** v0.8 working blueprint; code routes/store/auth; docs/SOP/MARKET_THESIS_WORKFLOW_V1.md; docs/SOP/ACTIVE_PRODUCT_DIRECTION.json; docs/SOP/MSOS_FRONTIER.md; docs/PRODUCT_THESIS.md; repo's control-plane rules.
- **Disagreement:** A guided, potentially conversational Investable journey is not currently an approved BUILD priority; older canon scopes an AI assistant out.
- **Evidence gap:** No fresh staging/prod E2E tests; user preference/market demand unproven; flexible builder and rule-aware analysis not established.
- **Ownership overlap:** existing market thesis #5491, current active UX backlog, multi-agent relay.
- **Risk if unresolved:** Agents could implement a second engine or start an unselected chapter, or mistake chat draft for source of truth.
- **Recommended default:** Accept this as a reviewable proposal; select G0 explicitly, then run normal pivot/queue reconciliation before implementation.
- **Founder decision required:** **Yes — approve or reject changing the active product wedge and work queue.** Technical details may default to the bounded two-leg BTC slice once selected.

## 9. Not included in this PR

No code deployment, no actual order routing, no changes to production permissions, no claim of completed security audit, no silent edits to active steering files or queue. This document becomes controlling only through the normal founder-selection and accepted-GitHub-canon process.
