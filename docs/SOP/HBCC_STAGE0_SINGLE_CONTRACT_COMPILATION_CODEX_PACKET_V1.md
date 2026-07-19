# HBCC Stage 0 single-contract compilation Codex packet v1

**Status:** PROPOSED — bounded implementation handoff  
**As-of:** 2026-07-18  
**Issue:** [#5396](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)  
**Parent charter:** [`../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md`](../VISION/MSOS/MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md)

## Thread setup

```text
Implementation thread. THREAD_ROLE: codex_build.
Repository: DanielTabakman/Probability-prediction-engine.
Implement only issue #5396.
GitHub is the source of truth. Relay: off.
Read docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md,
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

## Why this matters

The HBCC concept is not validated until one real structure shows whether payout semantics, settlement, executable price, and capacity can be preserved honestly.

The witness must prevent the central failure mode:

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

The implementation may use dataclasses, typed dictionaries, or Pydantic according to existing repository conventions, but must preserve these semantic objects.

### `ContractSpec`

Required fields:

- `contract_id`;
- `contract_type` (`strict_binary_above` or `capped_linear_call_spread`);
- `underlying`;
- `lower_strike`;
- `upper_strike` where applicable;
- `resolution_timestamp`;
- `currency`;
- `payout_min`;
- `payout_max`;
- `formal_payout_description`;
- `user_facing_question`;
- `semantic_equivalence_status`.

### `SettlementSpec`

Required fields:

- `source_index`;
- `publisher_or_venue`;
- `expiry_timestamp`;
- `timezone`;
- `calculation_method`;
- `currency`;
- `multiplier`;
- `outage_or_fallback_evidence`;
- `evidence_urls_or_pointers`;
- `evidence_gaps`.

### `HedgeSpec`

Required fields:

- instrument names;
- long/short sides;
- strikes and expiry;
- quantities and normalization;
- bid, ask, displayed quantity, and fetch timestamp for each leg;
- executable debit and executable unwind credit where available;
- fee assumptions;
- reserve assumptions;
- terminal hedge payoff definition;
- constraining leg;
- displayed-depth capacity;
- capacity-method label.

### `ResidualAnalysis`

Required fields:

- contract payoff function;
- hedge payoff function;
- residual function;
- piecewise regions;
- `max_abs_residual`;
- `max_positive_residual`;
- `max_negative_residual`;
- locations/regions of extrema;
- bound method (`mathematical_piecewise`, `grid_estimate`, or `simulation_estimate`);
- sampled payoff table for presentation.

### `CompileDecision`

Required fields:

- verdict (`COMPILE_EXACT`, `COMPILE_BOUNDED`, `MODIFY_PAYOUT`, or `REJECT`);
- hedgeability class;
- raw executable replication-cost range;
- synthetic research bid/ask after declared costs/reserves;
- capacity;
- risk flags;
- machine-readable reasons;
- human-readable explanation.

## Required payout functions

For `K1 < K2`, define the normalized call-spread terminal payoff:

```text
H(S_T) = 0                                      for S_T <= K1
H(S_T) = (S_T - K1) / (K2 - K1)               for K1 < S_T < K2
H(S_T) = 1                                      for S_T >= K2
```

Strict binary candidate, with threshold declared explicitly:

```text
Y_binary(S_T) = 0                               for S_T < K
Y_binary(S_T) = 1                               for S_T >= K
```

Capped-linear candidate:

```text
Y_ramp(S_T) = H(S_T)
```

Do not choose `K` implicitly. The CLI or deterministic selection routine must record whether the binary threshold is `K1`, `K2`, midpoint, or another explicit value and explain why.

## Instrument selection

The witness may accept explicit expiry/strike arguments or deterministically select a pair, but the frozen report must identify:

- exact Deribit instrument names;
- expiry;
- strike interval;
- underlying index and settlement method evidence;
- why the pair was selected;
- whether the order books had executable two-sided quotes;
- whether displayed depth was single-level or multi-level.

A deterministic selection default should prioritize:

1. a non-expired BTC option expiry with sufficient time remaining to avoid immediate expiry artifacts;
2. two call strikes sharing expiry and settlement semantics;
3. nonzero executable ask on the long leg and bid on the short leg;
4. nonzero displayed quantities on both required sides;
5. a narrow but not misleading width;
6. stable reproducibility through explicit frozen instrument arguments in the report.

If no pair passes, produce a valid rejection artifact rather than crashing or selecting marks.

## Executable pricing

For buying the spread:

```text
entry_debit = long_call_ask - short_call_bid
```

After quantity/multiplier normalization, disclose:

- raw debit;
- bid-side alternative where relevant;
- exchange fee assumptions;
- slippage reserve;
- stale-data reserve;
- settlement/basis reserve;
- total conservative cost;
- research synthetic bid/ask methodology.

Do not claim a real-world probability from replication cost.

## Capacity

Capacity must be derived from executable displayed depth on the required sides and named risk limits.

At minimum:

```text
spread_units_supported = min(
    long_leg_ask_quantity / long_quantity_per_unit,
    short_leg_bid_quantity / short_quantity_per_unit,
    configured_risk_limit_units,
)
```

Account for instrument multipliers and payout normalization. State whether this is a point estimate or lower bound. Open interest may be recorded for context but must not set capacity.

## Settlement evidence

Use official or primary venue documentation where accessible from public endpoints or stable repository evidence. If full outage/fallback rules cannot be established programmatically, record the evidence gap.

The compatibility matrix must separately label:

- payoff compatibility;
- underlying/index compatibility;
- timestamp compatibility;
- calculation-method compatibility;
- currency/multiplier compatibility;
- fallback-rule evidence;
- operational venue risk.

An exact terminal payoff is not an exact economic hedge when settlement semantics are materially mismatched.

## Output artifacts

The CLI must emit:

1. timestamped JSON containing raw market inputs, normalized specs, calculations, residual analysis, and decisions;
2. deterministic Markdown report rendered from the JSON or from the same typed object graph;
3. optional CSV payoff table or image if it is simple and reproducible, but the report must not depend on image inspection for the verdict.

The canonical compact report path should be:

```text
docs/SOP/HBCC_STAGE0_SINGLE_CONTRACT_COMPILATION_REPORT_V1.md
```

Large live-market JSON belongs under the artifact path and should follow existing repository policy for generated evidence. If it is not committed, include a compact reproducibility appendix with exact arguments, timestamps, instruments, and hashes where practical.

## Required tests

Tests must cover at least:

- strict binary payoff at values below, exactly at, and above the threshold;
- capped-linear payoff below `K1`, at `K1`, inside the ramp, at `K2`, and above `K2`;
- normalized call-spread payoff equivalence to capped-linear contract;
- non-equivalence to strict binary across the ramp;
- exact piecewise residual extrema for each supported binary-threshold convention;
- executable-side cost calculation;
- negative or crossed book handling;
- missing depth;
- stale timestamps;
- capacity normalization and constraining-leg selection;
- missing settlement evidence;
- compiler verdict mapping;
- JSON serialization and deterministic report fields.

Property-based tests are welcome but not required.

## Constraints

- Public data only.
- No authentication.
- No order placement.
- No wallet, signing, custody, or treasury code.
- No UI.
- No unrestricted LLM parsing.
- No question-family expansion.
- No dynamic hedging.
- No claim that marks are executable.
- No claim that finite grid sampling proves a global mathematical bound.
- No broad module-registry or product-backplane change.

## Non-goals

- Prediction-market listing discovery.
- Polymarket implementation.
- Customer discovery.
- Five-strike ladder.
- Automatic interestingness scoring.
- Narrative generation.
- Put spreads.
- Touch, path, range, multi-asset, volatility, funding, or correlation contracts.
- Live pilot.

## Acceptance criteria

The implementation is reviewable only when all issue #5396 acceptance criteria are met and the report states exactly one recommendation:

- `CONTINUE_HBCC_STATIC_PAYOFFS`;
- `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`;
- `STOP_HBCC_CURRENT_PRIMITIVE`.

The implementing agent must not select or start the next stage.

## Validation commands

Use exact repository-supported commands. At minimum provide results for:

```text
python -m pytest -q tests/test_hbcc_stage0_single_contract.py tests/test_cross_venue_tradeability.py
python -m ruff check src/hbcc scripts/hbcc_stage0_single_contract_witness.py tests/test_hbcc_stage0_single_contract.py
python scripts/hbcc_stage0_single_contract_witness.py --help
python scripts/hbcc_stage0_single_contract_witness.py <exact frozen arguments>
```

If the repository uses additional mandatory gates, run them or state why the bounded PR does not.

## Ownership / overlap warning

One implementation writer owns the new HBCC paths and report until the draft PR is open. Before editing shared Deribit or cross-venue modules, inspect open work and report overlap. Prefer a small adapter or new module over changing accepted Stage 0.1 semantics.

## Required PR body

The draft PR must include:

- what changed;
- why;
- issue #5396 link;
- exact selected instruments;
- fetch timestamp;
- artifact/report paths;
- focused test and lint output;
- compiler verdicts for both candidates;
- Stage 0 recommendation;
- explicit statement that `STOP_POLYMARKET_BRANCH` remains unchanged;
- mandatory `COORDINATION STATUS` block.

## COORDINATION STATUS

Agreement: partial  
Compared: HBCC charter; issue #5396; accepted hedge-backed event-liquidity Stage 0 and Stage 0.1 evidence  
Disagreement: prior wording treated narrow spreads primarily as approximate binary hedges; this packet requires explicit binary residual analysis and a distinct capped-linear candidate  
Evidence gap: live executable pair, settlement evidence, cost, capacity, and residual witness not yet produced  
Ownership overlap: potential shared Deribit fetcher and cross-venue tests  
Risk if unresolved: silent semantic substitution or overstatement of hedge quality  
Recommended default: implement new bounded HBCC paths and reuse shared code only where semantics are unchanged  
Founder decision required: no after charter merge; implementation remains bounded by issue #5396
