# API / Distribution Autonomous Operator v1

**Status:** Founder-authorized operating instruction.  
**Lane:** API / Distribution.  
**Canonical repo:** `DanielTabakman/Probability-prediction-engine`.  
**Execution system:** existing PPE control plane and existing Autobuilder/factory; do not create a second API pipeline.  
**Primary goal:** continuously advance the approved API product queue from charter → implementation → validation → staging → production → external acceptance → closeout, then continue to the next eligible API product.

## Start here

An API-lane Cursor/Codex agent should load, in order:

1. `docs/API/API_LANE_CHARTER_V1.md`
2. this file
3. `docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`
4. `docs/SOP/THREE_TRACK_COORDINATION_HANDOFF_V1.md`
5. `docs/SOP/ACTIVE_PHASE_MANIFEST.json`
6. `docs/SOP/PHASE_QUEUE.json`
7. `docs/SOP/PHASE_CHAPTER_BACKLOG.json`
8. the selected product charter / phase plan / evidence record

GitHub `main` is source of truth. Local Cursor state is only a working surface.

## Founder delegation

The founder has authorized the API lane to **keep working without asking for routine implementation choices**.

Use the smallest reversible implementation that satisfies accepted product intent. Resolve normal engineering details with code/tests/evidence. Continue automatically after green validation and accepted merge authority.

### Stop for founder input only when

- a new user-facing product would consume Qatom slot 4 or 5;
- the proposed work changes financial/product meaning rather than distribution;
- two accepted canon documents require materially different product outcomes;
- commercial/payment terms, credentials/secrets, or an irreversible external action require a human choice;
- a requested external action cannot be performed from the available authorized systems;
- safety/legal/compliance meaning would materially change the product.

Do **not** stop for naming, file layout, test strategy, ordinary API validation, reversible rate protection, documentation wording, routine refactors, or other engineering implementation details.

## Continuous operating loop

Repeat until the API queue is terminal or a true founder decision is required:

1. **Sync and inspect**
   - read current `main`;
   - inspect active manifest, queue, backlog, open PRs, exact merge/runtime evidence;
   - never trust stale READY state over newer terminal evidence.

2. **Reconcile stale state**
   - if an active manifest points at a chapter whose product is already merged and whose queue/backlog is terminal, reconcile it through the existing PPE closeout/selection machinery;
   - never rebuild a terminal chapter merely because a manifest is stale.

3. **Choose the highest-priority eligible API product**
   - use the existing PPE queue/control plane;
   - do not create a second API backlog;
   - one writer owns shared control-plane state.

4. **Charter before building**
   - if the user-facing product exists but its API contract does not, create/freeze the API contract, acceptance criteria, allowed paths, tests, staging/release requirements and rollback boundary;
   - merge charter/control work before dependent implementation when shared interfaces would otherwise drift.

5. **Execute with the existing machinery**
   - use the existing Autobuilder/factory for clean bounded BUILD packets when eligible;
   - use an isolated API worktree/local implementation agent for partner acceptance, external conformance, or work that is not a clean factory slice;
   - API is a lane; Autobuilder is an execution engine.

6. **Validate**
   - contract/schema tests;
   - deterministic/numerical invariants where applicable;
   - regression protection for existing product APIs;
   - isolated staging before production when required.

7. **Review and merge**
   - compare exact PR/head against charter and acceptance criteria;
   - require current CI/evidence;
   - use recorded merge authority; do not widen it silently.

8. **Release and accept**
   - production promotion receipt;
   - external request/response witness;
   - monitoring and rollback witness;
   - partner/Qatom docs match deployed behavior.

9. **Close**
   - terminalize the selected chapter through existing PPE machinery;
   - update evidence;
   - continue immediately to the next eligible API product.

## Current product order

### Slot 1 — Options Market Read

**Finish first.** The product and production API already exist. The remaining job is `options_market_read_partner_acceptance_v1`.

Use:
- `docs/SOP/SPRINT_OPTIONS_MARKET_READ_PARTNER_ACCEPTANCE_V1.md`
- `docs/SOP/PHASE_PLANS/options_market_read_partner_acceptance_v1_relay.json`
- `docs/SOP/OPTIONS_MARKET_READ_PARTNER_ACCEPTANCE_V1_EVIDENCE_STATUS.md`
- `docs/API/QATOM_OPTIONS_MARKET_READ_PARTNER_DECISIONS_V1.md`

Do not redesign the financial semantics. Finish conformance, docs/help parity, staging/production witness, external acceptance, monitoring and rollback, then close.

### Slot 2 — Best Exposure

After Slot 1 is moving cleanly or terminal, charter and implement the Best Exposure API using existing approved PPE/MSOS product logic.

Default user job:

> Given an asset, a belief about where/when it may move, and relevant loss/payoff constraints, return the approved exposure structure(s) that best fit that belief and explain the tradeoffs.

The first contract should prefer reuse over invention. Reconcile with existing:
- Options Made Simple / best-fit expression ranking;
- Exposure Menu;
- Options Horizon / date-horizon logic;
- existing payoff and scenario primitives.

Expected input families:
- asset;
- direction and/or target price/region;
- target date or bounded date range;
- optional maximum loss / risk budget;
- optional payoff/exposure preference.

Expected output families:
- best-fit approved expression;
- useful alternatives when materially different;
- cost/debit or capital-at-risk representation;
- maximum loss where defined;
- maximum gain where bounded;
- breakeven(s) where defined;
- scenario/payoff comparison at the user's horizon;
- timing/expiry sensitivity;
- data timestamp, method and limitations.

Keep execution/order routing out. Do not silently transform educational decision support into discretionary trading.

### Slot 3 — Exposure Compare

Default disposition: **do not consume a separate Qatom slot unless evidence shows a distinct product lifecycle.**

Prefer implementing compare as a mode/capability of Best Exposure when the same contract, inputs, data and release lifecycle can serve both. Only charter slot 3 separately if there is a materially distinct user job.

### Slots 4–5

Reserved. Stop before assigning either slot without a new founder product decision.

## Superseded standalone primitive

`msos_implied_range_api_v1` / issue #5501 is **not an active standalone API product** under the product-slot policy.

Do not auto-materialize or build `GET /v1/implied-range` merely because an older packet exists. Implied-range calculations may be reused or implemented internally when required by an approved product contract, without consuming a Qatom product slot.

## Decision rule

> Keep moving. Prefer existing product logic, bounded reversible changes, evidence, and the existing factory. Ask the founder only when the product decision itself changes.
