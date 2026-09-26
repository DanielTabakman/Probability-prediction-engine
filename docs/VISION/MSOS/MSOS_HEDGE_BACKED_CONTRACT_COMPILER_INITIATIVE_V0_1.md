# MSOS Hedge-Backed Contract Compiler initiative v0.1

**Status:** PROPOSED FOR REVIEW — core-engine charter; implementation deferred  
**As-of:** 2026-07-20  
**Owner:** MSOS steward  
**Parent vision:** [`MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`](MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md)  
**Execution decisions:** [`MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md`](MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md)  
**Deferred implementation issue:** [#5396 — HBCC Stage 0: Single-Contract Compilation Feasibility Witness](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)

## 1. Executive decision

The Hedge-Backed Contract Compiler (HBCC) is the core engine beneath the personalized market product.

Its job is to transform supported user intent into:

- a precise contingent claim;
- deterministic settlement rules;
- a hedge or admissible backing plan;
- executable pricing and capacity;
- a transferable claim representation where permitted;
- a compile, modify, or reject decision.

The controlling generation direction is:

```text
user or API intent
    -> deterministic contract semantics
    -> supported payoff basis
    -> external hedge and internal netting search
    -> executable pricing and capacity
    -> claim issuance or rejection
```

HBCC may also generate contracts hedge-first from available instruments, but the product vision is user-first: the user asks for the exact supported market they want.

Payout semantics remain controlling. The compiler must never use attractive question text to hide a different hedge payoff.

No implementation is currently authorized. The Autobuilder remains the selected build priority. Issue #5396 is deferred until the Autobuilder is complete and the founder explicitly selects this initiative.

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
| Start from existing prediction-market listings | Start from user intent or executable hedge instruments |
| Ask whether listed contracts can be hedged | Ask which requested contracts can honestly be compiled |
| Venue-specific availability constraint | Venue-agnostic contract-design and feasibility constraint |
| Terminal binary contract focus | Payout-preserving static contract focus first, broader language later |

Reusable public-market collection, semantic parsing, and compatibility checks may be retained. The rejected Polymarket availability assumption may not be revived without new evidence and a separate steward decision.

## 3. Core thesis

A prediction-style financial contract is a state-contingent payoff over an observable market state or path. A hedge-backed compiler should emit a contract only when it can map the contract payout to external hedge instruments, internal offsets, collateral, or explicitly limited risk capital with characterized residual exposure.

Let:

- `Y(omega)` be the customer contract liability;
- `H(omega)` be the aggregate external hedge payoff;
- `I(omega)` be internal offsetting portfolio exposure;
- `R(omega)` be retained residual exposure.

The economic identity is:

```text
Y(omega) = H(omega) + I(omega) + R(omega)
```

where `R` must remain inside declared limits and reserves.

The compiler's central job is not merely to estimate a probability. It must answer:

> What payoff is being offered, what backing is available, what does it cost at executable prices, how much can be supported, what residual and settlement risk remains, and when must the system abstain?

## 4. Liquidity inheritance

The core product insight is:

> **Bespoke questions do not necessarily require bespoke liquidity pools.**

Many custom contracts are different projections of a shared future-state distribution. They may inherit executable capacity from:

- standardized options, futures, spot, perpetuals, and other approved external markets;
- internal netting among customer contracts;
- native user liquidity;
- program-controlled collateral;
- explicitly limited liquidity-provider or protocol risk capital.

Liquidity is transformed, not copied.

A custom contract inherits only the capacity that remains after:

- hedge ratios;
- displayed depth;
- price impact;
- fees and slippage;
- collateral and margin;
- settlement compatibility;
- residual-risk limits;
- execution and operational reserves.

The customer position may be smaller than an external hedge lot through pooling and fractional claim issuance. That changes customer denomination, not aggregate hedge capacity.

The controlling detailed execution decisions are recorded in `MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md`.

## 5. Hardening correction: binary versus call-spread payoff

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

The compiler must choose one of four honest outcomes:

1. `COMPILE_EXACT` — the backing payoff and customer payout match under declared semantics;
2. `COMPILE_BOUNDED` — mismatch is explicitly bounded and reserved under a declared tolerance;
3. `MODIFY_PAYOUT` — offer the nearest payout naturally replicated by the available backing;
4. `REJECT` — no supported structure preserves the required semantics within the risk envelope.

Marketing language, user-interface simplicity, or venue conventions must not silently convert one payout into another.

## 6. Product definition

HBCC is a constrained compiler with five primary outputs.

### 6.1 `ContractSpec`

Defines the economic liability:

- contract type;
- underlying or market set;
- terminal or path observable;
- transformation;
- comparator or payout function;
- threshold, interval, or category set;
- observation window;
- denomination and payout cap;
- machine-readable payoff formula;
- user-facing question;
- semantic-equivalence proof state.

### 6.2 `SettlementSpec`

Defines the observable fact:

- source/index;
- publisher and venue;
- timestamp and timezone;
- averaging or calculation method;
- currency and precision;
- outage and fallback treatment;
- correction and finality policy;
- evidence pointers;
- oracle or attestation method;
- unresolved ambiguities.

The headline is presentation. The settlement specification is the contract.

### 6.3 `BackingSpec`

Defines the backing structure:

- external hedge venue and instruments;
- internal offsetting portfolio;
- collateral or paired-claim basis;
- liquidity-provider or retained-risk allocation;
- strikes, expiry, quantities, and multipliers;
- executable bid/ask inputs;
- terminal backing payoff;
- residual payoff function;
- mathematical or estimated error bounds;
- settlement and basis mismatches;
- fees, slippage, financing, and reserves;
- displayed depth and capacity methodology;
- custody and attestation state.

### 6.4 `QuoteSpec`

Defines the commercial offer:

- indicative or firm state;
- bid and ask;
- available size by price level;
- quote validity or invalidation condition;
- minimum and maximum customer size;
- partial-fill state;
- limit-order terms;
- batching or external hedge-lot treatment;
- pass-through costs;
- risk and capital charge;
- platform percentage and minimum fee.

### 6.5 `CompileDecision`

Defines whether the candidate can proceed:

- verdict;
- hedge or backing grade;
- replication-cost range;
- supported size;
- constraining leg or risk limit;
- risk flags;
- rejection or modification reasons;
- human-readable explanation;
- provenance and reproducibility identifiers.

## 7. Canonical contract grammar

A contract can be represented as:

```text
C = (U, O, G, W, K, R, P, S)
```

Where:

- `U` — underlying or market set;
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

HBCC may emit binary, categorical, bucketed, capped-linear, range, relative-performance, or other explicitly supported payout forms. The compiler is not restricted to binary presentation when the available backing spans a different payoff.

## 8. Generation modes

### 8.1 User-first compilation

The intended product mode:

1. accept natural-language or structured user intent;
2. produce deterministic machine-readable semantics;
3. search the supported payoff and backing basis;
4. calculate residual and settlement risk;
5. calculate executable cost and capacity;
6. return exact support, supported modification, or rejection;
7. emit a quote using the RFQ and limit-order protocol.

### 8.2 Hedge-first generation

The discovery and market-generation mode:

1. ingest executable hedge instruments and official settlement semantics;
2. identify payoff primitives spanned by those instruments;
3. normalize candidate payoffs;
4. generate formal contract and settlement specifications;
5. prove or estimate replication error;
6. calculate executable cost and supported capacity;
7. rank valid candidates for possible public launch.

Both modes terminate in the same deterministic objects and risk rules.

## 9. Hedgeability and backing classes

| Class | Meaning | Initial compiler treatment |
|---|---|---|
| A | Exact static terminal replication under matched settlement semantics | `COMPILE_EXACT` |
| B | Static replication with a mathematical residual bound inside declared tolerance and reserve | `COMPILE_BOUNDED` |
| C | Dynamic hedge with gap, path, and execution exposure | Research only until authorized |
| D | Model-backed relationship without payoff replication | Information product or explicitly collateralized risk product only |
| E | Observable but practically unhedgeable at required size | Reject or native-liquidity-only candidate |
| F | Circular, manipulable, ambiguous, or non-resolvable | `REJECT` |

Operational failure, venue credit, custody, oracle, and settlement evidence risks remain even when terminal payoff replication is Class A.

## 10. Quoting and fractionalization

The external hedge's minimum lot defines hedge granularity. It does not necessarily define customer minimum size.

Supported customer mechanisms may include:

- fractional claim units;
- pooled issuance;
- request batching;
- internal netting;
- bounded temporary inventory;
- native liquidity-provider bridging.

The initial quote model is:

```text
immediate indicative quote
    -> refreshed firm RFQ
        -> limit price and maximum size
            -> partial fill or batch where permitted
                -> hedge and claim issuance
```

Every quote must expose:

- price;
- available size;
- quote validity;
- partial-fill state;
- backing classification;
- limiting risk or hedge leg;
- costs and fees;
- maximum loss;
- settlement rule.

## 11. Compiler invariants

The implementation must preserve these invariants:

1. **Payout preservation:** user-facing text, formal payout, and backing analysis describe the same economic object.
2. **No inferred settlement match:** missing official evidence becomes a flag, not an assumption.
3. **Executable pricing:** costs use correct book sides and retain timestamps.
4. **Capacity before opportunity:** no quote size may exceed admissible net portfolio capacity.
5. **Fractionalization honesty:** smaller claim units do not imply greater total backing.
6. **Residual transparency:** residual payoff is a function, not a confidence score.
7. **Settlement transparency:** index, timestamp, oracle, finality, fallback, and correction risk remain explicit.
8. **Proof labeling:** distinguish mathematical bounds from grid and simulation estimates.
9. **Probability separation:** replication cost, risk-neutral price, real-world probability, and MSOS belief remain distinct.
10. **Abstention:** inability to compile safely is a valid and expected output.
11. **Provenance:** every recommendation can be reproduced from frozen inputs.
12. **No live implication:** planning, research synthetic quotes, and API designs do not authorize trading.
13. **Legal gate:** no customer-facing issuance or venue operation without qualified review for the target model and jurisdiction.

## 12. Initial supported payoff space

The deferred Stage 0 witness remains narrow:

- BTC;
- one listed options venue;
- one real expiry;
- two real call instruments;
- static terminal payoffs;
- strict terminal binary candidate;
- capped-linear terminal candidate derived from a normalized call spread;
- public executable bid/ask and displayed depth;
- offline research outputs.

The planned product language is broader and may later include:

- put-spread downside ramps;
- terminal ranges and buckets;
- mutually exclusive strike ladders;
- percentage-return contracts;
- relative-performance contracts;
- simple baskets;
- basis and funding contracts;
- implied-volatility and surface contracts;
- cross-market consistency contracts;
- probability-price derivatives;
- market-movement and market-impact contracts.

## 13. Automatic question generation

Automatic question generation is a product layer of HBCC, not merely text generation.

It should generate lazily from:

- user intent;
- supported payoff grammar;
- available strikes and expiries;
- hedge and netting capacity;
- probability landmarks;
- catalyst proximity;
- public attention;
- expected disagreement;
- comprehension;
- cannibalization of nearby contracts;
- operational, settlement, manipulation, and legal constraints.

The valid-set relationship is:

```text
possible questions
    contains resolvable questions
        contains compilable questions
            contains economically supportable questions
                contains questions worth quoting or launching
```

## 14. Distribution and revenue

The initial distribution plan is API-first for:

- prediction markets;
- hedge funds and market makers;
- research labs and forecasters;
- wallets, brokers, and exchanges;
- agents and professional RFQ clients.

The first-party site remains strategic and owns the complete blank-box product experience.

The initial fee hypothesis is:

```text
customer price
    = executable net backing cost
    + pass-through venue and settlement costs
    + risk and capital reserve
    + percentage platform fee
    + minimum platform fee
```

This remains an empirical unit-economics hypothesis, not a proven model.

## 15. Custody and operating-model hypotheses

HBCC must support or interoperate with several possible backing operators:

- on-chain hedge protocols;
- traditional brokers, custodians, exchanges, and clearing relationships;
- hedge funds and professional market makers;
- hybrid on-chain collateral plus off-chain hedge arrangements.

A first commercial API may provide contract design, pricing, settlement, risk, and quote-routing infrastructure while an eligible partner acts as issuer, market maker, or venue.

Self-custody, smart contracts, or tokenization do not automatically remove operator, dealer, marketplace, clearing, custody, tax, or derivatives obligations.

## 16. Stage plan

### Planning phase — current

Authorized:

- vision and charter development;
- supported question ontology;
- payout and settlement grammar;
- API and user-flow design;
- on-chain and partner architecture alternatives;
- legal, regulatory, tax, custody, and oracle question lists;
- staged evidence plan.

Not authorized:

- product code;
- live quotes;
- customer funds;
- token issuance;
- venue integration;
- deployment.

### Stage 0 — Single-contract compilation witness

Deferred until:

1. the Autobuilder is complete;
2. the vision and charter are accepted;
3. the founder explicitly selects Stage 0;
4. implementation ownership is assigned.

Deliver later:

- one timestamped BTC option-spread snapshot;
- strict-binary and capped-linear candidates from the same hedge;
- exact terminal payoff and residual functions;
- executable cost and capacity;
- settlement compatibility matrix;
- compile verdicts;
- one continue/stop recommendation.

### Stage 0.1 — Static payoff ladder

Not authorized until Stage 0 review.

### Stage 0.2 — Contract selector and quote protocol

Not authorized until prior review.

### Stage 1 — Minimum credible compiler API

Requires explicit steward selection and legal operating-model review.

### Stage 2 — Shadow quoting, portfolio netting, and reconciliation

Requires separate authorization.

### Stage 3 — Controlled partner or live pilot

Requires legal, venue, capital, operational, settlement, custody, oracle, and treasury gates.

## 17. Deferred Stage 0 decision gate

Stage 0 must later end in exactly one recommendation:

### `CONTINUE_HBCC_STATIC_PAYOFFS`

Use when at least one candidate is honestly compilable with executable pricing, interpretable capacity, and acceptable declared residual/operational risk.

### `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`

Use when the normalized spread supports the capped-linear contract but strict binary backing is not defensible under the initial primitive.

### `STOP_HBCC_CURRENT_PRIMITIVE`

Use when settlement evidence, executable depth, costs, or payout preservation prevent a credible contract even at research scale.

No recommendation automatically authorizes the next stage.

## 18. Current users and value hypotheses

### Prediction-market venue

Potential API customer for contract generation, settlement specifications, quote routing, liquidity evidence, and public-market promotion.

### Hedge fund or market maker

Potential issuer, hedge counterparty, liquidity provider, or API customer for structured RFQs and portfolio netting.

### Research lab or forecaster

Potential customer for deterministic question creation, probability sections, tradable forecast contracts, and settlement infrastructure.

### Wallet, broker, or exchange

Potential embedded distribution partner for custom markets and self-custodied claim positions.

### First-party trader

Potential user of a blank-box interface that expresses exact views without direct option-chain management.

These are hypotheses. Customer demand is not demonstrated by this charter.

## 19. Hard rejection rules

The compiler must reject or quarantine a candidate when:

- settlement language is ambiguous or incomplete;
- user-facing wording changes the formal payout;
- backing uses a materially incompatible index, timestamp, currency, or calculation method;
- the claimed error bound is not supported by its proof method;
- executable prices or timestamps are missing or stale;
- displayed depth and admissible net capacity cannot support the proposed size;
- capacity is inferred from open interest alone;
- fractionalization is presented as new aggregate liquidity;
- the candidate depends on unstable historical correlation rather than payoff replication without explicit collateral and risk capital;
- the settlement observable is cheaply manipulable;
- the contract is circular or self-referential;
- dynamic hedging is required but not explicitly authorized;
- custody, collateral, oracle, legal, or operational responsibilities are silently omitted.

## 20. Risks

### Semantic substitution

Calling one payoff another.

### Settlement basis

Customer claim and backing settle from different facts.

### Liquidity illusion

Treating a theoretical position, headline market volume, open interest, or fractional token units as executable capacity.

### Fractional hedge mismatch

Customer claims accumulate below the hedge-lot threshold while the system remains temporarily exposed.

### Stale quote and adverse selection

A customer accepts a quote after the backing market has moved.

### Custody and reconciliation

On-chain customer claims and off-chain hedges diverge operationally.

### Product overexpansion

The broad question space distracts from proving primitives.

### Regulatory and venue treatment

Personalized contingent-claim issuance, quoting, transfer, and settlement may trigger regulated activities depending on structure and jurisdiction.

### Reflexivity and manipulation

Derivative-on-market observables may allow participants to influence settlement variables.

## 21. Current decision

Continue planning and chartering the personalized market and HBCC system.

Do not implement issue #5396 or any product code until the Autobuilder is complete and the founder explicitly selects this initiative.

The parent vision and execution-decisions document control product direction. This charter controls the compiler's semantic, backing, pricing, capacity, quote, and rejection behavior.

## COORDINATION STATUS

Agreement: aligned  
Compared: personalized market parent vision; execution decisions; accepted hedge-backed event-liquidity work; deferred Stage 0 issue #5396  
Disagreement: none on product direction; the older narrow scanner framing is superseded, while `STOP_POLYMARKET_BRANCH` remains binding evidence  
Evidence gap: executable depth, latency, residual bounds, settlement alignment, fractional batching, partner model, custody, legal treatment, customer demand, and unit economics remain unproven  
Ownership overlap: none; documentation-only planning  
Risk if unresolved: future implementation could build a narrow scanner, conflate fractionalization with liquidity, or understate residual, settlement, custody, and legal risk  
Recommended default: accept HBCC as the core engine beneath the personalized market and keep all implementation deferred until Autobuilder completion and explicit selection  
Founder decision required: yes — approve, revise, or reject this charter
