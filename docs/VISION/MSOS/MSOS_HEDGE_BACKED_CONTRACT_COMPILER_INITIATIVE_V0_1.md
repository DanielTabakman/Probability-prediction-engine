# MSOS Hedge-Backed Contract Compiler initiative v0.1

**Status:** PROPOSED FOR REVIEW — bounded research initiative; not BUILD authorization  
**As-of:** 2026-07-18  
**Owner:** MSOS steward  
**First ship-to:** RESEARCH / OPERATOR  
**Implementation issue:** [#5396 — HBCC Stage 0: Single-Contract Compilation Feasibility Witness](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)

## 1. Executive decision

MSOS will investigate a **Hedge-Backed Contract Compiler (HBCC)**: a venue-agnostic system that begins with executable hedge instruments and compiles them into precisely specified prediction-style contracts, together with settlement semantics, executable cost, capacity, residual-risk bounds, and an explicit compile-or-reject verdict.

The initial direction is:

```text
available hedge instruments
    -> preservable terminal payoffs
    -> formal contract specifications
    -> executable pricing and capacity
    -> human-readable questions
    -> launch selection
```

The compiler must not begin with attractive question text and silently force an approximate hedge. Payout semantics are controlling.

The next authorized work is documentation plus the bounded Stage 0 witness in issue #5396. No full compiler, venue integration, automated generation surface, or live execution is authorized.

## 2. Relationship to accepted hedge-backed event-liquidity work

This initiative refines and extends the accepted hedge-backed event-liquidity research without reversing its evidence.

The accepted Stage 0.1 conclusion remains binding:

```text
STOP_POLYMARKET_BRANCH
```

That conclusion means the repository found no qualifying recurring Polymarket universe of terminal BTC binary contracts and must not invest in a Polymarket-specific hedge scanner on the strength of that search.

HBCC changes the search direction:

| Prior branch | HBCC branch |
|---|---|
| Start from existing prediction-market listings | Start from executable hedge instruments |
| Ask whether listed contracts can be hedged | Ask which contracts can honestly be emitted from the hedge payoff |
| Venue-specific availability constraint | Venue-agnostic contract-design and feasibility constraint |
| Terminal binary contract focus | Payout-preserving static contract focus |

Reusable public-market collection, semantic parsing, and compatibility checks may be retained. The rejected Polymarket availability assumption may not be revived without new evidence and a separate steward decision.

## 3. Core thesis

A prediction-style financial contract is a state-contingent payoff over an observable market state or path. A hedge-backed compiler should emit a contract only when it can map the contract payout to an external hedge with explicitly characterized residual exposure.

Let:

- `Y(S_T)` be the contract liability at settlement;
- `H(S_T)` be the external hedge payoff;
- `epsilon(S_T) = Y(S_T) - H(S_T)` be residual exposure.

The compiler's central job is not merely to estimate a probability. It must answer:

> What payoff can be preserved, what does replication cost at executable prices, how much can be supported, what residual risk remains, and when must the system abstain?

## 4. Hardening correction: binary versus call-spread payoff

A finite-width normalized call spread does **not** exactly replicate a strict digital payoff at every terminal price.

For strikes `K1 < K2`, the normalized call-spread payoff is:

```text
0                                      when S_T <= K1
(S_T - K1) / (K2 - K1)                 when K1 < S_T < K2
1                                      when S_T >= K2
```

This is a capped-linear ramp. A strict binary threshold contract is:

```text
0                                      when S_T < K
1                                      when S_T >= K
```

The compiler must therefore choose one of four honest outcomes:

1. `COMPILE_EXACT` — the hedge terminal payoff and contract terminal payout match under declared semantics;
2. `COMPILE_BOUNDED` — mismatch is explicitly bounded and reserved under a declared tolerance;
3. `MODIFY_PAYOUT` — emit the payout naturally replicated by the hedge, such as the capped-linear ramp;
4. `REJECT` — no supported contract preserves the required semantics within the risk envelope.

Marketing language, user-interface simplicity, or venue conventions must not silently convert one payout into another.

## 5. Product definition

The HBCC is a constrained compiler with four primary outputs.

### 5.1 `ContractSpec`

Defines the economic liability:

- contract type;
- underlying;
- terminal or path observable;
- transformation;
- comparator or payout function;
- threshold or strike interval;
- observation window;
- denomination and payout cap;
- machine-readable payoff formula;
- user-facing question;
- semantic-equivalence proof state.

### 5.2 `SettlementSpec`

Defines the observable fact:

- source/index;
- publisher and venue;
- timestamp and timezone;
- averaging or calculation method;
- currency and precision;
- outage and fallback treatment;
- correction policy;
- evidence pointers;
- unresolved ambiguities.

The headline is presentation. The settlement specification is the contract.

### 5.3 `HedgeSpec`

Defines the backing structure:

- hedge venue;
- instruments and sides;
- strikes, expiry, quantities, and multipliers;
- executable bid/ask inputs;
- terminal hedge payoff;
- replication class;
- residual payoff function;
- mathematical or estimated error bounds;
- settlement and basis mismatches;
- fees, slippage, and reserves;
- displayed depth and capacity methodology.

### 5.4 `CompileDecision`

Defines whether the candidate can proceed:

- verdict;
- hedge grade;
- replication-cost range;
- research-only synthetic bid/ask;
- supported size;
- constraining leg;
- risk flags;
- rejection or modification reasons;
- human-readable explanation;
- provenance and reproducibility identifiers.

## 6. Canonical contract grammar

A contract can be represented as:

```text
C = (U, O, G, W, K, R, P, S)
```

Where:

- `U` — underlying;
- `O` — observable;
- `G` — transformation of terminal state or path;
- `W` — observation window or terminal timestamp;
- `K` — threshold or thresholds;
- `R` — comparison or resolution condition;
- `P` — payout function;
- `S` — settlement specification.

A general binary question can be written as:

```text
1{ G(X_W) satisfies R(K) }
```

But HBCC may emit binary, categorical, bucketed, capped-linear, or other explicitly supported payout forms. The compiler is not restricted to binary presentation when the hedge naturally spans a different payoff.

## 7. Generation direction

HBCC generation is hedge-first by default:

1. ingest executable hedge instruments and official settlement semantics;
2. identify payoff primitives spanned by those instruments;
3. normalize candidate terminal payoffs;
4. generate formal contract and settlement specifications;
5. prove or estimate replication error;
6. calculate executable cost and supported capacity;
7. emit human-readable wording proven equivalent to the formal payout;
8. rank only valid candidates for possible launch.

Question-first compilation may exist later, but it must terminate in `REJECT` when no hedge preserves the requested payout.

## 8. Hedgeability classes

| Class | Meaning | Initial compiler treatment |
|---|---|---|
| A | Exact static terminal replication under matched settlement semantics | `COMPILE_EXACT` |
| B | Static replication with a mathematical residual bound inside declared tolerance and reserve | `COMPILE_BOUNDED` |
| C | Dynamic hedge with gap, path, and execution exposure | Research only; not launchable in v0.1 |
| D | Model-backed relationship without payoff replication | Information product only |
| E | Observable but practically unhedgeable at required size | Reject or research only |
| F | Circular, manipulable, ambiguous, or non-resolvable | `REJECT` |

Operational failure, venue credit, and settlement evidence risks remain even when terminal payoff replication is Class A.

## 9. Initial supported payoff space

Stage 0 considers only:

- BTC;
- one listed options venue;
- one real expiry;
- two real call instruments;
- static terminal payoffs;
- strict terminal binary candidate;
- capped-linear terminal candidate derived from a normalized call spread;
- public executable bid/ask and displayed depth;
- offline research outputs.

Possible later families, not authorized now, include:

- put-spread downside ramps;
- terminal ranges and buckets;
- mutually exclusive strike ladders;
- relative-performance contracts;
- basis and funding contracts;
- implied-volatility and surface contracts;
- cross-market consistency contracts;
- probability-price derivatives.

## 10. Compiler invariants

The implementation must preserve these invariants:

1. **Payout preservation:** user-facing text, formal payout, and hedge analysis describe the same economic object.
2. **No inferred settlement match:** missing official evidence becomes a flag, not an assumption.
3. **Executable pricing:** costs use the correct book sides and retain timestamps.
4. **Capacity before opportunity:** no quote size may exceed hedge depth and risk limits.
5. **Residual transparency:** residual payoff is a function, not a single confidence score.
6. **Proof labeling:** distinguish mathematical bounds from grid and simulation estimates.
7. **Probability separation:** replication cost, risk-neutral price, real-world probability, and MSOS belief remain distinct.
8. **Abstention:** inability to compile safely is a valid and expected output.
9. **Provenance:** every recommendation can be reproduced from frozen inputs.
10. **No live implication:** research synthetic quotes do not authorize trading.

## 11. Automatic question generator boundary

An automatic question generator is a later layer of HBCC, not the first implementation.

It should generate lazily from the supported payoff universe rather than materialize every mathematically valid question. Candidate selection may later use:

- probability landmarks;
- available strikes and expiries;
- hedge depth;
- catalyst proximity;
- public attention;
- expected disagreement;
- comprehensibility;
- cannibalization of nearby contracts;
- operational and manipulation risk.

The valid-set relationship is:

```text
possible questions
    contains resolvable questions
        contains hedgeable questions
            contains economically supportable questions
                contains questions worth launching
```

HBCC first establishes hedgeable and supportable. A selector later establishes worth launching.

## 12. Stage plan

### Stage 0 — Single-contract compilation witness

Authorized by issue #5396.

Deliver:

- one timestamped BTC option-spread snapshot;
- strict-binary and capped-linear candidates from the same hedge;
- exact terminal payoff and residual functions;
- executable cost and capacity;
- settlement compatibility matrix;
- compile verdicts;
- one continue/stop recommendation.

### Stage 0.1 — Static payoff ladder

Not authorized until Stage 0 review.

Potential scope:

- five contract candidates around selected probability landmarks;
- strike and expiry selection rules;
- cross-candidate capacity and shared-hedge accounting;
- contract-family coherence.

### Stage 0.2 — Contract selector

Not authorized until Stage 0.1 review.

Potential scope:

- interest and comprehension scoring;
- catalyst and disagreement signals;
- liquidity fragmentation analysis;
- ranked launch recommendations.

### Stage 1 — Minimum credible compiler

Requires explicit steward SELECTION.

Potential scope:

- reusable `ContractSpec`, `SettlementSpec`, `HedgeSpec`, and `CompileDecision` objects;
- supported static payoff templates;
- deterministic CLI/API;
- frozen provenance;
- explicit rejection paths.

### Stage 2 — Shadow quoting and reconciliation

Requires separate authorization.

### Stage 3 — Controlled live pilot

Requires legal, venue, capital, operational, settlement, and treasury gates. No customer funds.

## 13. Stage 0 decision gate

Stage 0 must end in exactly one recommendation:

### `CONTINUE_HBCC_STATIC_PAYOFFS`

Use when at least one candidate is honestly compilable with executable pricing, interpretable capacity, and acceptable declared residual/operational risk.

### `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`

Use when the normalized spread supports the capped-linear contract but strict binary backing is not defensible under the initial primitive.

### `STOP_HBCC_CURRENT_PRIMITIVE`

Use when settlement evidence, executable depth, costs, or payoff preservation prevent a credible contract even at research scale.

No recommendation automatically authorizes the next stage.

## 14. Initial users and value

### Internal MSOS operator / researcher

Receives a reproducible answer to what can be compiled, at what cost and size, and with what residual exposure.

### Prediction-market venue or contract designer

Potential later customer for settlement-ready contract proposals carrying hedge and capacity evidence.

### Market maker

Potential later customer for static hedge plans, executable synthetic pricing, capacity envelopes, and abstention rules.

### Trader

Potential later beneficiary of simpler, bounded-loss expressions that do not require direct option-chain management.

These are hypotheses. Customer demand is not demonstrated by this charter.

## 15. Economic model hypotheses

Possible later revenue mechanisms include:

- contract-design and listing infrastructure;
- hedge and risk analytics licensing;
- market-maker tooling;
- venue integration fees;
- data products;
- spreads or liquidity revenue under separately approved live operations.

Stage 0 tests mechanism feasibility, not monetization.

## 16. Hard rejection rules

The compiler must reject or quarantine a candidate when:

- settlement language is ambiguous or incomplete;
- user-facing wording changes the formal payout;
- the hedge uses a materially incompatible index, timestamp, currency, or calculation method;
- the claimed error bound is not supported by its proof method;
- executable prices or timestamps are missing or stale;
- displayed depth cannot support the proposed size;
- capacity is inferred from open interest alone;
- the candidate depends on unstable historical correlation rather than payoff replication;
- the settlement observable is cheaply manipulable;
- the contract is circular or self-referential;
- dynamic hedging is required but not explicitly authorized;
- operational reserves or failure modes are silently omitted.

## 17. Non-goals

This initiative does not currently authorize:

- a consumer prediction-market application;
- a new exchange or protocol;
- broad question generation;
- derivatives-on-derivatives implementation;
- Polymarket-specific development;
- live order entry;
- custody or treasury movement;
- customer funds;
- automated legal or compliance conclusions;
- token issuance;
- a new top-level MSOS module without registry selection.

## 18. Success criteria

Early success is demonstrated by correctly and reproducibly answering:

- what payout is being offered;
- what hedge terminal payoff actually exists;
- where they differ;
- whether the difference is exact, bounded, estimated, or unacceptable;
- what executable hedge entry costs;
- what size displayed depth supports;
- what settlement evidence matches or conflicts;
- what the compiler recommends and why.

A credible `REJECT` or `STOP_HBCC_CURRENT_PRIMITIVE` result is successful evidence generation.

## 19. Risks

### Semantic substitution

The largest immediate risk is calling a ramp payoff a binary hedge.

### Settlement basis

A terminal payoff match is insufficient when the contract and option settle from different indexes, timestamps, or procedures.

### Liquidity illusion

A theoretical structure may have negligible executable depth.

### Product overexpansion

The broad question space can distract from proving one primitive.

### Regulatory and venue treatment

Systematic financial event-contract generation may resemble listed derivatives activity and requires later external review before any live or customer-facing use.

### Reflexivity and manipulation

Derivative-on-prediction-market observables may allow participants to influence the settlement variable and remain outside initial scope.

## 20. Current decision

Proceed only with issue #5396 and its associated Stage 0 packet. Do not begin the automatic question generator or additional question families until the witness is reviewed.

## COORDINATION STATUS

Agreement: partial  
Compared: accepted hedge-backed event-liquidity charter; Stage 0 feasibility report; Stage 0.1 terminal-availability report; HBCC white-paper thesis  
Disagreement: the accepted charter described narrow spreads as approximate binary hedges, while this refinement makes payout preservation controlling and recognizes the normalized spread as a capped-linear payoff unless binary residual risk is explicitly bounded and reserved  
Evidence gap: no timestamped venue-agnostic contract-compilation witness exists  
Ownership overlap: possible reuse of cross-venue data and parser code; implementation should default to new bounded paths  
Risk if unresolved: MSOS could claim hedge backing while silently changing contract semantics  
Recommended default: accept this charter provisionally for the sole purpose of running and reviewing Stage 0 issue #5396  
Founder decision required: yes — merge or reject this charter PR
