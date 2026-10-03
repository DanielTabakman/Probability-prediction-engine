# HBCC Stage 0 single-contract compilation Codex packet v1

**Status:** DEFERRED — do not execute until Autobuilder completion and explicit founder selection  
**As-of:** 2026-07-20  
**Issue:** [#5396](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)  
**Parent product vision:** [`../VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`](../VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md)  
**Core-engine charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md)  
**Execution decisions:** [`../VISION/MSOS/MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md`](../VISION/MSOS/MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md)

## Execution gate

Do not launch this packet until all of the following are true:

1. the Autobuilder is complete;
2. the personalized-market vision, HBCC charter, and execution decisions are accepted on the default branch;
3. the founder explicitly selects HBCC Stage 0;
4. one implementation writer is assigned through the control plane;
5. current market-data and external-review assumptions are reconfirmed.

Until then, this document is a retained future handoff, not active implementation scope.

## Thread setup

```text
Implementation thread. THREAD_ROLE: codex_build.
Repository: DanielTabakman/Probability-prediction-engine.
Implement only issue #5396 after its deferred state is explicitly removed.
GitHub is the source of truth. Relay: off.
Read docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md,
docs/VISION/MSOS/MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md,
docs/VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md,
docs/VISION/MSOS/MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md,
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

It must record external hedge-lot granularity separately from customer denomination. The witness may analyze fractional customer claims conceptually, but it does not implement token issuance, batching, pooling, or live fractional hedging.

## Why this matters

The HBCC concept is not empirically validated until one real structure shows whether payout semantics, settlement, executable price, capacity, and residual exposure can be preserved honestly.

The witness must prevent the central failure modes:

> treating a finite-width call-spread ramp as though it were an exact binary payoff;

and:

> treating option-lot fractionalization as though it creates additional aggregate liquidity.

This is a system-level calibration and honesty test beneath the personalized market vision. It is not the product itself.

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

The implementation may use dataclasses, typed dictionaries, or Pydantic according to existing repository conventions, but must preserve these semantic objects.

### `ContractSpec`

Required fields:

- `contract_id`;
- `contract_type` (`strict_binary_above` or `capped_linear_call_spread`);
- `underlying`;
- `lower_strike`;
- `upper_strike` where applicable;
- `threshold` where applicable;
- `expiry_timestamp`;
- `payout_currency`;
- `payout_cap`;
- machine-readable piecewise payout;
- user-facing wording;
- semantic-equivalence proof state.

### `SettlementSpec`

Required fields:

- hedge index/source;
- exact expiry timestamp and timezone;
- settlement calculation;
- currency and multiplier;
- outage and fallback evidence where available;
- correction/finality evidence where available;
- evidence pointers;
- explicit unknown fields.

### `HedgeSpec`

Required fields:

- venue;
- instruments;
- sides;
- quantities;
- strikes and expiry;
- contract multipliers;
- executable bid/ask inputs and timestamps;
- displayed depth;
- normalized payoff;
- residual function;
- residual-bound proof type;
- settlement compatibility;
- external hedge-lot granularity;
- capacity methodology;
- constraining leg.

### `QuoteSpec`

Research-only output fields:

- indicative replication-cost bid and ask;
- pass-through fees;
- configurable risk and operational reserve;
- research-only platform fee input;
- available size at current displayed depth;
- quote timestamp;
- staleness rule;
- no-live-execution marker.

### `CompileDecision`

Required fields:

- verdict: `COMPILE_EXACT`, `COMPILE_BOUNDED`, `MODIFY_PAYOUT`, or `REJECT`;
- hedge grade;
- supported size;
- constraining leg;
- maximum residual values and locations;
- settlement flags;
- human-readable explanation;
- reproducibility identifiers.

## Required candidate pair

Using the same selected BTC expiry and adjacent or otherwise defensible liquid call strikes, compile and compare:

### 1. Strict terminal binary candidate

- Proposed payout: `$1` if settlement value is at or above the declared threshold, otherwise `$0`.
- The system must not label a normalized finite-width call spread as exact replication.
- It must calculate and display the full residual payoff function across terminal states.
- Verdict must be one of the canonical compile outcomes with machine-readable reasons.

### 2. Capped-linear terminal candidate

- Proposed payout: `$0` at or below `K1`, linear from `$0` to `$1` between `K1` and `K2`, and `$1` at or above `K2`.
- Test whether the normalized call spread preserves this terminal payoff under matched settlement semantics.
- Operational and settlement-basis risks remain separately disclosed even when terminal payoff replication is exact.

## Required outputs

For each candidate, produce:

- canonical `ContractSpec`;
- canonical `SettlementSpec`;
- selected hedge instruments and normalized quantities;
- live bid/ask and source timestamps;
- executable hedge entry cost on the correct book sides;
- trading-fee and configurable reserve inputs;
- fair-value / replication-cost range;
- research-only indicative bid and ask;
- terminal payoff table across a sufficiently dense price grid;
- maximum absolute replication error;
- maximum positive and negative residual;
- location and shape of replication error;
- settlement/index/timestamp compatibility matrix;
- external hedge-lot granularity;
- hedge-depth-derived aggregate capacity estimate;
- explicit statement that fractional claims do not increase aggregate capacity;
- stale-data and missing-depth flags;
- compiler verdict and human-readable explanation.

The JSON output must retain all raw inputs needed to reproduce calculations without refetching.

## Formal payout requirements

Let prediction-contract liability be `Y(S_T)` and hedge terminal payoff be `H(S_T)`.

The witness must calculate:

```text
residual(S_T) = Y(S_T) - H(S_T)
```

and report at minimum:

- `max_abs_residual`;
- `max_positive_residual`;
- `max_negative_residual`;
- terminal-price regions where each occurs;
- whether the bound is mathematical, grid-estimated, or simulation-estimated.

A finite grid alone must not be described as a mathematical global bound unless the piecewise payoff structure proves it.

## Settlement compatibility

Explicitly compare:

- underlying/index;
- expiry timestamp;
- timezone;
- settlement calculation;
- currency and multiplier;
- outage/fallback treatment where discoverable;
- correction and finality treatment where discoverable.

Missing official evidence becomes an evidence gap or rejection flag, not an inferred match.

## Capacity and granularity methodology

Estimate aggregate capacity only from observable executable depth and predefined risk limits.

Report:

- minimum external hedge lot;
- number of hedge lots executable at current displayed depth;
- aggregate claim notional represented by those lots;
- size executable at current price level;
- price-impact assumption, if any;
- which option leg constrains capacity;
- whether multi-level depth was available;
- whether the estimate is a lower bound, upper bound, or point estimate.

Do not infer meaningful capacity from open interest alone.

Do not imply that dividing a hedge lot into smaller customer claim units increases the aggregate liability that can be supported.

## Constraints

- Public-data, offline research only.
- No authenticated endpoints.
- No live orders, wallets, custody, signing, treasury movement, or token issuance.
- No unrestricted LLM parsing as settlement source of truth.
- Preserve exact distinction among replication cost, risk-neutral price, real-world probability, and user belief.
- Prefer the smallest reversible implementation.
- Reuse existing code only where semantics remain correct.
- Do not implement the API-first go-to-market, RFQ workflow, first-party site, fractional claims, internal netting, or custody architecture in Stage 0.

## Non-goals

- Selecting a prediction-market venue.
- Proving customer demand.
- Generating a full strike/expiry ladder.
- Narrative or marketing generation.
- Dynamic hedging.
- Path-dependent, barrier, touch, multi-asset, volatility, or conditional contracts.
- Production API or frontend.
- Live market making.
- Legal, tax, or regulatory conclusions.

## Acceptance criteria

- [ ] Deferred execution gate is explicitly lifted before implementation begins.
- [ ] One deterministic CLI produces a timestamped frozen JSON artifact and compact Markdown report.
- [ ] The report uses one real BTC expiry and two real option instruments with executable public bid/ask evidence.
- [ ] Binary and capped-linear candidates are generated from the same hedge structure.
- [ ] Strict binary semantics are never silently replaced by the call-spread ramp.
- [ ] Terminal payout and residual functions are independently testable and covered by unit tests.
- [ ] The call-spread/capped-linear equivalence is proven algebraically or piecewise, not only sampled.
- [ ] All settlement mismatches and missing evidence are explicit.
- [ ] Costs use executable sides rather than marks alone.
- [ ] Capacity is tied to displayed depth and names the constraining leg.
- [ ] Hedge-lot granularity is reported separately from customer denomination.
- [ ] The report states that fractional claims do not increase aggregate hedge capacity.
- [ ] Every candidate ends in a canonical compile verdict.
- [ ] Focused tests and lint pass.
- [ ] The final report makes one Stage 0 recommendation:
  - `CONTINUE_HBCC_STATIC_PAYOFFS`;
  - `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`;
  - `STOP_HBCC_CURRENT_PRIMITIVE`.
- [ ] The report includes the mandatory `COORDINATION STATUS` block.

## Validation commands or evidence

At minimum:

```text
python -m pytest -q <new focused tests> tests/test_cross_venue_tradeability.py
python -m ruff check <new script/module paths> <new focused tests>
python scripts/hbcc_stage0_single_contract_witness.py --help
python scripts/hbcc_stage0_single_contract_witness.py <frozen witness args>
```

The PR must include exact commands, pass/fail output, artifact paths, fetch timestamps, and selected instruments.

## Ownership / overlap warning

One implementation writer only for the new HBCC witness paths. Existing Polymarket Stage 0.1 code is reusable reference material but is not authorized for broad refactoring.

If another agent is editing shared cross-venue modules or tests, report the overlap before editing and choose non-overlapping new paths where possible.

## Completion boundary

Stage 0 is complete when the reproducible report is independently reviewable and reaches one explicit recommendation.

It does not authorize Stage 0.1, a full compiler, API, quote service, fractional claim system, first-party site, custody, or live action.

## COORDINATION STATUS

Agreement: aligned  
Compared: personalized market vision; HBCC charter; execution decisions; accepted Stage 0 and Stage 0.1 evidence; deferred issue #5396  
Disagreement: none; the packet remains the correct first witness but is no longer current build scope  
Evidence gap: no timestamped venue-agnostic single-contract compilation witness exists  
Ownership overlap: possible future overlap with cross-venue data and parser modules; default to new bounded paths  
Risk if unresolved: an implementation agent may start early, overstate binary hedge quality, or confuse claim fractionalization with aggregate liquidity  
Recommended default: retain this packet in deferred state until Autobuilder completion and explicit founder selection  
Founder decision required: no while deferred; yes when selecting implementation
