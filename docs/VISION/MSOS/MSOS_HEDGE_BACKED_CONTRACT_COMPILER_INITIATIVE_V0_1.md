# MSOS Hedge-Backed Contract Compiler initiative v0.1

**Status:** PROPOSED FOR REVIEW — core-engine charter; planning only; implementation deferred  
**As-of:** 2026-07-20  
**Owner:** MSOS steward  
**Parent product vision:** [`MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`](MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md)  
**Deferred feasibility issue:** [#5396 — HBCC Stage 0 single-contract compilation witness](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)

## 1. Executive decision

MSOS will plan a **Hedge-Backed Contract Compiler (HBCC)** as the core engine of a personalized market product.

The product begins with a blank box:

> **What do you want to make a market on?**

HBCC determines whether the requested financially resolvable question can be transformed into:

- a precise contingent payoff;
- deterministic settlement semantics;
- an executable price;
- a supported size and liquidity explanation;
- an external hedge and residual-risk description;
- a transferable claim asset where the eventual deployment model permits it;
- a compile, modify, or reject decision.

The controlling product direction is:

```text
user intent
    -> deterministic contract specification
    -> supported hedge and liquidity basis
    -> executable quote and available size
    -> claim asset and settlement path
    -> private trade, publication, or API delivery
```

HBCC is not merely a scanner for existing prediction markets. It is the compiler that allows bespoke user questions to inherit liquidity from standardized markets and a shared portfolio risk engine.

No implementation is authorized while the Autobuilder remains the selected build priority. Issue #5396 and its Codex packet are deferred until explicit founder selection after Autobuilder completion.

## 2. Binding prior evidence

The accepted Stage 0.1 conclusion remains binding:

```text
STOP_POLYMARKET_BRANCH
```

That conclusion means:

- do not restart a Polymarket-specific hedge scanner on the existing evidence;
- do not assume an adequate universe of listed terminal BTC prediction contracts exists;
- preserve reusable public-data collection and semantic parsing where useful;
- require new evidence and a separate steward decision before revisiting that venue-specific branch.

HBCC changes the search direction rather than reversing the conclusion:

| Prior venue-first branch | HBCC personalized-market branch |
|---|---|
| Start from existing listed questions | Start from user intent and supported payoff primitives |
| Ask whether a venue contract can be hedged | Ask what contract can honestly be compiled and quoted |
| Each question depends on its native order book | Bespoke contracts may inherit shared external liquidity |
| Venue listing is the product boundary | First-party blank box and API are the product boundary |

## 3. Core product thesis

A personalized financial question can be represented as a state-contingent payoff over a future market state or path.

Let:

```text
Y(omega) = customer contract liability
H_i(omega) = payoff of hedge instrument i
a_i = quantity of hedge instrument i
epsilon(omega) = Y(omega) - sum_i a_i H_i(omega)
```

HBCC must answer:

> What payout is requested, can it be preserved, what does the backing cost at executable prices, how much can be supported, what risk remains, and when must the system abstain?

The valuable output is not question text. It is a complete economic object:

```text
ContractSpec
+ SettlementSpec
+ HedgeSpec
+ QuoteSpec
+ CapacitySpec
+ Claim/RedemptionSpec
+ CompileDecision
```

## 4. Liquidity inheritance

Many user-facing questions are different projections, partitions, or transformations of the same underlying future-state distribution.

Examples include:

- BTC above a threshold;
- BTC within a range;
- BTC returning more than a chosen percentage;
- a capped-linear section between two prices;
- one supported asset outperforming another.

These contracts do not necessarily require separate pools of native liquidity. When their payoffs can be transformed into standardized hedge instruments, they may be quoted from:

- external option, futures, spot, or other approved markets;
- internal offsetting customer inventory;
- fully collateralized paired claims;
- native market-maker participation;
- explicitly limited risk capital.

Liquidity is transformed, not copied. The compiler must state the actual executable capacity rather than the headline liquidity of the underlying market.

## 5. Hardening correction: binary versus call-spread payoff

A finite-width normalized call spread does **not** exactly replicate a strict binary payout at every terminal price.

For `K1 < K2`, the normalized call-spread payoff is:

```text
0                                      when S_T <= K1
(S_T - K1) / (K2 - K1)                 when K1 < S_T < K2
1                                      when S_T >= K2
```

A strict terminal binary threshold is:

```text
0                                      when S_T < K
1                                      when S_T >= K
```

The compiler must choose one honest outcome:

1. `COMPILE_EXACT` — contract and hedge terminal payoffs match under declared settlement semantics;
2. `COMPILE_BOUNDED` — mismatch has a proven bound inside declared tolerance and reserve;
3. `MODIFY_PAYOUT` — offer the payout naturally represented by the hedge, such as a capped-linear ramp;
4. `REJECT` — no supported contract preserves the requested economics within the risk envelope.

User-interface simplicity must never silently substitute one payoff for another.

## 6. Canonical domain objects

### 6.1 `QuestionIntent`

Captures what the user is trying to express:

- natural-language request;
- underlying or market set;
- date, expiry, or observation window;
- threshold, range, comparison, or transformation;
- desired payout and size;
- private or public preference;
- unresolved ambiguity.

### 6.2 `ContractSpec`

Defines the liability:

- contract type;
- underlying;
- terminal or path observable;
- transformation;
- comparator or payout function;
- threshold or interval;
- observation window;
- denomination and payout cap;
- machine-readable payoff formula;
- user-facing wording;
- semantic-equivalence proof state.

### 6.3 `SettlementSpec`

Defines the observable fact:

- source or index;
- publisher and venue;
- timestamp and timezone;
- averaging or calculation method;
- currency, precision, and rounding;
- outage and fallback treatment;
- correction and dispute policy;
- evidence pointers;
- unresolved gaps.

The headline is presentation. The settlement specification is the contract.

### 6.4 `HedgeSpec`

Defines the backing transformation:

- hedge venue and instruments;
- sides, strikes, expiries, quantities, and multipliers;
- executable bid/ask and depth inputs;
- terminal hedge payoff;
- replication class;
- residual payoff function;
- proof or estimation method;
- settlement and basis mismatches;
- fees, slippage, capital charge, and reserves;
- constraining leg and capacity methodology.

### 6.5 `QuoteSpec`

Defines the customer-facing economics:

- bid and ask;
- available size at each price level;
- fee and spread decomposition;
- backing classification;
- maximum loss;
- quote timestamp and expiry;
- alternatives with better liquidity where useful.

### 6.6 `ClaimSpec`

Defines the eventual position asset where supported:

- ownership representation;
- transferability;
- collateral or hedge reference;
- minting and burning rules;
- expiry;
- oracle or attestation source;
- redemption rights;
- administrative and upgrade controls.

### 6.7 `CompileDecision`

Defines whether the request proceeds:

- verdict;
- hedge grade;
- supported size;
- residual-risk bound;
- risk flags;
- modification or rejection reasons;
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
- `G` — transformation of state or path;
- `W` — observation window or terminal timestamp;
- `K` — threshold or thresholds;
- `R` — resolution condition;
- `P` — payout function;
- `S` — settlement specification.

The supported language may include binary, range, bucketed, capped-linear, scalar, and later other explicitly authorized payout forms.

Question composition may begin with natural language, but accepted semantics must end in this deterministic representation or a stricter equivalent.

## 8. Compiler pipeline

HBCC should ultimately support both directions.

### 8.1 Question-first compilation

```text
user intent
    -> semantic specification
    -> hedge search
    -> payoff and settlement verification
    -> executable quote and capacity
    -> compile, modify, or reject
```

This is the primary first-party product experience.

### 8.2 Hedge-first generation

```text
available hedge instruments
    -> preservable payoff primitives
    -> formal contract candidates
    -> executable pricing and capacity
    -> human-readable questions
    -> launch selection
```

This supports automatic market generation, venue APIs, discovery, and question recommendations.

Both directions must terminate in explicit rejection when the economics cannot be preserved.

## 9. Hedgeability classes

| Class | Meaning | Treatment |
|---|---|---|
| A | Exact static replication under matched settlement semantics | `COMPILE_EXACT` |
| B | Static replication with a proven residual bound inside declared tolerance and reserve | `COMPILE_BOUNDED` |
| C | Dynamic hedge with gap, path, or execution exposure | Research only until separately authorized |
| D | Model-backed relationship without payoff replication | Forecast or information product, not hedge-backed claim |
| E | Observable but practically unhedgeable at requested size | Modify, reduce size, or reject |
| F | Circular, manipulable, ambiguous, or non-resolvable | `REJECT` |

Terminal payoff replication does not remove operational, counterparty, oracle, or legal risk.

## 10. Liquidity and capacity model

For requested notional `N`, the compiler seeks the largest size such that an admissible net portfolio exists.

Capacity ends when one or more of the following binds:

- payoff cannot be spanned within tolerance;
- executable hedge depth is exhausted;
- market impact destroys quote economics;
- collateral or capital is insufficient;
- residual-risk limits bind;
- internal exposure becomes concentrated;
- adverse selection or latency makes the quote unsafe;
- settlement or oracle integrity is insufficient;
- counterparty, bridge, stablecoin, or venue limits bind;
- regulatory or customer-access gates prohibit issuance.

Available liquidity is therefore:

> **The maximum additional customer notional that can be transformed into an admissible net portfolio at the displayed quote.**

The system must state whether capacity is a lower bound, upper bound, or point estimate and must name the limiting constraint.

## 11. On-chain claim boundary

An eventual Solana or other on-chain deployment may allow users to self-custody transferable contingent claims and redeem them through programmatic settlement.

Possible models include:

1. fully collateralized paired claims;
2. hedge-backed issuance;
3. a hybrid portfolio using collateral, external hedges, internal netting, native liquidity, and reserves.

On-chain settlement can automate ownership, transfer, collateral vaulting, and redemption. It does not by itself prove:

- that the protocol has no custody or operator role;
- that an off-chain hedge is controlled trustlessly;
- that the claim is outside derivatives, securities, gaming, or other regulation;
- that the customer receives tax deferral.

These remain separate architecture and external-review questions.

## 12. Initial supported product language

The initial planning space includes:

- terminal price thresholds;
- terminal ranges and buckets;
- capped-linear probability sections;
- percentage-return thresholds;
- selected relative-performance contracts;
- later option-price, implied-volatility, realized-volatility, basis, and funding observables where semantics and backing are defensible.

The first implementation primitive remains intentionally narrow, but the product vision is not limited to one BTC call spread.

## 13. Automatic generation and selection

The compiler should not materialize every mathematically valid contract.

It should generate lazily from:

- user requests;
- probability landmarks;
- available strikes and expiries;
- hedge depth;
- repeated demand;
- catalyst proximity;
- expected disagreement;
- comprehension;
- native-market interest;
- operational and manipulation risk.

The valid-set relationship is:

```text
possible questions
    contains resolvable questions
        contains compilable questions
            contains economically supportable questions
                contains questions worth quoting or publishing
```

## 14. Product surfaces

### 14.1 First-party personalized market

Owns:

- the blank-box experience;
- user intent and demand data;
- personalized contract creation;
- private trading;
- publication and sharing;
- native participation;
- repeated-market standardization.

### 14.2 API

Supports:

- existing prediction markets;
- wallets and exchanges;
- agent-generated markets;
- professional RFQs;
- embedded contract creation and quoting;
- settlement and risk infrastructure integrations.

Partner distribution is an opportunity, not the limiting product definition.

## 15. Revenue hypotheses

Potential revenue includes:

- bid-ask spread;
- execution fee;
- contract-creation or RFQ fee;
- API and infrastructure fees;
- listing and liquidity services;
- market-making revenue;
- settlement or oracle fee;
- analytics and risk tooling.

Revenue must be evaluated after hedge costs, capital, collateral, adverse selection, residual losses, settlement, operations, and compliance.

## 16. Expansion toward market events

The planned conceptual ladder is:

```text
probability sections
    -> personalized financial questions
    -> market-movement and volatility questions
    -> market-impact contracts
    -> external-event contracts and impact maps
```

Implied volatility must not be treated as a direct confidence score or proof of a named event.

A more accurate working model is:

> Implied volatility is the market price of future dispersion and uncertainty, including risk premia and supply-demand effects.

Forward levels, skew, term structure, and option flows add directional, asymmetric, and time-localized information.

The first event-like products should remain directly observable in market data, such as realized movement, volatility, basis, or correlation changes. External named events require a separate event ontology, oracle, causal model, and impact map.

## 17. Compiler invariants

1. **Payout preservation:** user wording, formal payout, claim asset, and hedge analysis describe the same economic object.
2. **No inferred settlement match:** missing evidence becomes a gap or rejection.
3. **Executable pricing:** quote costs use correct book sides and timestamps.
4. **Capacity before opportunity:** no supported size exceeds hedge, collateral, and risk limits.
5. **Residual transparency:** residual exposure is represented as a function or explicit state set.
6. **Proof labeling:** mathematical, grid, historical, and simulation evidence remain distinct.
7. **Probability separation:** replication cost, risk-neutral price, real-world forecast, and user belief remain separate.
8. **Abstention:** rejection and modification are normal compiler outputs.
9. **Provenance:** every decision is reproducible from frozen inputs.
10. **Custody honesty:** smart-contract control and economic responsibility are described accurately.
11. **Tax honesty:** tokenization does not imply a specific tax result.
12. **No live implication:** planning and research quotes do not authorize execution.

## 18. Deferred Stage 0 witness

Issue #5396 remains the first proposed empirical test after the Autobuilder is complete and the initiative is selected.

It will compare:

- a strict binary terminal contract;
- the capped-linear contract naturally represented by the same call spread;
- executable cost and depth;
- settlement compatibility;
- residual payoff;
- supported size;
- compile verdict.

The witness is a system-level balancing and honesty test. It is not the full product and does not limit the personalized-market vision.

Stage 0 must end in one of:

- `CONTINUE_HBCC_STATIC_PAYOFFS`;
- `CONTINUE_HBCC_CAPPED_LINEAR_ONLY`;
- `STOP_HBCC_CURRENT_PRIMITIVE`.

No recommendation automatically authorizes a subsequent stage.

## 19. Planning work authorized now

While implementation is deferred, continue bounded charter work on:

- supported question ontology;
- contract and settlement grammar;
- on-chain claim models;
- liquidity, netting, and capacity theory;
- first-party user journeys;
- API concepts;
- backing and risk disclosures;
- native-market promotion lifecycle;
- market-event theory;
- legal, regulatory, tax, oracle, custody, and counterparty question lists;
- future feasibility and customer-discovery plans.

## 20. Hard rejection rules

Reject or quarantine a candidate when:

- settlement is ambiguous or incomplete;
- wording changes the formal payout;
- claim-token rights differ from the displayed contract;
- hedge settlement is materially incompatible;
- an error bound lacks an adequate proof method;
- executable prices or timestamps are missing or stale;
- displayed depth cannot support the requested size;
- capacity is inferred from open interest alone;
- the candidate depends only on unstable historical correlation;
- the observable is cheaply manipulable;
- the contract is circular or self-referential;
- dynamic hedging is required but not authorized;
- operational, counterparty, oracle, or bridge risks are omitted;
- legal or access gates are unresolved for the proposed launch surface.

## 21. Current non-goals

This charter does not currently authorize:

- implementation before Autobuilder completion;
- live order entry or market making;
- deployment of claim tokens;
- custody, treasury movement, or customer funds;
- a consumer launch;
- a production API;
- unrestricted question generation;
- a final chain selection;
- automated legal or tax conclusions;
- Polymarket-specific development;
- politics, sports, weather, or personal-event markets in the initial language.

These are sequencing boundaries, not statements that the long-term product is limited to an internal research tool.

## 22. Five truths to solve

1. The supported language must express views users actually want.
2. Quotes must be immediate enough for the blank-box experience.
3. Supported size must feel meaningful after real constraints.
4. The interface must remain simpler than direct derivatives construction.
5. Unit economics must survive all hedge, capital, risk, settlement, operational, and distribution costs.

The addressable question space is treated as sufficiently large. The primary uncertainties are economic, operational, distributional, legal, and regulatory feasibility.

## 23. Current decision

Continue product theory, planning, and chartering only.

Do not implement issue #5396 or broader HBCC capability until:

1. the Autobuilder is complete;
2. the personalized-market vision and this charter are accepted;
3. the founder explicitly selects the next feasibility stage;
4. implementation ownership is assigned through the control plane.

## COORDINATION STATUS

Agreement: partial  
Compared: accepted hedge-backed event-liquidity charter; accepted Stage 0 and Stage 0.1 evidence; original HBCC draft charter; personalized market compilation vision  
Disagreement: the original HBCC draft emphasized an immediate internal research witness; the controlling direction now defines HBCC as the engine of a personalized first-party market plus API and defers implementation until Autobuilder completion  
Evidence gap: executable capacity, user demand, on-chain operating model, tax treatment, and regulatory pathway remain unproven  
Ownership overlap: none for this documentation revision; future implementation may overlap PPE market data, settlement, execution, and Autobuilder-managed delivery paths  
Risk if unresolved: the project could optimize a narrow scanner while missing the larger personalized-market product or could overstate payout, liquidity, custody, tax, or regulatory properties  
Recommended default: accept this charter as the core-engine layer beneath the personalized-market vision and keep issue #5396 deferred  
Founder decision required: yes — accept, revise, or reject this charter
