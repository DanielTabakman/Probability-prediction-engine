# MSOS Personalized Market execution decisions v0.1

**Status:** PROPOSED FOR REVIEW — planning decisions only; implementation deferred  
**As-of:** 2026-07-20  
**Owner:** MSOS steward  
**Parent vision:** [`MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`](MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md)  
**Core engine:** [`MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md`](MSOS_HEDGE_BACKED_CONTRACT_COMPILER_INITIATIVE_V0_1.md)  
**Deferred feasibility issue:** [#5396 — HBCC Stage 0 single-contract compilation witness](https://github.com/DanielTabakman/Probability-prediction-engine/issues/5396)

## 1. Executive decision

The project will proceed under the following product model once the Autobuilder is complete and this initiative is explicitly selected:

> A personalized derivatives market with a prediction-market interface, exposed through both a first-party blank-box site and an API.

The initial go-to-market is API-first for existing prediction markets, hedge funds, research labs, forecasters, wallets, exchanges, agents, and other professional or embedded distribution partners. The first-party site remains the strategic destination and owns the complete user experience.

The core product loop is:

```text
user or API client asks for the exact market they want
    -> Question Composer produces deterministic intent
    -> HBCC compiles the intent into payoff, settlement, hedge, price, and capacity
    -> quoting layer returns an indicative or firm quote plus available size
    -> accepted positions become transferable claims where permitted
    -> portfolio engine nets exposures and acquires external hedges
    -> oracle or approved settlement source resolves the claim
    -> holder redeems the payout
```

No production implementation, live trading, customer funds, token issuance, or deployment is authorized by this document.

## 2. Decision: customer size may be smaller than hedge-lot size

The minimum tradable unit of an external hedge does **not** have to become the minimum customer position.

It sets **hedge granularity**, not the final customer denomination.

The system may support smaller customer positions by:

- pooling multiple customer requests into one external hedge lot;
- issuing fractional claim units against a larger fully collateralized or hedged position;
- warehousing a small bounded residual until the next customer or hedge batch arrives;
- using internal netting across related customer contracts;
- batching requests at fixed intervals or when a hedge threshold is reached;
- using a native market maker or liquidity provider to bridge the temporary mismatch.

The customer-facing claim may therefore be divisible even when the underlying option or futures hedge is not.

This creates a required accounting invariant:

```text
total outstanding customer claim liability
    <= verified collateral + admissible external hedge value + declared residual-risk reserve
```

The system must track fractional customer obligations exactly. Fractionalization may reduce customer minimum size; it does not create additional aggregate hedge capacity.

## 3. Decision: meaningful executable size is an upper-bound problem

The minimum hedge lot answers:

> What is the smallest external hedge unit?

It does not answer:

> How much total customer notional can the system quote?

For a requested contract and maximum acceptable customer price, supported size ends when one of these becomes binding:

- executable hedge depth;
- price impact;
- collateral or margin;
- residual-risk limit;
- portfolio concentration;
- settlement compatibility;
- venue, counterparty, bridge, or stablecoin exposure;
- legal or access restrictions.

The operational definition remains:

> **Available liquidity is the maximum additional customer notional that can be transformed into an admissible net portfolio at the displayed quote.**

The quote response should therefore expose a size ladder rather than one vague liquidity number:

```text
price <= P1: size N1
price <= P2: cumulative size N2
price <= P3: cumulative size N3
```

## 4. Decision: use an RFQ and limit-order model, not an always-firm instant promise

The product does not initially require every custom contract to receive a continuously firm millisecond quote.

A practical first quoting model is:

1. **Immediate indicative quote** from the latest compiled surface and cached executable data.
2. **Firm quote request** that refreshes the required external books and risk state.
3. **Short quote-validity window** or market-move invalidation condition.
4. **Limit instruction** such as:

```text
Buy up to N units at no more than P per unit.
```

5. **Partial fill permission** where the user allows it.
6. **Batching or queueing** for customer requests below external hedge granularity.
7. **Automatic cancellation or re-quote** when the hedge can no longer be acquired within the declared price.

This interaction is closer to a consumer-friendly RFQ desk than an empty conventional order book.

Being slower than a liquid spot exchange may be acceptable for wealth, structured exposure, and custom positions. The acceptable latency remains an empirical product question and should depend on:

- underlying volatility;
- customer size;
- hedge depth;
- quote duration;
- whether the customer submits a limit rather than demanding immediate execution;
- the platform's stale-quote loss rate.

## 5. Residual risk explained

Residual risk is the portion of the customer's payout that is not exactly offset by the external hedge.

Let:

- `Y(omega)` be the customer claim payout;
- `H(omega)` be the hedge payout.

Then:

```text
residual(omega) = Y(omega) - H(omega)
```

Example:

- customer claim pays `$1` when BTC settles at or above `$150,000`;
- hedge is a normalized `$145,000 / $155,000` call spread;
- at `$150,000`, the call spread pays roughly `$0.50` while the customer claim pays `$1`;
- the system remains short approximately `$0.50` per claim in that state.

That difference is residual payoff risk.

Residual risk can arise from:

- finite strike spacing;
- payout-shape mismatch;
- path dependence;
- dynamic hedge slippage;
- basis differences;
- incomplete fills;
- fractional hedge-lot mismatch;
- model error;
- operational failure.

The compiler must either:

- eliminate the residual;
- prove a mathematical bound and reserve against it;
- modify the customer payout to match the natural hedge;
- or reject the request.

## 6. Settlement risk explained

Settlement risk exists when the customer claim and hedge depend on different settlement facts or procedures even if their headlines appear equivalent.

Example:

- customer contract resolves using Coinbase BTC/USD at 11:59 p.m. ET;
- external option settles using a Deribit index at 08:00 UTC;
- BTC can be above the threshold at one observation and below it at the other;
- the customer claim can pay `$1` while the hedge pays `$0`.

Settlement risk includes:

- different index or venue;
- different timestamp or timezone;
- different averaging window;
- different currency or conversion rule;
- oracle failure or manipulation;
- exchange outage;
- different fallback or correction procedures;
- disagreement over finality.

The preferred design is to define the customer contract around the hedge instrument's official settlement semantics whenever that remains understandable and commercially useful.

A token or smart contract can automate the declared settlement rule. It cannot make an ambiguous, manipulable, or incompatible rule safe merely by placing it on-chain.

## 7. Decision: external hedge custody is an architecture choice, not a thesis blocker

The external hedge may be held through several models.

### 7.1 On-chain hedge model

Use on-chain spot, options, perpetuals, lending, or other approved instruments where sufficient liquidity and settlement compatibility exist.

Advantages:

- programmatic visibility;
- atomic or near-atomic settlement opportunities;
- transparent collateral;
- reduced reconciliation friction.

Risks:

- smart-contract failure;
- oracle failure;
- bridge and stablecoin exposure;
- protocol liquidity limits;
- venue concentration.

### 7.2 Traditional broker or prime model

The operating entity or an approved liquidity provider holds external options, futures, spot, and collateral through a broker, futures commission merchant, prime broker, custodian, or exchange account.

Advantages:

- access to deeper traditional markets;
- established margin and clearing infrastructure;
- professional execution.

Risks:

- counterparty and custody exposure;
- reconciliation between on-chain claims and off-chain hedges;
- capital fragmentation;
- account and jurisdiction restrictions.

### 7.3 Hedge-fund or market-maker partner model

A licensed or otherwise legally eligible hedge fund, derivatives dealer, market maker, or venue provides signed executable quotes or acts as the direct issuer or hedge counterparty.

The API may supply:

- deterministic contract specification;
- settlement rules;
- hedge request;
- price and size request;
- resulting claim metadata;
- reconciliation and risk data.

This model may reduce the need for MSOS to become the initial balance-sheet counterparty, but it does not eliminate legal, technical, or counterparty diligence.

### 7.4 Hybrid collateral and hedge model

Use:

- on-chain program-controlled collateral;
- off-chain external hedges;
- attestations or signed position evidence;
- internal netting;
- liquidity-provider capital;
- residual-risk reserves.

This is a plausible mature architecture and must be evaluated against solvency, enforceability, operational control, and regulatory requirements.

## 8. Decision: legal status is unresolved and requires qualified counsel before launch

At the current planning stage, the project is not executing customer trades or operating a venue.

The future product must not assume:

> We are not breaking laws because the contracts are self-custodied or implemented as smart contracts.

Official regulatory materials treat many event contracts as derivatives and emphasize that tokenization does not change the legal nature of the underlying instrument. Canadian regulators have also treated users' contractual rights involving crypto assets as potentially securities or derivatives depending on the structure.

Therefore:

- no public launch occurs without qualified legal review for the target jurisdiction and operating model;
- the legal analysis must cover issuer, dealer, marketplace/exchange, clearing, custody, derivatives, securities, gambling, payments, AML/KYC, oracle, marketing, and customer-access questions;
- product architecture should preserve partnership routes with existing regulated venues, dealers, hedge funds, and custodians;
- the API may begin as contract-design, pricing, research, and liquidity infrastructure where legally appropriate, but labels do not control substance;
- legal review is a launch gate, not a reason to stop product planning.

Relevant official starting points:

- CFTC: https://www.cftc.gov/LearnandProtect/PredictionMarkets
- OSC Bitvo decision: https://www.osc.ca/en/securities-law/orders-rulings-decisions/bitvo-inc
- SEC tokenized securities statement: https://www.sec.gov/newsroom/speeches-statements/corp-fin-statement-tokenized-securities-012826-statement-tokenized-securities

## 9. Decision: API-first go-to-market

The initial commercial distribution plan is API-first.

Target API customers and partners include:

- existing prediction markets;
- options, derivatives, and crypto venues;
- hedge funds and market makers;
- research labs and forecasting organizations;
- wallets and broker interfaces;
- autonomous agents;
- professional traders and structured-product desks.

The API may expose bounded functions such as:

```text
POST /contract/compile
POST /quote/indicative
POST /quote/firm
POST /order/limit
GET  /contract/{id}
GET  /quote/{id}
GET  /position/{id}
GET  /settlement/{id}
```

Conceptual request:

```json
{
  "intent": "Will BTC be between 120000 and 150000 at the selected expiry?",
  "size": 5000,
  "max_price": 0.47,
  "partial_fill": true,
  "visibility": "private"
}
```

Conceptual response:

```json
{
  "status": "supported_with_modification",
  "contract_spec": {},
  "settlement_spec": {},
  "indicative_bid": 0.42,
  "indicative_ask": 0.46,
  "available_size": 18500,
  "quote_type": "indicative",
  "backing_class": "external_hedge_plus_internal_netting",
  "risk_flags": [],
  "alternatives": []
}
```

The first-party site remains part of the intended product. API-first distribution is the initial acquisition and integration strategy, not abandonment of the owned interface.

## 10. Decision: initial fee model hypothesis

The initial unit-economics hypothesis is:

```text
customer price
    = executable hedge or net portfolio cost
    + pass-through venue and settlement costs
    + risk and capital reserve
    + percentage platform fee
    + minimum platform fee
```

Possible components:

- percentage of notional;
- minimum fee per issued contract or RFQ;
- bid-ask spread;
- explicit quote or execution fee;
- API subscription or usage fee;
- partner revenue share;
- settlement or oracle fee;
- premium for highly customized, small, or operationally expensive contracts.

The credit-card-style structure of `percentage + minimum + pass-through costs` is the default hypothesis to test.

It is not yet accepted as economically viable. The fee must be tested against:

- external hedge spread and fees;
- market impact;
- collateral and financing;
- adverse selection;
- residual losses;
- settlement and oracle costs;
- partner economics;
- customer willingness to pay.

## 11. Why these problems were raised

The problems were not random, and they were not assigned to the founder because the system could not reason about them.

They are the unavoidable constraint classes in any product that promises to:

```text
quote
    -> issue
        -> hedge
            -> transfer
                -> settle
                    -> redeem
```

They fall into four categories.

### 11.1 Product and architecture decisions

Can be substantially reasoned about and chartered now:

- blank-box interface;
- API-first distribution;
- RFQ and limit-order quoting;
- fractional customer claims;
- liquidity-source hierarchy;
- fee-model hypothesis;
- private-to-public market lifecycle.

### 11.2 Empirical engineering questions

Require later market data, prototypes, and runtime evidence:

- executable depth;
- quote latency;
- residual payoff bounds;
- settlement compatibility;
- internal netting effectiveness;
- adverse selection;
- real unit economics.

### 11.3 External-authority questions

Require qualified outside professionals or counterparties:

- legal and regulatory treatment;
- tax treatment;
- licensing or exemptive-relief path;
- custody and clearing arrangements;
- enforceability of claims and partner contracts.

### 11.4 Market-discovery questions

Require prospective users and partners:

- which contract families are wanted first;
- acceptable quote speed;
- acceptable fees;
- useful minimum and maximum sizes;
- partner integration requirements;
- willingness to let the API or MSOS own the customer relationship.

The purpose of surfacing these classes is to prevent a coherent vision from being mistaken for a completed operating system. They are not objections to the product. They are the work program required to make the product true.

## 12. Decisions preserved going forward

1. Product: personalized derivatives with a prediction-market interface.
2. Primary UX: a blank box where the user asks for the exact supported market they want.
3. Initial scope: financially resolvable questions with external hedge inheritance.
4. Core engine: HBCC.
5. Liquidity: external hedges plus internal netting plus native participation plus bounded risk capital.
6. Position model: divisible and potentially transferable customer claim assets where permitted.
7. Customer size: may be smaller than external hedge-lot size through pooling and fractionalization.
8. Quote model: indicative quote, firm RFQ, limit price, partial fills, batching, and re-quote rules.
9. Distribution: API-first plus strategic first-party site.
10. Initial customers: prediction markets, hedge funds, market makers, research and forecasting organizations, wallets, venues, and agents.
11. Revenue hypothesis: pass-through costs plus risk/capital charge plus percentage and minimum fee.
12. Custody: evaluate on-chain, traditional, partner, and hybrid hedge models.
13. Regulation: unresolved; qualified legal review is mandatory before customer-facing launch.
14. Execution: deferred until Autobuilder completion and explicit initiative selection.
15. Product honesty: payout, hedge, settlement, capacity, and backing classifications remain explicit.

## 13. COORDINATION STATUS

Agreement: aligned  
Compared: founder personalized-market direction; `MSOS_PERSONALIZED_MARKET_COMPILATION_VISION_V0_1.md`; HBCC charter; deferred issue #5396  
Disagreement: none on product direction; one correction retained — option minimum lot defines hedge granularity, not total capacity or necessarily customer minimum size  
Evidence gap: real depth, quote latency, residual bounds, custody path, legal treatment, partner demand, and unit economics remain unproven  
Ownership overlap: none; documentation-only planning  
Risk if unresolved: future implementation may confuse fractionalization with new liquidity, or may underprice residual, settlement, legal, and operational risk  
Recommended default: accept these as planning decisions, keep implementation deferred, and use this document as the next-level execution theory beneath the parent vision  
Founder decision required: yes — approve, revise, or reject this planning document
