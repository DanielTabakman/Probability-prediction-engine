# MSOS — Market Read First: implementation packet v0.1

**Prepared:** 2026-11-21  
**Status:** Proposed **implementation-ready plan** on the Jensen documentation PR; **not** selected into the active relay queue, merged, built, tested, or deployed.  
**Goal:** An ordinary investor can understand the *range of outcomes priced by options* **before** being asked to shape a personal belief or select an options strategy. A serious trader can open a **Deep dive** using the same underlying data, without a second contradictory market read.

**User research:** Jensen interactive simulation (2026-11-21). [Pilot protocol](./MSOS_STRATEGY_SESSION_PILOT_V0_3.md) · [Jensen walkthrough](./JENSEN_NOV_2026_LANDSCAPE_WALKTHROUGH.md) · [Handoff](./JENSEN_NOV_2026_SESSION_CLOSEOUT.md).

## 1. Repo reality — confirmed starting points (main, inspected 2026-11-21)

| Existing surface | Exact owner / code entry | Consequence |
|---|---|---|
| Customer-facing app | `apps/msos-web/` (Next.js/React/TypeScript) | Implement presentation and route/workflow within the existing MSOS shell, not a new unrelated app. |
| Strategy Lab entry | `apps/msos-web/src/app/strategy-lab/page.tsx` → `StrategyLabContent` → `StrategyLabClientShell` → `StrategyLabWorkSection` / `StrategyLabInteractivePanel` | This is the insertion path for the first guided market briefing. |
| Existing workflow | `apps/msos-web/src/lib/strategyLabWorkflow.ts` and `WorkflowStepper.tsx`: `compare → confirm → plan` | The read is **not yet a first-class stage**. Add it without breaking existing links or deep-link users. |
| Price distribution display | `PpeEmbedBoundary.tsx` → `LabeledDistributionChart.tsx`, driven by `ppeDisplayPayload.ts` `series_by_expiry` precomputed price/pdf arrays and optional quartiles/mean | **Reuse** this chart and expiry data for read-only market view. Do **not** reimplement probability math in TypeScript. |
| Asset selection and data | `StrategyLabClientShell.tsx` loads matching `DisplayPayload` and offers asset picker; available assets may include BTC/ETH/NVDA | Trust, method, data presence, expiry support and dividend limitations must remain asset-specific. Do not assume every asset has full curves or valid option quotes. |
| Standalone market read | `apps/msos-web/src/app/options-market-read/`, `OptionsMarketReadConsole.tsx`, and Python `src/viz/options_market_read.py` (`GET /v1/options-market-read`, v1.3) | Useful **copy and summary conventions**, but **this API is BTC-only**: `src/viz/options_market_read_assets.py` enables only BTC. It presently returns median, middle 50%, ATM IV and narrative, **not a full chain-calibrated density or all five metrics**. No NVDA call/fallback masquerading as supported. |
| Engineering boundaries | `AGENTS.md`, `docs/REPOSITORY_BOUNDARIES.md`, `docs/SOP/REPO_LAYER_MAP_V1.md`, `docs/SOP/MSOS_FRONTIER.md` | Use approved `MSOS_UI`/PRODUCT-PLANE slice for web work. Any PPE model/API enhancement is a **separately selected** PPE/UI or core slice. Do not silently change active queue or data contracts. |

**Key risk:** A display payload may contain a *lognormal reference* curve, not a rigorously calibrated options-chain-implied density. The UI must label `method`, `as_of`, `snapshot`, `asset`, `expiry`, and `trust` from actual supplied fields, without inventing provenance when absent. The existing Jensen 47%-assumed model and later 50.44%-IV illustration are separate and not a synchronized price surface.

## 2. What the first release should feel like

**Default (Simple, distribution first):**

> **What are options pricing for [asset] by [date]?**  
> Chart of prices at a selected listed expiration, with *price at expiration* on the horizontal axis and a plain-English explanation alongside it: **middle range, median, important tails, and uncertainty**. A trader-supplied target is an overlay, not a prerequisite.  
> Below it: “This is pricing-implied uncertainty, not a forecast.” A compact provenance state (market-backed / illustrative / stale, whichever evidence supports) and an obvious **Explore the details** disclosure.  
> Then a single **Compare with my view** action that advances into the pre-existing belief/comparison stage without losing asset, expiry, or prior thesis.

