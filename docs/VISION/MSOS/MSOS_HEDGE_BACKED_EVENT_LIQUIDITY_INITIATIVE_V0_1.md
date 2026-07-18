# MSOS hedge-backed event liquidity initiative v0.1

**Status:** **CHARTERED FOR FEASIBILITY** — bounded MSOS initiative; **not current BUILD scope**  
**As-of:** 2026-07-18  
**Owner:** MSOS steward  
**First ship-to:** RESEARCH / OPERATOR  
**Live execution:** explicitly excluded until a later steward SELECTION

## Purpose

Define a bounded path for MSOS to translate financially resolvable prediction-market contracts into executable options hedges, synthetic event prices, and shadow market-making decisions.

This initiative tests whether MSOS can move from:

> “What probability does the options market imply?”

into the narrower operational question:

> “Can this event contract be replicated closely enough, at executable prices, to quote or trade it with a known residual risk?”

It is an extension of the existing `cross_venue_event_gap` module and research pipeline, not a new top-level product and not authorization for order routing.

## Controlling canon

| Doc | Role |
|-----|------|
| [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](../../SOP/MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) | Strategic ownership and non-widening rules |
| [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](../../SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md) | Priority and anti-drift gate |
| [`PPE_MODULE_REGISTRY_V1.md`](../../SOP/PPE_MODULE_REGISTRY_V1.md) | Existing `cross_venue_event_gap` module, tiers, and ship-to |
| [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](../../SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) | Existing Polymarket ↔ options collection, scan, and backtest capability |
| [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md`](../../SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md) | Bounded Codex handoff for fresh Stage 0 feasibility evidence |
| [`MSOS_Market_Interaction_Modes_v0.1.md`](MSOS_Market_Interaction_Modes_v0.1.md) | Hedging and expression-search ontology; simulation-only guard |
| [`SEMANTIC_CONTRACTS.md`](../../SEMANTIC_CONTRACTS.md) | Risk-neutral probability, belief, and user-facing meaning contracts |

## Initiative decision

MSOS will treat hedge-backed event liquidity as a **bounded research initiative** with four ordered stages:

1. deterministic contract specification;
2. executable hedge compilation and synthetic pricing;
3. shadow execution and reconciliation;
4. controlled live pilot only after a separate legal, operational, and capital gate.

The current charter authorizes **documentation and feasibility work only**. It does not add a relay queue row, alter the active product direction, or authorize app surfaces, automated execution, custody, or treasury movement.

## Product thesis

A terminal financial prediction contract is a state-contingent payoff. Some contracts can be approximated by listed option structures.

Example:

- event contract: `YES pays $1 if BTC > K at T`;
- approximate hedge: a narrow call spread around `K`, normalized to a $1 terminal payout;
- synthetic event price: executable hedge cost plus fees, slippage, capital cost, and a reserve for basis and settlement mismatch.

The opportunity is not merely to produce another probability estimate. It is to determine whether the event payoff can be replicated closely enough that a cross-venue price difference remains after all realistic costs and residual risks.

## Relationship to existing MSOS modules

This initiative **extends** the registered `cross_venue_event_gap` module. It does not create a new module class in v0.1.

| Existing capability | Initiative extension |
|--------------------|----------------------|
| Compare event-market price with options-implied probability | Compile an executable hedge and synthetic bid/ask |
| Daily snapshot, scan, and backtest pipeline | Store contract specification, hedge plan, cost stack, and residual-risk witness |
| Research/operator ship-to | Preserve research/operator-first posture |
| Simulation and research only | Add shadow quoting and fill simulation before any live pilot |

A new registry row or higher target tier requires a later steward SELECTION.

## Initial customer and use case

**Initial user:** internal MSOS operator or market-structure researcher.

**Initial job:** inspect a financial event contract and receive:

- deterministic payoff specification;
- compatible hedge candidates;
- executable synthetic bid and ask;
- fee, spread, slippage, collateral, and basis-risk decomposition;
- maximum residual loss;
- quote / abstain explanation;
- reproducible snapshot identifier.

This is not initially a retail betting product, broker, exchange, advisory service, or autonomous trading agent.

## Initial market universe

A contract is eligible for v0.1 feasibility only when all of the following are true:

- underlying is BTC, ETH, or SOL;
- payoff is binary and terminal-price based;
- direction is `above` or `below` a named threshold;
- resolution timestamp is explicit;
- resolution index or source is explicit;
- payout and denomination are explicit;
- a listed options market has sufficiently comparable expiry, settlement, and underlying;
- both venues expose enough market data to estimate executable cost and depth.

Examples:

- “Will BTC be above $120,000 at 08:00 UTC on September 25?”
- “Will ETH finish below $4,000 on December 31?”

Excluded from v0.1:

- elections, politics, sports, and nonfinancial outcomes;
- touch, barrier, path-dependent, or continuously monitored contracts;
- contracts combining multiple assets or conditions;
- vague or discretionary resolution language;
- contracts whose hedge and event settlement sources materially differ;
- contracts requiring dynamic hedging to make the payoff approximately safe.

## Core domain objects

### `EventContractSpec`

Required fields:

- venue and contract identifier;
- underlying;
- comparator (`above` / `below`);
- threshold;
- resolution timestamp and timezone;
- resolution source and calculation;
- payout, currency, and contract multiplier;
- YES / NO payoff mapping;
- fee and collateral rules;
- ambiguity flags;
- human-verification state.

### `HedgeCandidate`

Required fields:

- hedge venue and instruments;
- strikes, expiry, quantities, and multiplier normalization;
- executable entry bid / ask;
- terminal payoff approximation;
- maximum replication error;
- settlement, index, and timestamp mismatch;
- available hedge depth;
- liquidity and confidence scores;
- explicit rejection reason when unsafe.

### `SyntheticEventQuote`

Required fields:

- synthetic bid and ask;
- raw hedge cost;
- trading fees;
- expected slippage;
- legging-risk reserve;
- settlement / basis-risk reserve;
- duplicated-collateral charge;
- stale-data reserve;
- quote timestamp and source timestamps;
- size available at the quoted synthetic price.

### `QuoteDecision`

Required fields:

- event-market bid, ask, and depth;
- synthetic bid, ask, and depth;
- proposed side and size;
- gross discrepancy;
- conservative net edge;
- retained exposure and maximum loss;
- hedge action;
- inventory adjustment;
- decision: `QUOTE`, `WATCH`, or `ABSTAIN`;
- human-readable reason and machine-readable flags.

## System components

### 1. Event-market adapter

Collect:

- full contract wording and resolution rules;
- order-book depth and trades;
- fees, tick size, collateral, and account constraints;
- market status and timestamps.

### 2. Contract specification layer

Transform resolution language into `EventContractSpec`.

v0.1 begins with manual mapping or human approval. An unrestricted language-model parser must not be the source of truth for payoff or settlement semantics.

### 3. Options-market adapter

Collect:

- executable bid / ask and depth by strike and expiry;
- contract multiplier;
- settlement index and methodology;
- underlying or forward reference;
- fees, margin, and premium requirements;
- source timestamps and freshness.

### 4. Hedge compiler

Initial supported transformations:

- terminal `above` → narrow call spread;
- terminal `below` → narrow put spread;
- YES / NO complement transformations.

The compiler must return `NOT_SAFELY_HEDGEABLE` rather than force a structure.

### 5. Executable synthetic-pricing engine

Calculate both sides of the synthetic event market using executable book sides and available depth, not theoretical marks.

It must include:

- crossing and spread cost;
- venue fees;
- expected slippage;
- legging risk;
- settlement mismatch;
- strike and expiry approximation error;
- collateral duplication;
- conservative operational-failure buffer.

### 6. Opportunity scanner

Flag only when a conservative discrepancy remains, for example:

```text
event_bid > synthetic_ask + required_buffer
```

or:

```text
event_ask < synthetic_bid - required_buffer
```

A raw probability difference is not sufficient.

### 7. Shadow market maker

Simulate:

- resting quotes and cancellations;
- partial fills;
- stale-quote exposure;
- hedge fills, slippage, and failed legs;
- inventory skew;
- collateral usage;
- final resolution and reconciliation.

### 8. Risk and reconciliation layer

Maintain a unified economic position across separate venues:

- event exposure;
- options exposure;
- cash and collateral;
- maximum terminal loss;
- settlement basis;
- net Greeks where relevant;
- unresolved hedge failures;
- venue concentration;
- final P&L attribution.

## Probability and meaning contract

The initiative preserves two distinct views:

### Options-implied distribution

Used for:

- hedge-market consensus;
- replication cost;
- risk-neutral event pricing;
- cross-market consistency analysis.

### MSOS belief distribution

Used for:

- expected real-world profitability;
- quote skew;
- desired retained exposure;
- deciding whether to hedge fully or partially.

The product must not present an options-implied probability as a literal real-world forecast, and must not collapse replication cost, belief, and expected return into one number.

## Stage plan and gates

### Stage 0 — Feasibility packet

Deliverables:

- sample of representative financial event contracts;
- deterministic contract taxonomy;
- settlement-compatibility matrix;
- manually verified hedge examples;
- executable cost stack;
- list of recurring rejection reasons;
- estimate of qualifying-market frequency and depth.

**Execution packet:** [`HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md`](../../SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md)

**Continue gate:** a meaningful recurring subset of contracts is deterministically specifiable and has plausible static hedges.

### Stage 1 — Minimum credible hedge scanner

Potential later BUILD scope, only after explicit SELECTION:

- one event venue;
- one options venue;
- one underlying;
- terminal `above` / `below` contracts;
- static call-spread and put-spread hedges;
- executable synthetic bid / ask;
- visible cost and basis-risk decomposition;
- explicit abstention.

**Gate:**

- contract spec matches human interpretation;
- hedge payoff matches hand calculations;
- settlement mismatches are never silent;
- every opportunity shows conservative net edge and maximum residual loss;
- decision can be reproduced from stored inputs.

### Stage 2 — Shadow execution

Add historical replay where data permits, simulated resting quotes, partial fills, hedge-leg simulation, inventory, reconciliation, and P&L attribution.

**Gate:**

- positive simulated performance after conservative costs over a meaningful sample;
- adverse selection is measured;
- hedge tracking error is bounded;
- operational failures are included in stress results;
- results are reproducible from frozen snapshots.

### Stage 3 — Controlled live pilot

Requires a separate steward SELECTION and external review.

Pilot boundary:

- one underlying;
- one event venue;
- one hedge venue;
- manually approved contract specs;
- small predefined limits;
- manual treasury movement;
- cancel-all and venue shutdown controls;
- no customer funds.

**Gate before first live quote:**

- legal and venue eligibility reviewed;
- account terms permit intended activity;
- reconciliation and settlement procedures tested;
- hedge-failure and cancel-all drills passed;
- capital exists on both venues;
- maximum loss is known before every quote.

### Stage 4 — Scale

Not authorized by this charter. Possible later work includes multiple underlyings, automated hedge execution, portfolio allocation, range contracts, execution-agent interfaces, and external market-maker tooling.

## Success metrics

Early success is not revenue. It is the ability to answer correctly and reproducibly:

> What can be hedged, what does the hedge actually cost, what residual risk remains, and when should MSOS abstain?

Measure:

- percentage of discovered contracts deterministically parseable;
- percentage passing the hedgeability gate;
- synthetic-price agreement with manual calculations;
- percentage rejected for settlement or liquidity mismatch;
- conservative net edge after costs;
- hedge tracking error;
- adverse-selection loss after simulated fills;
- capital locked per dollar of expected profit;
- maximum settlement mismatch;
- reconciliation error count;
- false-positive opportunity rate.

## Hard abstention rules

The system must not quote when:

- resolution language is ambiguous;
- event and hedge settlement sources materially differ;
- required data is stale or unsynchronized;
- hedge depth is insufficient;
- the hedge cannot be executed within the displayed buffer;
- fees, margin, or collateral requirements are unknown;
- conservative net edge is non-positive;
- maximum loss cannot be calculated;
- either venue is operationally impaired;
- account or jurisdictional eligibility is unresolved.

## What it will take

### Data

- event contract metadata, resolution rules, order books, trades, and fees;
- options books with depth, multipliers, expiry, and settlement metadata;
- spot / forward and index references;
- synchronized timestamps;
- historical snapshots sufficient for replay;
- collateral and margin rules.

### Engineering

Feasibility can reuse the existing cross-venue collector, scanner, backtest pipeline, options distribution engine, and frozen-evaluation concepts.

New work would include:

- deterministic event-contract schema;
- compatibility and basis-risk engine;
- hedge compiler;
- executable cost-stack calculator;
- shadow quote and fill simulator;
- cross-venue position reconciliation;
- operator witness and kill-switch procedures.

### People

A lean feasibility effort can be stewarded by one product / market-structure owner with engineering support. A live pilot needs explicit ownership for:

- quantitative and market-structure logic;
- data and execution reliability;
- risk and reconciliation;
- legal, tax, and venue review;
- treasury and incident response.

### Capital

Research and shadow execution require data and infrastructure spend but little trading capital.

A live pilot requires:

```text
required capital
= event-venue collateral
+ options premium or margin
+ transfer / rebalancing buffer
+ stress reserve
```

Capital duplication may erase a nominal spread. Return on locked collateral is therefore a primary metric, not an afterthought.

### Planning estimate

Assuming the current cross-venue and options infrastructure is reusable:

- Stage 0 feasibility packet: roughly 1–2 focused engineer-weeks;
- Stage 1 scanner: roughly 3–6 additional engineer-weeks;
- Stage 2 shadow execution and risk: roughly 4–8 additional engineer-weeks;
- live-pilot readiness: dominated by venue access, data quality, operational procedures, and legal review rather than the hedge formula alone.

These are planning assumptions, not delivery commitments.

## First implementation sequence after future SELECTION

1. `EventContractSpec` schema and fixtures.
2. Manual contract mapper and approval state.
3. Settlement-compatibility and basis-risk report.
4. One `above` payoff → normalized call-spread compiler.
5. Executable synthetic bid / ask with complete cost stack.
6. Opportunity scanner with `QUOTE / WATCH / ABSTAIN` output.
7. Frozen snapshot and reproducibility contract.
8. Shadow fills, hedge fills, inventory, and reconciliation.
9. Feasibility and continuation report.

Do not begin with unrestricted language parsing, autonomous execution, or multi-venue breadth.

## Continuation decision

Continue beyond feasibility only when evidence supports all three claims:

1. a recurring set of event contracts can be reliably compiled into static hedges;
2. executable discrepancies survive conservative costs and adverse selection;
3. collateral, settlement, and operational burdens do not consume the advantage.

If any claim fails, retain the work as an MSOS legibility and research capability rather than forcing it into a market-making business.

## Changelog

| Date | Change |
|------|--------|
| 2026-07-18 | v0.1 — charter bounded hedge-backed event liquidity initiative; feasibility only; no live execution authorization |
| 2026-07-18 | Link bounded Stage 0 Codex feasibility packet |