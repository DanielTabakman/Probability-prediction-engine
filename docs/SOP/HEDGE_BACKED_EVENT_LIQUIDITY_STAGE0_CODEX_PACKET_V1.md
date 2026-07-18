# Hedge-backed event liquidity — Stage 0 Codex packet v1

**Thread role:** `codex_build`  
**Execution posture:** feasibility / evidence only  
**Parent charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md)  
**Active product frontier:** unchanged  
**Live orders / customer funds / treasury movement:** forbidden

## Goal

Determine, using the repository's existing Polymarket ↔ Deribit pipeline and fresh reproducible evidence, whether a recurring set of terminal BTC price-event contracts can be mapped to plausible static options hedges closely enough to justify a later minimum credible hedge-scanner build.

This packet authorizes **Stage 0 feasibility only**. It does not authorize a product surface, automated quoting, order routing, custody, or a live pilot.

## Why this matters

MSOS already compares event-market prices with options-implied probabilities. The unresolved question is whether qualifying event payoffs can be represented precisely, matched to sufficiently compatible option expiries and settlement rules, and priced with executable data rather than theoretical probability differences.

The continuation decision must be evidence-based before MSOS spends engineering effort on a hedge compiler or shadow market maker.

## Prerequisite

Use one of these safe paths:

1. preferred: begin from `main` after PR **#5384** is merged; or
2. if explicitly instructed to work before merge, base from `agent/charter-hedge-backed-event-liquidity` and do not modify the charter or its index links.

Before editing or running work, report any branch, file, or ownership overlap.

## Canon / relevant documents

Read only what is needed:

- `docs/VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`
- `docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`
- `docs/SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`
- `docs/SOP/PPE_MODULE_REGISTRY_V1.md`
- `docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md`
- `docs/SEMANTIC_CONTRACTS.md`
- `docs/SOP/REPO_LAYER_MAP_V1.md`

## Relevant code paths

Inspect and reuse before adding anything:

- `scripts/collect_cross_venue_snapshot.py`
- `scripts/run_cross_venue_scan.py`
- `scripts/run_cross_venue_backtest.py`
- `src/data/fetch_polymarket.py`
- `src/data/parse_btc_markets.py`
- `src/data/fetch_deribit.py`
- `src/viz/cross_venue_export.py`
- `src/viz/prediction_spread_probs.py`
- `tests/test_cross_venue_export.py`
- existing cross-venue collector, scan, tradeability, and backtest tests

## Current behavior

The existing pipeline:

- discovers BTC price questions from Polymarket;
- matches them to Deribit expiries;
- compares Polymarket YES probability with lognormal and options-chain probability estimates;
- exposes spread-cost proxies, alignment labels, snapshots, scans, and backtests.

It does **not yet prove**:

- exact resolution-time and resolution-index compatibility;
- a deterministic event payoff specification;
- a normalized static options hedge with bounded terminal replication error;
- executable synthetic bid and ask from the correct option-book sides and depth;
- the full fee, slippage, basis-risk, and duplicated-collateral stack.

Do not infer those capabilities from a probability-gap output.

## Required work

### A. Establish fresh evidence

Run the existing cross-venue collector and relevant scan/tradeability commands against fresh public data. Record:

- exact commands;
- UTC timestamps;
- generated artifact paths;
- any data-source, authentication, rate-limit, or schema failures;
- whether inputs are marks, mids, top-of-book quotes, or depth-aware executable prices.

Do not commit raw large artifacts or secrets.

### B. Select representative contracts

Evaluate up to **20** distinct current or recently archived BTC terminal-price event contracts. Aim for at least **10** when the available universe permits it.

For each candidate, record:

- event venue and contract identifier;
- exact question and full resolution-rule source;
- comparator and strike;
- resolution timestamp and timezone;
- resolution price source and calculation window;
- payout denomination and YES / NO mapping;
- event-market bid, ask, depth, fees, and collateral facts when available;
- matched Deribit expiry, index, expiry timestamp, multiplier, strikes, and available quote type;
- settlement mismatches and unresolved ambiguity.

If fewer than 10 suitable candidates exist, do not manufacture a sample. Report the actual count and why the universe is thin.

### C. Manual hedge witness

For each otherwise plausible candidate, construct or reject a static hedge witness:

- terminal `above` → normalized narrow call spread around the threshold;
- terminal `below` → normalized narrow put spread around the threshold;
- use listed strikes and actual multipliers;
- show terminal payoff at representative prices below, within, and above the spread;
- quantify maximum approximation error over the transition interval;
- state whether the hedge is truly executable, mark-based only, or unavailable.

Do not call a mark-based estimate executable.

### D. Cost and compatibility matrix

For every candidate, classify each item as known, estimated, unavailable, or not applicable:

- option bid / ask crossing cost;
- event-market bid / ask and fees;
- expected slippage and available depth;
- hedge legging reserve;
- expiry mismatch;
- timestamp mismatch;
- settlement-index mismatch;
- strike approximation error;
- duplicated collateral or margin burden;
- stale-data risk;
- maximum residual terminal loss.