**Deep dive (optional):** Same graph, asset, date and snapshot with expanders for (1) matched-expiry ATM implied volatility; (2) **terminal** `P(S_T ≥ K)` when a validated source/model exists, with touch/barrier outcomes distinguished and not silently substituted; (3) fuller distribution bins/quantiles plus forward versus median; (4) skew/smile at comparable strikes/deltas **if available**; (5) IV term structure over **actually listed expiries**. Include available quote timestamps, reliability, liquidity, model and rate/dividend assumptions. Display “Unavailable for this snapshot” instead of fabricated metrics. Deeper view may expose method flags and sensitivity; it must not calculate a probability in frontend TS.

**Interaction contract:**
- Market-first and thesis-first entries both work; preserve original thesis and amendments separately in the eventual session record.
- The trader can switch Simple ↔ Deep dive without reloading a different market snapshot or resetting answers.
- Never force touch-versus-finish semantics or a complex questionnaire before showing the basic distribution. Clarify them *after* the map when they materially affect strategy design.
- A user can explore a conditional/illustrative read even if data is thin; do not mark it `verified`, and never imply a tradable quote.
- Market Read is distinct from **strategy candidate construction**, **same-horizon payoff comparison**, **simulated execution**, and **live execution**.
- The original $200 NVDA example and later +25% idea remain **different exploratory statements**; never silently overwrite the first with the second.

## 3. Implementation slices — do the smallest valuable thing first

### Slice A — MSOS_UI, PRODUCT-PLANE: simple-first briefing (first build)

**Allowed product work:** `apps/msos-web/` plus its colocated tests and UI styles. **Forbidden without separate selection:** PPE computation changes in `src/engine/` or `src/viz/`, rewriting option contracts, adding a new public API, enabling NVDA in the BTC-only API, order routing or unapproved cross-repo code.

