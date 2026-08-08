# MSOS Personalized Market Compilation vision v0.1

**Status:** PROPOSED FOR REVIEW — product vision and planning charter only; implementation deferred  
**As-of:** 2026-07-20  
**Owner:** MSOS steward  
**Core engine:** [`MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md`](MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md)  
**Execution decisions:** [`MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md`](MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md)  
**Deferred feasibility issue:** [#5396 — HBCC Stage 0 single-contract compilation witness](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)

## 1. Executive decision

The long-term product is a **personalized market interface**:

> A blank box where a user asks for the exact market they want.

For supported questions, the system converts the user's intent into:

- a precise contingent claim;
- deterministic settlement rules;
- an executable price and available size;
- a disclosed source of liquidity and backing;
- a transferable position asset where the deployment model permits it;
- automatic or rule-bound settlement and redemption.

The initial supported topical scope may be narrower than a general prediction market, but the contract space can still be extremely large. A finite language of financial underlyings, expiries, thresholds, ranges, transformations, and payout functions can generate a vast number of personalized contracts.

The central product insight is not merely that many questions can be generated. It is that many bespoke questions can inherit liquidity from the same standardized external markets and shared internal risk book.

The target product is therefore:

> **Personalized derivatives with a prediction-market interface.**

The initial user promise is:

> **Make a market on your exact view.**

The intended distribution is both:

1. a first-party site centered on the blank-box question interface; and
2. an API through which wallets, exchanges, agents, communities, and existing prediction markets can request contracts and quotes.

No implementation is authorized by this document. Product planning continues while the Autobuilder remains the selected build priority. HBCC implementation issue #5396 is deferred until the Autobuilder is complete and the founder explicitly selects this initiative.

## 2. Founder insight hardened by this charter

A conventional prediction market usually treats every listed question as a separate product that must attract its own buyers, sellers, and market makers.

A personalized hedge-backed market can work differently:

```text
user asks a bespoke question
    -> compiler maps it into a common payoff basis
    -> shared external markets and internal netting provide a quote
    -> the bespoke contract can trade without first building its own crowd
```

This means a custom question does not necessarily require a custom pool of liquidity.

Examples such as:

- BTC above a threshold;
- BTC inside a range;
- BTC returning more than a chosen percentage;
- one asset outperforming another;
- a capped-linear payoff across a selected interval;

may appear as different markets to users while being combinations or projections of a common set of spot, futures, option, and collateral positions.

This is the controlling product-level insight. It supersedes any framing of HBCC as merely a research tool for scanning existing prediction-market listings.

## 3. Theory: Liquidity Inheritance for Personalized Markets

### 3.1 State-space view

Let `omega` represent a possible future market state or path.

A user-created contract defines a contingent payoff:

```text
Y(omega)
```

Standardized external instruments define available hedge payoffs:

```text
H_1(omega), H_2(omega), ..., H_n(omega)
```

The contract is statically compilable when the system can find quantities `a_i` such that:

```text
Y(omega) = sum_i a_i H_i(omega)
```

under matched settlement semantics.

It is boundedly compilable when:

```text
abs(Y(omega) - sum_i a_i H_i(omega)) <= epsilon
```

under a declared proof method, risk tolerance, and reserve.

The important consequence is that the number of user-facing questions can be much larger than the number of standardized instruments. Many questions are different functions, partitions, or projections of the same underlying future-state distribution.

### 3.2 Liquidity inheritance principle

A bespoke contract inherits liquidity when its risk can be transformed into positions in deeper standardized markets.

It does not inherit the entire headline liquidity of the underlying asset. It inherits only the executable capacity available through the required hedge transformation after:

- hedge ratios;
- displayed depth;
- market impact;
- settlement compatibility;
- fees and slippage;
- collateral requirements;
- residual-risk limits;
- execution and operational reserves.

Liquidity is therefore **transformed**, not copied.

### 3.3 Question density without liquidity fragmentation

If every custom question opens an isolated order book and waits for matching counterparties, personalization fragments liquidity.

If custom questions are quoted by a shared compiler and portfolio risk engine, personalization need not produce equivalent fragmentation. The system can create contracts lazily, on demand, without pre-funding every possible market.

The platform may support millions of possible specifications while only instantiating the contracts users actually request.

### 3.4 One-user market principle

A personalized contract can be economically meaningful even when only one customer requests it.

The product need not wait for another user who wants the exact opposite question. The system may quote against:

- an external hedge;
- internal offsetting inventory;
- committed risk capital;
- a fully collateralized paired-claim mechanism;
- or a hybrid of those sources.

This makes the initial interaction closer to an RFQ or automated structured-product desk than a conventional empty order book, while preserving a simple prediction-market experience.

### 3.5 Internal netting principle

Different questions may produce offsetting exposures even when their wording and payoff shapes differ.

The risk engine should evaluate the aggregate portfolio payoff rather than hedge every question independently. Internal netting can:

- reduce external hedge transactions;
- improve customer prices;
- expand supported capacity;
- reduce collateral use;
- create value from native market participation.

Netting must never obscure customer-level liabilities or settlement obligations.

### 3.6 Native participation principle

External hedge liquidity is the initial differentiator, not the only possible source of liquidity.

A personalized contract may begin as a private one-user position and later become:

- shareable;
- publicly discoverable;
- directly tradable by other users;
- supported by a native order book or AMM;
- standardized when repeated demand appears.

The mature liquidity stack is:

```text
external hedge liquidity
+ internal portfolio netting
+ native user liquidity
+ explicitly limited risk capital
```

## 4. Product architecture

### 4.1 Question Composer

Accepts natural-language intent and helps the user specify:

- underlying or market set;
- date, expiry, or observation window;
- threshold, range, comparison, or transformation;
- payout form;
- desired size;
- public or private market preference.

The Question Composer may feel intelligent, but the accepted contract must terminate in deterministic machine-readable semantics. Language-model output is not itself the source of truth.

### 4.2 Contract Compiler

Transforms supported intent into:

- `ContractSpec`;
- `SettlementSpec`;
- exact payout function;
- supported hedge basis;
- semantic-equivalence proof state;
- compile, modify, or reject decision.

HBCC is the core implementation of this layer.

### 4.3 Pricing and Liquidity Engine

Produces:

- executable replication cost;
- bid and ask;
- available size by price level;
- fees, reserves, and capital charge;
- limiting hedge leg or risk constraint;
- price-expiry-threshold alternatives when the requested contract is weakly supported.

### 4.4 Portfolio Risk and Netting Engine

Maintains the combined state-contingent liability across all contracts and separates:

- customer obligations;
- external hedge positions;
- collateral;
- residual exposure;
- settlement basis;
- operational and counterparty risk.

### 4.5 Claim Asset and Settlement Layer

Where legally and operationally permitted, an accepted position may be represented as a transferable on-chain claim asset.

The claim asset should encode or point to:

- the contract specification;
- payout rights;
- settlement source and procedure;
- collateral or backing model;
- expiry and redemption state.

An oracle or approved attestation supplies the settlement fact. The program applies the declared payout and permits redemption.

### 4.6 Market Promotion Layer

A private custom contract may later be published and promoted as a native market. Repeatedly requested contracts may become templates or standing public markets.

This turns user question demand into product-development data.

### 4.7 Distribution Layer

The same compiler should support:

- the first-party personalized-market site;
- an authenticated market-creation and quoting API;
- embedded wallet and exchange interfaces;
- existing prediction-market integrations;
- agent-generated market requests;
- internal operator and research tooling.

The first-party site owns the complete blank-box experience. The API is a distribution strategy, not a replacement for owning the user interface.

## 5. Blank-box user experience

The primary interface begins with:

> **What do you want to make a market on?**

Example request:

> Will Bitcoin be between $120,000 and $150,000 at the end of September?

The response should show:

- whether the exact request is supported;
- precise payout and settlement terms;
- YES/NO, range, scalar, or other payout representation;
- live bid and ask;
- current available size;
- maximum loss;
- backing classification;
- concise explanation of price provenance;
- alternatives with better liquidity when useful;
- controls to trade privately, publish, share, or revise.

The system should not force users to learn option-chain conventions before expressing their view.

## 6. Initial product language

The first problem already explored by PPE is buying probability sections of a future distribution.

The next product layer is to let the user express those sections as personalized questions.

Initial families to plan include:

- terminal price above or below a threshold;
- terminal ranges and buckets;
- capped-linear sections between two thresholds;
- percentage-return thresholds;
- comparisons among supported assets;
- simple baskets where static backing is defensible;
- selected option, volatility, basis, and funding observables in later stages.

The supported language should be broad enough to feel open-ended while remaining closed under explicit compiler rules.

Unsupported requests should receive:

- a clear rejection;
- the nearest supportable alternatives;
- an explanation of what prevents pricing or liquidity.

## 7. On-chain claim and custody models

Solana or another programmable settlement network may materially improve the product by making positions portable, self-custodied, composable, and automatically redeemable.

Three distinct models must not be conflated.

### 7.1 Fully collateralized paired claims

A participant deposits a unit of collateral and receives complementary claims whose combined terminal payout equals that collateral, such as YES plus NO.

Advantages:

- transparent full collateralization;
- simple terminal solvency;
- claim tokens can be self-custodied and traded;
- native participants can mint, split, combine, and redeem positions.

Constraint:

- native market makers and traders still determine useful pre-settlement liquidity unless an external hedge or protocol quote is added.

### 7.2 Hedge-backed issuance

The system sells a custom claim and acquires an external hedge intended to cover the payout.

Advantages:

- bespoke contracts can receive immediate one-sided quotes;
- liquidity can be inherited from standardized derivatives.

Constraints:

- if the hedge is off-chain, a smart contract cannot independently prove or control the full hedge without custody, attestations, or an integrated clearing arrangement;
- execution, margin, counterparty, and bridge risk remain;
- the issuer or protocol may still have material legal and operational responsibilities.

### 7.3 Hybrid portfolio model

The system combines:

- fully collateralized claims;
- external hedge positions;
- internal user netting;
- native market-maker capital;
- conservative residual-risk reserves.

This is the likely mature architecture, but it is more complex than the first proof.

### 7.4 Self-custody boundary

Users can hold claim assets in their own wallets. Collateral can be held by program-controlled vaults rather than a conventional company bank account. Settlement and redemption can be governed by program rules.

However:

> **Non-custodial software architecture does not by itself imply that the developer, operator, interface, oracle, market maker, or issuer has no regulatory responsibility.**

Control over listings, upgrade keys, oracle selection, fees, market access, hedge execution, or front-end operation may remain relevant.

## 8. Tax non-assumption

A transferable claim token is an asset with a value that changes before settlement. That may create useful portability and composability.

The product must not assume that tokenization automatically creates tax deferral.

Potentially taxable events may include:

- exchanging collateral or another token for a claim asset;
- selling or trading the claim before settlement;
- receiving settlement proceeds;
- operating as a frequent trader or business;
- fees or rewards earned by market makers or liquidity providers.

Tax character may depend on jurisdiction, facts, instrument design, and whether returns are treated as capital gains, business income, derivative income, gambling income, or another category.

Tax treatment is an external legal question, not a protocol property. No product claim about tax deferral is authorized without qualified advice for the target jurisdiction.

## 9. Theoretical liquidity stopping point

Liquidity for a custom contract is not infinite. At a requested customer price and size, support ends when no admissible portfolio satisfies all constraints.

For customer notional `N`, payoff `Y`, hedge quantities `a_i`, and hedge instruments `H_i`, the system seeks the largest `N` such that:

```text
residual risk is within limit
AND executable hedge depth is sufficient
AND total hedge cost plus reserves fits inside the customer quote
AND collateral and counterparty limits are satisfied
AND settlement compatibility is acceptable
AND legal and operational gates permit the transaction
```

The next stopping points are:

1. **Payoff span:** the requested payoff cannot be represented by supported hedge primitives within tolerance.
2. **Executable depth:** one or more hedge legs run out of size at acceptable prices.
3. **Market impact:** additional hedge size moves the external market enough to eliminate the quote economics.
4. **Collateral:** margin, premium, paired collateral, or duplicated venue collateral becomes limiting.
5. **Residual-risk budget:** basis, strike spacing, path dependence, or model error exceeds permitted exposure.
6. **Internal portfolio concentration:** net exposure becomes too concentrated in one state, expiry, venue, or oracle.
7. **Adverse selection and latency:** informed flow or hedge delay makes displayed quotes unsafe.
8. **Settlement and oracle risk:** the fact can no longer be resolved with sufficient integrity.
9. **Counterparty and bridge risk:** external venues, custodians, bridges, or stablecoins create an unacceptable failure bound.
10. **Regulatory and access limits:** product, jurisdiction, customer, or venue restrictions cap issuance.

A useful operational definition is:

> **Available liquidity is the maximum additional customer notional that can be transformed into an admissible net portfolio at the displayed quote.**

Internal netting can move this limit outward. Unoffset customer flow can move it inward.

## 10. Why the market is real

The product may feel like a "market laid over another market," but the custom claim is not fictitious.

It is a genuine state-contingent asset whose value is derived from:

- the future settlement state;
- the cost of replicating or financing that state exposure;
- native supply and demand;
- residual and operational risk.

The better description is:

> **A synthetic market overlay on standardized liquidity.**

The interface exposes personalized contingent claims. The underlying markets provide a common pricing and hedge basis.

## 11. Revenue model

Revenue occurs when a question becomes economic activity, not merely when text is generated.

Potential revenue includes:

- bid-ask spread;
- execution fee;
- contract-creation or RFQ fee;
- API and infrastructure fees;
- market-making revenue;
- settlement or oracle fee;
- listing and liquidity services for partner venues;
- premium analytics and risk tooling.

The platform may earn on every executed personalized contract while reusing common infrastructure and netting exposures across contracts.

The product must measure revenue after:

- external hedge spread and fees;
- market impact;
- capital and collateral cost;
- adverse selection;
- oracle and settlement cost;
- residual losses;
- operations and compliance.

## 12. Distribution choice

The product should be designed for both owned and partner distribution.

### First-party site

Owns:

- the blank-box interaction;
- user intent and question-demand data;
- personalization;
- publishing and social discovery;
- native liquidity growth;
- the complete product experience.

### API

Allows:

- existing prediction markets to request contract specifications and quotes;
- wallets and exchanges to embed custom markets;
- agents to create supported questions programmatically;
- professional customers to request structured RFQs;
- external applications to publish markets using the same compiler.

Selling to existing prediction markets is a distribution option and early revenue path. It is not the limiting definition of the product.

## 13. Expansion theory: from price states to market events

The planned expansion ladder is:

```text
probability sections
    -> personalized financial questions
    -> market-movement and volatility questions
    -> market-event inference
    -> external-event contracts and impact maps
```

### 13.1 Options as time-indexed state prices

Options across strikes and expiries encode market prices for future state exposure. They provide a distribution-like surface under risk-neutral pricing rather than a single forecast.

### 13.2 Volatility correction

Implied volatility should not be defined simply as confidence or lack of confidence.

A harder and more useful statement is:

> **Implied volatility is the market price of future dispersion and uncertainty, including risk premia and supply-demand effects.**

Directional and asymmetric information are distributed across:

- spot and forward levels;
- call-put relationships;
- skew;
- term structure;
- option flows and positioning.

A localized increase in implied variance around a time window can indicate that the market assigns extra value to movement or uncertainty in that window. It does not by itself identify the event, prove direction, or establish a real-world causal probability.

### 13.3 Market-movement contracts

The first event-like extension should remain directly market-observable:

- will realized movement exceed a threshold;
- will realized volatility exceed implied volatility;
- will the market leave a specified range;
- will correlation or basis break;
- will uncertainty rise in a chosen window.

These ask whether "something happens in the market" without claiming knowledge of the external cause.

### 13.4 Market-impact contracts

The next layer groups markets and asks how an event-shaped disturbance expresses itself:

- which asset group moves most;
- whether an impact is broad or sector-specific;
- direction and duration of the response;
- whether correlation rises or breaks;
- whether volatility is concentrated in a chosen window.

### 13.5 External-event contracts

A later system may define candidate external events, estimate their occurrence probabilities, and map expected market impacts.

That requires distinct components:

- event ontology;
- external resolution oracle;
- causal and conditional model;
- market-impact mapping;
- uncertainty and alternative-cause handling;
- separate distinction between event probability and hedgeability.

The system must not infer that an implied-volatility premium proves a named event will occur. It may use the premium as evidence that the market prices additional uncertainty in a window.

## 14. Role of the HBCC witness

The deferred Stage 0 witness is not the product vision.

It is a system-level calibration and honesty test intended to determine whether:

- contract payouts and hedge payouts are truly equivalent or bounded;
- executable costs are measured consistently;
- settlement mismatches are surfaced;
- available size is measured rather than imagined;
- different contracts can be valued on a comparable basis.

In that sense, the witness is an early balancer that helps make every emitted contract economically commensurable with its backing and risk.

The witness remains valuable, but it will run only after the Autobuilder is complete and the initiative is explicitly selected.

## 15. Five product truths to solve

The product mechanism and user-value proposition are coherent. The following are treated as engineering, market-structure, and distribution problems to solve:

1. **Expressiveness:** the supported question language regularly captures the view users actually want.
2. **Immediacy:** the system can return a reliable quote fast enough to preserve the magic of the blank box.
3. **Meaningful liquidity:** supported contracts offer useful size after real hedge and risk constraints.
4. **Simplicity:** the customer sees a clear question, payout, price, size, maximum loss, and settlement rule rather than an option-chain workflow.
5. **Unit economics:** fees and spread exceed hedge costs, capital cost, adverse selection, residual risk, settlement, and operations.

These are not reasons to shrink the vision. They are the main hypotheses the research and implementation program must test.

## 16. Planning work authorized now

While implementation is deferred, product-charter work may continue on:

- supported question ontology;
- payout and settlement grammar;
- on-chain claim architecture alternatives;
- liquidity-source and netting model;
- blank-box user journeys;
- API contract and integration concepts;
- backing and risk disclosure language;
- market promotion and standardization lifecycle;
- market-event and volatility research theory;
- legal, regulatory, tax, oracle, and custody question lists;
- staged feasibility and customer-discovery plans.

No production code, live-market execution, custody, token issuance, deployment, or customer launch is authorized.

## 17. Decisions preserved

1. Long-term product: personalized market creation through a blank-box interface.
2. Initial differentiator: financially resolvable contracts that inherit external hedge liquidity.
3. Core engine: HBCC.
4. Distribution: first-party site plus API.
5. Liquidity model: external hedges plus internal netting plus native participation.
6. Asset model hypothesis: self-custodied, transferable contingent claims with programmatic settlement where permitted.
7. Product honesty: liquidity is transformed and bounded, never described as infinite.
8. Tax boundary: tokenization does not itself prove tax deferral.
9. Regulatory boundary: non-custodial architecture does not itself remove operator obligations.
10. Execution detail: `MSOS_PERSONALIZED_MARKET_EXECUTION_DECISIONS_V0_1.md` controls hedge granularity, fractionalization, RFQ quoting, residual and settlement risk, API-first go-to-market, custody alternatives, legal gate, and initial fee-model hypotheses.