Return one outcome:

- `ELIGIBLE_FOR_SCANNER_FEASIBILITY`
- `WATCH_EVIDENCE_INCOMPLETE`
- `REJECT_NOT_SAFELY_HEDGEABLE`

### E. Produce the feasibility report

Create:

`docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`

The report must include:

1. executive answer;
2. evidence date and commands;
3. data-quality and quote-type audit;
4. contract taxonomy;
5. candidate compatibility matrix;
6. at least three detailed hedge witnesses when evidence permits;
7. recurring rejection reasons;
8. qualifying-market frequency and observed depth;
9. the missing capabilities required for a credible Stage 1 scanner;
10. continuation recommendation: `GO`, `NARROW_AND_REPEAT`, or `STOP`;
11. explicit confidence and evidence gaps.

A `GO` requires evidence for all three charter claims:

1. recurring contracts are deterministically specifiable;
2. plausible discrepancies survive a conservative known-cost stack, or the precise missing executable data is obtainable;
3. settlement, collateral, and operational burdens appear potentially tolerable.

If executable prices or full resolution rules are unavailable, the result cannot be an unconditional `GO`.

## Minimal tooling rule

Prefer existing commands and manual analysis.

Only add a small research-only script when it materially improves reproducibility and cannot be achieved cleanly with existing code. Any new script must:

- live under `scripts/`;
- have pure logic extracted to `src/engine/` or `src/data/` only when justified;
- include focused tests;
- write only under `artifacts/hedge_backed_event_liquidity/`;
- contain no order-entry, credentials, signing, custody, or treasury functionality.

Do not add Streamlit or MSOS UI.

## Allowed write paths

- `docs/SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_FEASIBILITY_REPORT_V1.md`
- `scripts/hedge_backed_event_*` only if required for reproducibility
- `src/engine/hedge_backed_event_*` only for pure research logic and only if required
- `src/data/hedge_backed_event_*` only for narrowly scoped parsing/data contracts and only if required
- `tests/test_hedge_backed_event_*`

## Forbidden write paths

- `apps/msos-web/`
- existing user-facing `src/viz/` surfaces
- order-routing, signing, account, wallet, custody, or treasury code
- deployment configuration
- `.env` or secret-bearing files
- `docs/SOP/MSOS_FRONTIER.md`
- `docs/SOP/MVP1_FRONTIER.md`
- `docs/SOP/ACTIVE_PHASE_MANIFEST.json`
- phase queues, active direction, or relay selection state
- the parent charter, unless a factual contradiction is reported for founder review rather than silently edited

## Non-goals

- proving profitability from theoretical probabilities;
- building a general natural-language contract parser;
- supporting ETH, SOL, politics, sports, touch events, or multivariable contracts;
- placing or simulating live orders beyond offline shadow calculations;
- optimizing capital allocation;
- creating a market-making business plan;
- changing current MSOS product priorities.

## Acceptance criteria

- Fresh collector/scan evidence is recorded with reproducible commands and UTC timestamps.
- Candidate contracts are not reduced to question text; resolution source, time, and calculation semantics are inspected.
- At least 10 candidates are evaluated when the available universe allows; otherwise the shortage is evidenced.
- At least three detailed static-hedge witnesses are completed when suitable candidates exist.
- Quote inputs are correctly labeled as executable, top-of-book, midpoint, mark, model, or unavailable.
- Settlement and expiry mismatch are explicit, never silently treated as exact.
- Every candidate receives an eligibility classification and reason.
- The report separates options-implied pricing from physical belief probability.
- No active frontier, queue, product UI, execution, custody, or treasury code changes.
- Any new logic has focused tests.
- A draft PR is opened with the commands run, test evidence, artifact paths, and Coordination Status.

## Validation

Run the smallest relevant checks first, then the repository pre-push gate if code changed.

Suggested minimum:

```bash
python scripts/collect_cross_venue_snapshot.py
python scripts/run_cross_venue_scan.py
python scripts/run_cross_venue_tradeability.py
pytest -q tests/test_cross_venue_export.py
```

If code changed:

```bash
ruff check <touched Python paths>
pytest -q <focused tests>
python scripts/run_pushable_gate.py --pre-push
```

If external live-data commands fail, preserve the exact failure as evidence and continue with available archived fixtures or snapshots; do not fake a successful live run.

## Ownership / overlap warning

Only one agent may write the Stage 0 report or any new `hedge_backed_event_*` paths at a time. Do not modify PR #5384 while its charter branch is being edited by another agent.

## Required return

Include in the PR description and final response:

```text
COORDINATION STATUS
Agreement: aligned | partial | conflict | unknown
Compared: charter, packet, code paths, commands, evidence
Disagreement: <none or concise statement>
Evidence gap: <none or missing proof>
Ownership overlap: <none or overlapping paths/state>
Risk if unresolved: <none or consequence>
Recommended default: <one action>
Founder decision required: yes | no
```

Also return:

```text
AGENT CONTINUITY
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```