1. Add a `MarketReadFirstPanel` (name provisional) to the Strategy Lab route, **before** interactive belief adjustment. Reuse `DisplayPayload`, `findSeriesByExpiry`, `PpeEmbedBoundary` / `LabeledDistributionChart`, `buildExpiryMarketContext`, and the existing selected asset/expiry state; do not duplicate a second fetch or PDF calculator.
2. Initially show **only the market curve** (not the user's belief curve), clear expiry axis and readable narrative about its shape. If the coherent provided series is missing, show a deliberate `illustrative/unavailable` state with an explanation, never an unlabeled generic bell.
3. Introduce an explicit **Market read → Compare view → Confirm view → Plan paper trade** progression. Use the existing workflow helpers/stepper; preserve old `/strategy-lab` and saved deep links. A local UI stage transition may ship as a pilot, but **do not claim durable completion/mandatory server enforcement** until Slice C verifies navigation/resume gates.
4. Make **Simple** the initial view. A non-destructive `Deep dive` expander reveals available quantiles, forward/median (where source gives them), ATM IV, provenance, trust flags and clear metric definitions; five-metric coverage is a **target**, not a pretense all fields already exist.
5. Keep the same snapshot and expiry when switching modes, advancing to comparison, and changing/returning asset. Reuse existing source labels and trust banners; use `as_of_utc` only when available. If only an application-generation timestamp exists, do not portray it as quote time.
6. Explain `upper half` as above modeled **median**, not a guarantee of edge. Distinguish **stock-price volatility** from **option-IV premium/vega** when users later explore strategies.

**Acceptance witness (A):** On a supported asset and expiry with valid data, a tester can open Strategy Lab and see a readable distribution + short explanation **before** the belief builder. Choosing Deep dive uses the same series; choosing Compare shows existing belief tools with unchanged asset/expiry. On NVDA with insufficient or model-only data, there is a prominent correct caveat. Old confirm/expression routes still work and are not mislabeled live trading.

### Slice B — data contract / quantitative validation (separate selection if needed)

1. Audit backend `DisplayPayload` field availability and whether chart data is **lognormal reference vs BL calibrated**, with exact source/quote timestamps, price/forward/dividend/rate inputs, `trust_state`, and expiry handling.
2. For every desired metric, map **source field → method → display qualifier**. Do not derive terminal CDF by naive sum of `pdf_pct` unless the array's normalization and price-grid spacing are formally specified and tested. Add a **backend-returned** terminal probability and labeled price bins only after a stable schema is selected and numeric tests verify integrals/tails.
3. Skew and term-structure plots require coherent cross-strike/cross-expiry source points. If not present, display `Not available` and keep the five metrics as educational definitions, not readings.
4. Respect supported asset list; equity options **NVDA** require their own verified chain quality, dividend/forward treatment and available expiry before any measured-market claim.
5. If new fields/routes are necessary, use a separately chartered PPE module/API task with versioned schema, backward compatibility and no extra TS option pricing.

### Slice C — workflow durability and decision handoff (following A/B evidence)

- Define a user/session record for `asset, expiry, snapshot_id, method, data_status, original_thesis, current_thesis, briefing_seen_at, read_status` and selected detail level. Persist only with an existing authorized store, or explicitly label session-only state. Prevent route/direct-link bypass of the **required conceptual briefing** before claiming production stage enforcement; preserve accessibility/navigation.
- Then connect to candidate cards, including the **underlying shares baseline** and same-target-date scenarios. Do not implement broker execution under this ticket.
- Evaluate Simple and Deep mode with one nontechnical tester and one advanced options trader. Capture comprehension and failure points, not just click-through.

## 4. Machine-checkable validation checklist

| Test | Expected |
|---|---|
| Default Strategy Lab with selected supported asset/expiry | Market read shown first, using **one** underlying distribution payload |
| Change expiry in briefing | Market curve, median/ranges/provenance update together; no stale second series |
| Toggle Simple ↔ Deep dive ↔ Simple | No altered numerical answers or lost asset/expiry/thesis |
| Data mode = loading / demo / thin_chain / degraded | Explicit, accurate state; no fabricated market probabilities or execution prices |
| NVDA chosen | Use actual available MSOS display payload with equity-specific caveats; **never** call BTC-only `/v1/options-market-read` as NVDA |
| Change or lack quote source/time | No misleading `fresh`, `live`, `verified`, or broker-executable claim |
| Probability surface lacks valid CDF or strike data | Probability/skew shown as `unavailable`, not synthetic “market implied” certainty |
| 25% appreciation and uncapped-upside user interest | Later comparison includes stock baseline and appropriate uncapped payoff candidate where feasible; not a credit spread pretending uncapped |
| Enter comparison after briefing | Existing belief/confirm/plan navigation preserved with same selected asset/expiry |
| Direct confirm/deep links and reload | Document pilot-only gap until durable read-status gate is implemented; no false claims about completion |
| Regression | Existing Strategy Lab / Options Market Read tests unchanged in meaning; tests/build/security boundary check pass |

**Suggested verification commands once on a runnable workspace:**
`cd apps/msos-web && npm run build`; `npm run test:options-market-read`; `npm test` only if an actual npm test script is available (currently package.json exposes `test:options-market-read`); Python `pytest` targeted to distribution/market-read modules as applicable; repository-authoritative `python scripts/run_pushable_gate.py` and `python scripts/check_repository_boundaries.py`. Run the UI journey witness / screenshots through the repo's established MSOS review process. **None of these commands were executed by writing this document.**

## 5. Release gates, priority and ownership

**Proposed order:** Build Slice A → inspect data/compute capability and select Slice B only for missing metrics → validate Slice C persistency/transition. Do not defer the whole simple experience until all five advanced metrics are available. A full advanced five-metric market report is **not** Slice A's completion claim.

**Release labels:**
- **Prototype/demo**: coherent distribution displayed, provenance clearly model/indicative, no trade suggestions, test only.
- **Market Read confirmed**: verified compatible market snapshot and calibrated method where claimed, numeric regression passed, meaningful reliability flags.
- **Strategy selection**: includes underlying benchmark and per-candidate cost/loss/capped-upside on same intended exit; not live execution.
- **Execution**: separate future selection and broker authorization, entirely out of scope.

**Steward boundary:** This packet is **not** a change to `docs/SOP/MSOS_FRONTIER.md`, `PHASE_QUEUE.json`, or master PPE canon. Before implementation, the authorized operator must reconcile the active frontier/worker leases and make an explicit **Slice A selection** into the repository's normal relay workflow. Do not displace a running worker by merging this docs PR or editing the active queue silently. In the new build, use the repo's required build packet/preset, PR and gate rules.

## 6. Prompt for the first build worker (concise handoff)

> Implement **MSOS Market Read First — Slice A only**. Follow `docs/MSOS_MARKET_READ_FIRST_IMPLEMENTATION_PACKET_V0_1.md` and `docs/MSOS_STRATEGY_SESSION_PILOT_V0_3.md` after the docs PR lands or by reading the PR branch. Inspect current `main` and the active `MSOS_FRONTIER`/worker lease first. Within the authorized `MSOS_UI`/PRODUCT-PLANE paths, make Strategy Lab show a plain-language, provenance-labeled distribution before thesis tuning, with a Simple default and non-destructive Deep dive toggle; reuse PPE display curves and existing asset/expiry selection. Keep the BTC-only standalone Market Read API unchanged and do not add TypeScript probability math. Show loading/degraded/demo states honestly. Preserve the old workflow routes. Add regression tests, run the repo-required gate and provide screenshot and data-quality witness. Report gaps for skew/term-structure/terminal CDF as a **separate proposed Slice B**, not fake completed metrics. Do not execute trades or silently change the controlling queue.
