# HBCC Stage 0 single-contract compilation Codex packet v1

**Status:** DEFERRED — do not execute until Autobuilder completion and explicit founder selection  
**As-of:** 2026-07-20  
**Issue:** [#5396](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)  
**Parent product vision:** [`../VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`](../VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md)  
**Core-engine charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md)

## Execution gate

Do not launch this packet until all of the following are true:

1. the Autobuilder is complete;
2. the personalized-market vision and HBCC charter are accepted on the default branch;
3. the founder explicitly selects HBCC Stage 0;
4. one implementation writer is assigned through the control plane;
5. current market-data and external-review assumptions are reconfirmed.

Until then, this document is a retained future handoff, not active implementation scope.

## Thread setup after authorization

```text
Implementation thread. THREAD_ROLE: codex_build.
Repository: DanielTabakman/Probability-prediction-engine.
Implement only issue #5396.
GitHub is the source of truth. Relay: off.
Read docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md,
docs/VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md,
docs/VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md,
and this packet before editing.
Do not change product direction or acceptance criteria.
Before editing, report ownership overlap and any disagreement with the charter.
Open a draft PR and include reproducible evidence.
```

## Goal

Build and run one offline, public-data BTC witness that starts from a real two-leg option structure and compiles two prediction-style terminal contracts:

1. a strict binary threshold candidate;
2. the capped-linear payout naturally represented by the normalized call spread.

The witness must quantify the complete terminal residual function, executable entry cost, settlement compatibility, displayed-depth capacity, and compiler verdict for both candidates.

## Product context

This witness is not the full product. The controlling product is a personalized market with a blank-box interface and API, supported by HBCC.

The witness is a system-level calibration test that asks whether one payoff primitive can be:

- represented honestly;
- priced from executable hedge markets;
- capacity-limited;
- compared on a common economic basis;
- emitted without silently changing its payout.

## Why this matters

The personalized-market thesis depends on bespoke claims inheriting liquidity from shared standardized instruments.

The witness tests the smallest defensible instance of that mechanism and prevents the central failure mode:

> treating a finite-width call-spread ramp as though it were an exact binary payoff.

## Binding prior evidence

The accepted Stage 0.1 recommendation remains:

```text
STOP_POLYMARKET_BRANCH
```

Do not fetch or require a live Polymarket contract. This is a venue-agnostic, hedge-first compilation witness.

## Relevant code paths

Inspect before editing:

- `scripts/hedge_backed_event_stage0_1_terminal_witness.py`
- `src/data/fetch_deribit.py`
- `tests/test_cross_venue_tradeability.py`
- `tests/test_cross_venue_export.py`

Preferred new paths unless repository conventions indicate a smaller coherent alternative:

- `src/hbcc/contract_specs.py`
- `src/hbcc/payoffs.py`
- `src/hbcc/compiler.py`
- `scripts/hbcc_stage0_single_contract_witness.py`
- `tests/test_hbcc_stage0_single_contract.py`
- `artifacts/hedge_backed_contract_compiler/stage0/`
- `docs/SOP/HBCC_STAGE0_SINGLE_CONTRACT_COMPILATION_REPORT_V1.md`

Do not broadly refactor the existing Polymarket witness.

## Required domain objects

The implementation may use dataclasses, typed dictionaries, or Pydantic according to repository conventions, but must preserve these semantic objects.

### `ContractSpec`

Required fields:

- `contract_id`;
- `contract_type` (`strict_binary_above` or `capped_linear_call_spread`);
- underlying;
- lower and upper thresholds as applicable;
- terminal timestamp and timezone;
- denomination and payout cap;
- exact machine-readable payoff formula;
- user-facing wording;
- semantic-equivalence proof state.

### `SettlementSpec`

Required fields:

- source/index;
- publisher and venue;
- observation timestamp and timezone;
- settlement calculation;
- currency and precision;
- outage and fallback treatment where official evidence is available;
- evidence pointers;
- explicit unknowns.

### `HedgeSpec`

Required fields:

- venue and instrument identifiers;
- option sides, strikes, expiry, quantities, and multiplier normalization;
- executable bid/ask inputs and source timestamps;
- displayed depth by leg;
- terminal hedge payoff;
- replication class;
- residual payoff formula;
- error-bound method;
- settlement and basis mismatches;
- fees, slippage, and configurable reserves;
- constraining leg and capacity methodology.

### `CompileDecision`

Required fields:

- verdict: `COMPILE_EXACT`, `COMPILE_BOUNDED`, `MODIFY_PAYOUT`, or `REJECT`;
- hedge grade;
- replication-cost range;
- research-only synthetic bid and ask;
- supported size;
- risk flags;
- machine-readable reasons;
- human-readable explanation;
- provenance identifiers.

## Required candidate pair

Use the same selected BTC expiry and two real call instruments.

### Candidate A — strict binary

Proposed terminal payout:

```text
Y_binary(S_T) = 1 when S_T >= K, otherwise 0
```

Requirements:

- never describe the finite-width call spread as exact binary replication;
- calculate the complete residual function;
- identify all state regions where the hedge differs;
- state whether any residual bound is mathematical, grid-estimated, or simulation-estimated;
- include the reserve or rejection logic.

### Candidate B — capped linear

For `K1 < K2`, proposed terminal payout:

```text
0                                      when S_T <= K1
(S_T - K1) / (K2 - K1)                 when K1 < S_T < K2
1                                      when S_T >= K2
```

Requirements:

