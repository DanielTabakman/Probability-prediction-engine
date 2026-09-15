# Market Structure Engine ↔ Hummingbot Boundary v1

**Status:** Proposed architecture contract  
**Purpose:** Harden the boundary between differentiated market-structure research and generic trading infrastructure.  
**Source of truth:** GitHub. This document must be reviewed before becoming controlling canon.

## Decision

Use Hummingbot as the default provider for commodity trading infrastructure. Build and own only the differentiated market-structure intelligence that Hummingbot does not provide.

The market-structure work remains a separate engine/repository. It should integrate with Hummingbot through narrow adapters/contracts rather than being implemented inside Hummingbot or merged back into MSOS.

## Core principle

Before building any generic trading capability, ask:

> Does Hummingbot already provide this capability at sufficient quality for the experiment or product requirement?

- If **yes**, reuse Hummingbot behind an adapter.
- If **partially**, wrap Hummingbot and add only the missing research-specific behavior.
- If **no**, build the smallest missing capability locally and document why Hummingbot was insufficient.

This is a build-vs-reuse gate, not a requirement to force every research workflow through Hummingbot.

## Target architecture

```text
                   MARKET STRUCTURE ENGINE
                   differentiated intelligence
          ┌─────────────────────────────────────┐
          │ feed fitness by scale               │
          │ multi-scale structure detection     │
          │ cross-scale persistence             │
          │ forward validation / baselines      │
          │ market-state / structure snapshot   │
          └───────────────┬─────────────────────┘
                          │
                 narrow output contract
                          │
                          ▼
                     HUMMINGBOT API
                 commodity trading layer
          ┌─────────────────────────────────────┐
          │ historical OHLCV                    │
          │ live prices/candles/order books     │
          │ funding / trading rules             │
          │ strategy/controller backtesting     │
          │ controllers + executors             │
          │ portfolio/orders/fills/positions    │
          │ bot deployment/monitoring           │
          │ Gateway / DEX / CLMM operations     │
          └───────────────┬─────────────────────┘
                          │
                          ▼
                       MARKETS

MSOS sits above these systems as the founder/operator workflow and visualization layer.
```

## Component ownership

### `market-structure-engine` owns

- feed usefulness/fitness by scale;
- normalized/relative structure definitions;
- support/resistance/zone detection;
- cross-scale persistence;
- research experiments;
- frozen-detector forward validation;
- control/random/dumb baselines;
- evidence that a structure contains information;
- compact market-state / structure outputs;
- research provenance and negative results.

It does **not** own generic exchange connectivity, order routing, generic bot orchestration, or a second full trading backtester.

### Hummingbot owns by default

When its supported interface is sufficient:

- historical OHLCV candles;
- current prices and candles;
- order-book snapshots;
- funding information;
- trading rules and supported order types;
- strategy/controller backtesting;
- controller/script deployment;
- reusable executors;
- balances, portfolio state, orders, fills and positions;
- archived bot performance/history;
- Gateway DEX/CLMM operations;
- live/paper execution infrastructure.

The stable dependency target is **Hummingbot API + Gateway + Controller/Executor interfaces**, not a specific Hummingbot Dashboard UI.

### `oct-signal-capture` owns only when needed

Signal Capture is retained as a specialist research observation layer rather than the default source for generic market data.

Use it when the experiment requires:

- raw/high-resolution observations not retained by Hummingbot;
- historical L1/L2/tick data under our control;
- unusual/custom providers;
- research-grade provenance;
- provider-specific evidence;
- a feed unavailable or unsuitable through Hummingbot.

Do not expand Signal Capture merely to duplicate a Hummingbot capability.

### MSOS owns

- founder/operator visibility;
- current question, experiment, stage and next action;
- research conclusions and rejected hypotheses;
- decision workflow;
- visualization of market-structure output;
- visualization of Hummingbot execution/backtest state;
- human approval boundaries.

MSOS must not duplicate market-structure math or become the generic trading engine.

## Two distinct kinds of backtest

Do not collapse research validation into strategy simulation.

### 1. Research / information backtest — market-structure-engine

Question:

> Does this detected structure contain useful information about what happens afterward?

Examples:

- freeze a detected level at time T;
- measure future behavior around it;
- compare with random/control levels;
- compare multi-scale vs single-scale persistence;
- estimate whether the phenomenon exists before defining a trading rule.

This backtest may be implemented locally because the object being tested is the research hypothesis, not an executable strategy.

### 2. Trading strategy backtest — Hummingbot

Question:

> If this validated market-state signal were expressed as a real strategy, what would the trading result have been?

Use Hummingbot for:

- controller configuration;
- executor simulation;
- trade costs/fees;
- position/order behavior;
- realized/unrealized P&L;
- drawdown and other execution-level performance;
- comparison of execution expressions.

Do not build a parallel generic trading simulator unless a documented Hummingbot limitation blocks the experiment.

## Integration contract

The market-structure engine should expose a compact, implementation-independent result. Avoid leaking detector internals into MSOS/Hummingbot.

Minimum conceptual payload:

```text
StructureSnapshot
- instrument / market identity
- observation timestamp
- source/provenance
- scale fitness
- detected zones / levels
- horizons supporting each level
- persistence / evidence summary
- detector/version identity
- research-status flags
```

The output must distinguish:

- observed structure;
- validated information;
- strategy signal;
- executable intent.

A detected level is **not** automatically a trade signal.

## Safety and authority boundaries

1. Market-structure research is read-only with respect to trading systems.
2. No detector may place, cancel or modify orders.
3. No research result becomes executable merely because it appears in MSOS.
4. Hummingbot write authority remains disabled until a separately approved execution stage.
5. Credentials/wallet/CEX secrets remain on the execution host; the research engine receives no secret material unless explicitly required and approved.
6. Hummingbot adapters default to read-only during research/validation.
7. Production execution changes require a separate bounded task/PR and explicit acceptance criteria.

## Context/token hardening

The future `market-structure-engine` repo should be designed so an implementation/research agent does not need to read PPE/MSOS, Hummingbot internals, or Signal Capture internals for ordinary work.

Required front door:

```text
README.md
PROJECT_STATE.md
ARCHITECTURE.md
INTEGRATION_CONTRACT.md
RESEARCH_METHOD.md
FINDINGS.md
```

Agent reading rule:

1. `PROJECT_STATE.md` — what is happening now;
2. relevant research/architecture contract;
3. only the code path needed for the assigned experiment;
4. external repo docs only when the adapter/interface itself is being changed.

Do not ask agents to rediscover the full MSOS/PPE repository for market-structure tasks.

## Hummingbot reuse gate

Before accepting new infrastructure in `market-structure-engine`, the task/PR must answer:

```text
Capability needed:
Hummingbot capability checked:
Why existing Hummingbot capability is sufficient / insufficient:
Smallest local addition required:
Long-term ownership:
```

If this section is absent for generic data/backtest/execution infrastructure, the change is not ready for review.

## Current evidence and immediate interpretation

The live NDAX multi-scale witness currently shows approximately:

- 5m: POOR
- 15m: MARGINAL
- 1h: USABLE
- 4h: USABLE
- 1d: currently USABLE, but history is immature

Persistent levels recur across multiple horizons. This supports the research direction that feed usefulness is scale-dependent and the same general structure detector can surface recurring patterns across scales.

It does **not** yet prove predictive usefulness, tradability, or superiority to a baseline.

## Hardened next sequence

### Phase A — repo split

Create `DanielTabakman/market-structure-engine` and move only market-structure research/analysis ownership into it.

Do not move:

- generic Hummingbot infrastructure;
- MSOS UI/product code;
- execution credentials/state;
- Signal Capture collectors that remain useful as standalone observation infrastructure.

### Phase B — freeze and validate the current detector

- version/freeze the v0 detector before tuning;
- record zones at time T;
- run forward validation;
- compare against dumb/random baselines;
- test whether multi-scale persistence adds information.

### Phase C — add Hummingbot historical-data adapter

Use Hummingbot historical candles as the default path for ordinary OHLCV research where appropriate.

Keep Signal Capture as an alternative adapter for raw/high-resolution/provider-specific evidence.

### Phase D — strategy expression backtest

Only after a structure hypothesis survives research validation:

- map the research output to a Hummingbot Controller/config;
- use Hummingbot backtesting with explicit costs;
- compare possible executor/strategy expressions;
- keep the detector independent of the trading expression.

### Phase E — paper / tiny live

Only after explicit strategy-backtest acceptance:

- paper/read-only operational witness first;
- then separately approve a tiny live execution experiment;
- preserve full order/fill/result provenance for LEARN.

## Acceptance criteria for this architecture

This architecture is functioning when:

- market-structure agents can work without loading the PPE/MSOS codebase;
- ordinary historical OHLCV research can use Hummingbot rather than duplicated ingestion;
- Signal Capture is used only for justified specialist evidence;
- research validation can run without trading authority;
- a validated market-structure output can be translated into a Hummingbot strategy without moving detector code into Hummingbot;
- Hummingbot handles generic strategy simulation/execution accounting;
- MSOS can explain the current project state without containing the underlying detector implementation;
- no component has two competing sources of truth for the same generic capability.

## Non-goals

- rewriting Hummingbot;
- embedding the research engine inside Hummingbot;
- merging the future market-structure repo back into MSOS;
- building a second generic trading platform;
- replacing Signal Capture before its specialist value is evaluated;
- generating a trade solely because a multi-scale level exists;
- live execution during the current research phase.

## Coordination Status

Agreement: aligned with the current multi-scale research direction and MSOS non-widening/control-plane rules.  
Compared: MSOS/PPE control-plane SOP, current operating-loop probe, current Signal Capture multi-scale probe, current Hummingbot API/Gateway/backtesting capabilities.  
Disagreement: prior architecture implicitly treated more generic market-data/backtest infrastructure as ours to build; this contract makes Hummingbot reuse the default.  
Evidence gap: Hummingbot compatibility/quality must still be validated per connector, market, resolution and experiment; current live NDAX research evidence comes from Signal Capture.  
Ownership overlap: Hummingbot adapters and Signal Capture adapters must not both silently become canonical for the same data capability.  
Risk if unresolved: duplicated infrastructure, larger agent context, inconsistent backtests and unnecessary maintenance.  
Recommended default: approve this boundary, split the market-structure repo, then forward-validate the frozen detector while adding a narrow Hummingbot historical-data adapter.  
Founder decision required: no — founder requested this hardened direction.