- prove the normalized call-spread equivalence algebraically or piecewise;
- separately disclose settlement, execution, and operational risks;
- do not treat terminal payoff equivalence as complete risk elimination.

## Required market-data witness

Use timestamped public market data and retain all inputs required to reproduce calculations without refetching.

The witness must include:

- selected expiry and instruments;
- live executable bid and ask on the correct sides;
- available displayed depth;
- source timestamps and freshness;
- contract multipliers;
- official settlement semantics or explicit evidence gaps;
- fee and configurable reserve inputs.

Do not use marks alone for executable cost. Do not infer capacity from open interest alone.

## Required calculations

For each candidate calculate:

```text
residual(S_T) = Y(S_T) - H(S_T)
```

Report at minimum:

- `max_abs_residual`;
- `max_positive_residual`;
- `max_negative_residual`;
- terminal-state regions where each occurs;
- proof or estimation method;
- executable hedge entry cost;
- cost range after fees and reserves;
- research-only bid and ask;
- supported size and limiting constraint.

## Settlement compatibility

Explicitly compare:

- underlying/index;
- expiry timestamp;
- timezone;
- settlement calculation;
- currency and multiplier;
- outage and fallback rules where discoverable.

Missing official evidence must become an evidence gap or rejection flag, not an inferred match.

## Capacity methodology

Estimate capacity from observable executable depth and predefined risk limits.

Report:

- size available at current displayed levels;
- which leg constrains capacity;
- whether multi-level depth is available;
- any price-impact assumption;
- whether the result is a lower bound, upper bound, or point estimate;
- what would cause capacity to be recalculated.

## Required outputs

Produce:

1. one timestamped frozen JSON artifact;
2. one compact Markdown report;
3. independently testable payoff and residual functions;
4. one final recommendation.

The report must distinguish:

- demonstrated facts;
- calculations;
- assumptions;
- evidence gaps;
- unsupported claims.

## Constraints

- Public-data, offline research only.
- No authenticated endpoints.
- No live orders, wallets, custody, signing, token issuance, deployment, or treasury movement.
- No unrestricted LLM parsing as settlement source of truth.
- Preserve the distinction among replication cost, risk-neutral price, real-world probability, and user belief.
- Prefer the smallest reversible implementation.
- Reuse existing code only when semantics remain correct.

## Non-goals

- Building the personalized-market site.
- Building the API.
- Selecting a chain or custody architecture.
- Selecting a prediction-market venue.
- Proving customer demand.
- Generating a strike or expiry ladder.
- Narrative generation.
- Dynamic hedging.
- Path-dependent, barrier, touch, multi-asset, volatility, or conditional contracts.
- Production market making.

## Acceptance criteria

- [ ] The execution gate was explicitly confirmed before implementation.
- [ ] One deterministic CLI produces a timestamped frozen JSON artifact and compact Markdown report.
- [ ] One real BTC expiry and two real option instruments have executable public bid/ask evidence.
- [ ] Binary and capped-linear candidates are generated from the same hedge structure.
- [ ] Strict binary semantics are never silently replaced by the call-spread ramp.
- [ ] Terminal payout and residual functions are independently testable and covered by unit tests.
- [ ] Call-spread/capped-linear equivalence is proven algebraically or piecewise.
- [ ] Settlement mismatches and missing evidence are explicit.
- [ ] Costs use executable sides rather than marks alone.
- [ ] Capacity is tied to displayed depth and names the constraining leg.
- [ ] Every candidate ends in an allowed compiler verdict.
- [ ] Focused tests and lint pass.
- [ ] Final report ends in one Stage 0 recommendation.
- [ ] Report includes the mandatory `COORDINATION STATUS` block.

## Final recommendation set

The witness must end in exactly one:

- `CONTINUE_HBCC_STATIC_PAYOFFS`;
- `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`;
- `STOP_HBCC_CURRENT_PRIMITIVE`.

No result authorizes the full compiler, personalized-market site, API, on-chain claim deployment, or live action.

## Validation commands or evidence

At minimum:

```text
python -m pytest -q <new focused tests> tests/test_cross_venue_tradeability.py
python -m ruff check <new script/module paths> <new focused tests>
python scripts/hbcc_stage0_single_contract_witness.py --help
python scripts/hbcc_stage0_single_contract_witness.py <frozen witness args>
```

The future PR must include exact commands, pass/fail output, artifact paths, fetch timestamps, and selected instruments.

## Ownership / overlap warning

One implementation writer only for new HBCC witness paths. Existing Polymarket Stage 0.1 code is reference material and is not authorized for broad refactoring. If another agent is editing shared market-data or cross-venue modules, report overlap before editing and prefer non-overlapping paths.

## Completion boundary

Stage 0 is complete when the reproducible report is independently reviewable and reaches one explicit recommendation. It does not authorize the next stage.

## COORDINATION STATUS

Agreement: partial  
Compared: control-plane charter; personalized-market vision; HBCC core-engine charter; accepted Stage 0 and Stage 0.1 evidence; issue #5396  
Disagreement: this packet was originally ready for immediate execution; founder direction now defers all implementation until Autobuilder completion and explicit selection  
Evidence gap: no timestamped venue-agnostic single-contract compilation witness exists  
Ownership overlap: future overlap may exist with shared Deribit and cross-venue modules; default to new bounded paths  
Risk if unresolved: an agent could execute a valid future packet at the wrong priority or silently change a binary payout into a ramp  
Recommended default: retain this packet as future scope and do not run it until the execution gate is explicitly satisfied  
Founder decision required: no for deferral; yes before future execution
