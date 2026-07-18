# MSOS company vision v1

**Purpose:** Durable company-level product doctrine for Market Structure OS. This document defines the long-term destination, customer, product loop, expansion logic, and strategic constraints. It is **not** an instruction to widen the active BUILD queue.

**As-of:** 2026-07-13 · **Status:** Strategic north star · **Scope authority:** Active implementation remains governed by [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](../../SOP/MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md), [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](../../SOP/MINIMUM_CREDIBLE_DEMO_GATE_V1.md), and [`MSOS_FRONTIER.md`](../../SOP/MSOS_FRONTIER.md).

---

## Company thesis

Market software is fragmented around tools, data vendors, and instrument silos. Traders must manually carry context between charts, research, option chains, calculators, spreadsheets, brokers, alerts, and journals.

**MSOS should become one coherent environment that carries a market decision from understanding through strategy, execution, monitoring, and learning.**

The opportunity is not novelty for its own sake. Proven market capabilities may be integrated, recreated, or simplified when doing so removes workflow friction. The product advantage comes from:

- one shared model of the market decision;
- one continuous user workflow;
- accumulated decision context;
- reliable calculations and provenance;
- unusually legible UX;
- a build system that can absorb useful capabilities faster than conventional teams.

The autobuilder is the factory. It is not, by itself, the product, brand, or durable moat.

---

## Product promise

### External promise

> **Understand the market. Build the trade.**

MSOS helps users understand what the market is pricing, explore what could happen, compare ways to trade an outlook, monitor the resulting position or thesis, and learn from what happened.

### Internal product doctrine

> **Market understanding → belief → expression → execution → monitoring → learning**

“Belief to expression” remains a core intellectual primitive: markets imply beliefs, users hold beliefs, and financial instruments express differences between them. It is internal doctrine and advanced-product language, not necessarily the primary consumer tagline.

---

## The complete decision loop

The product must support the full loop over time:

1. **Observe** — What is happening now? What changed?
2. **Understand** — What happened before? What is unusual? What is the market pricing?
3. **Form a view** — What outcomes does the user consider plausible, and why?
4. **Choose a strategy** — Which available expression best fits the view, horizon, confidence, constraints, and portfolio?
5. **Execute** — Simulate, prepare, or eventually route the order through the user’s authenticated venue.
6. **Monitor** — What changed in the thesis, pricing, risk, or invalidation conditions?
7. **Learn** — Was the view, timing, sizing, or expression correct? What should change next time?

“Pre-belief” is useful internal reasoning but should normally appear in customer language as **market understanding**, **context**, or **orientation**.

A user-facing workflow should use ordinary questions:

- What is happening?
- What is the market pricing?
- What happened in similar situations?
- What could happen next?
- What do you think?
- What are the best ways to trade that view?
- What would change your mind?
- What happened, and what can you learn?

MSOS does not remove sophistication. It moves calculations, market structure, and instrument mechanics behind a legible interface while preserving inspectability.

---

## Initial customer

The initial user is **not the completely uninitiated beginner** and not a large institutional procurement department.

The first target is:

> **An emerging serious trader or very small trading team that understands basic markets but cannot yet assemble institutional-quality research, strategy construction, risk analysis, and workflow.**

Likely expansion path:

1. experienced retail and emerging serious traders;
2. small trading and research teams;
3. independent finance firms and emerging funds;
4. larger institutional deployments where justified.

The “hedge fund” ambition is initially functional rather than organizational: give a one-to-five-person operation capabilities that previously required a larger firm and a fragmented software stack.

---

## Strategic wedge

The broad company vision must be entered through one narrow, repeatable, high-value job.

Current wedge:

> **The easiest credible way to understand what a market is pricing and turn an outlook into a suitable strategy.**

The active BTC-options MCD is the first product witness of this wedge. It is not the whole company.

The wedge succeeds when a serious trader can:

- understand the market-implied view;
- compare it with a personal scenario or thesis;
- see the type of disagreement;
- compare plausible expressions;
- preserve the assumptions and result;
- reach clarity without a long guided explanation.

Do not broaden the BUILD queue merely because the long-term architecture supports more tools.

---

## Product surface over time

The eventual environment may include:

### Market understanding

- current market state and recent changes;
- historical context and comparable situations;
- market-implied probabilities and distributions;
- events, catalysts, positioning, volatility, term structure, and cross-market inconsistencies;
- provenance and timestamps for every material input.

### Guided outlook

Users may:

- enter an existing thesis;
- modify the market-implied outlook;
- explore scenarios without committing to a view;
- begin with no view and investigate what is happening.

### Strategy and expression search

The system may compare:

- spot or underlying exposure;
- options and option spreads;
- calendars and term-structure expressions;
- futures, prediction markets, or other supported venues;
- hedges for existing positions;
- waiting or declining the trade when pricing already reflects the view.

There is rarely one universal “optimal strategy.” Ranking must state the assumptions and tradeoffs: horizon, magnitude, confidence, volatility, liquidity, portfolio exposure, maximum loss, probability, and convexity.

### Portfolio, execution, monitoring, and learning

- portfolio-aware risk and concentration checks;
- read-only broker/account connection;
- paper execution and frozen forward records;
- broker-ready order tickets;
- later, direct user-authorized execution without MSOS custody where legally and technically appropriate;
- thesis, market-pricing, risk, and invalidation monitoring;
- decision journal and outcome review.

---

## Execution expansion sequence

Execution is a natural completion of the loop, but it must be staged:

1. **Read-only account connection** — positions, cash, exposure, cost basis, and open orders.
2. **Paper execution** — end-to-end workflow testing and forward performance records.
3. **Broker-ready order construction** — exact order prepared; user confirms through the venue.
4. **Direct authenticated execution** — only after product reliability, legal review, permissions, and operational controls.
5. **Multi-broker and team controls** — approvals, limits, audit history, and shared portfolios.

Not holding customer assets may reduce custody complexity but does not automatically remove regulatory obligations created by recommendations, trade facilitation, or order routing.

Solana wallets and on-chain settlement are relevant for supported crypto-native markets. They are not a universal replacement for regulated brokerage integrations.

---

## Workflow import doctrine

MSOS should copy **workflows**, not blindly copy applications.

For every observed trader process, capture:

> **Trigger → Orientation → Hypothesis → Validation → Instrument selection → Position construction → Execution → Monitoring → Review**

Study:

- what initiated the decision;
- which questions were asked;
- which data, content, and tools were consulted;
- where the user switched applications;
- what information was copied manually;
- which calculations were performed;
- what was saved and what was lost;
- how the thesis was monitored and invalidated;
- how the result was later reconstructed or distorted by hindsight.

The opportunity is usually in eliminating context handoffs, not reproducing every visible feature.

Operational method lives in [`TRADER_WORKFLOW_RESEARCH_V1.md`](../../SOP/TRADER_WORKFLOW_RESEARCH_V1.md).

---

## Build, integrate, clone, avoid

Use this hierarchy for capabilities:

1. **Integrate** when the capability is standardized, reliable, and not strategically differentiating.
2. **Clone and simplify** when incumbents prove demand but the workflow or UX is bloated, fragmented, or inaccessible.
3. **Build deeply** when the capability defines the shared market model, decision loop, trust layer, or differentiated analytical engine.
4. **Avoid or defer** when the capability does not reinforce the active workflow or create reusable decision context.

Do not rebuild a complete commodity platform when a focused component or integration completes the workflow. For example, MSOS may need enough charting to attach evidence to a thesis without recreating every function of a dedicated charting terminal.

Respect intellectual property, data licences, contracts, trademarks, and applicable law. “Clone” means independently implement proven product functionality and workflow patterns, not copy protected source code, proprietary data, or distinctive assets.

---

## Shared platform model

The long-term platform should converge on stable shared objects rather than disconnected mini-apps.

Canonical objects may include:

- asset, market, venue, instrument, and event;
- market observation and evidence;
- scenario, thesis, probability, and disagreement;
- strategy, expression, order, position, and portfolio;
- risk, constraint, catalyst, and invalidation;
- alert, decision, frozen evaluation, and outcome review.

Architectural layers:

1. **Canonical market and decision objects**
2. **Data and venue adapters**
3. **Analytical engines**
4. **User-facing tools and views**
5. **Cross-tool workflow layer**
6. **Agent assistance and automation layer**

New tools should become views and operations on shared objects whenever possible. They should not create isolated duplicate state, math, or workflow channels.

---

## Durable advantage

Fast implementation is a current advantage, but other teams will gain comparable coding capacity. Durable advantage must compound elsewhere:

- canonical market-reasoning and decision objects;
- accumulated user theses, decisions, portfolios, and preferences;
- cross-tool workflows that preserve context;
- reliable, reproducible, inspectable calculations;
- data provenance and frozen historical records;
- product judgment and legible interaction design;
- integrations and ecosystem participation;
- observed workflow knowledge;
- trust earned through honest limitations and performance records.

Network effects are welcome but not required for the first user to receive substantial value.

Potential later network effects:

- reusable strategy and workflow templates;
- public timestamped analyses;
- creator-linked strategy pages;
- team playbooks and shared decision records;
- verified paper and live histories kept distinct from backtests;
- marketplaces for modules, data, or analytical workflows;
- trained operators and firms using a shared software standard.

---

## Frozen decision record

MSOS should preserve what was knowable and believed at the time of a decision.

A frozen record may contain:

- timestamp and available source data;
- market-implied probabilities or distributions;
- user thesis and assumptions;
- strategies considered and selected;
- entry, sizing, risk, and invalidation criteria;
- expected outcomes;
- subsequent market and position outcome.

Always distinguish:

- **historical simulation / backtest**;
- **paper-traded forward record**;
- **live-traded record**.

This is strategically valuable for learning, research integrity, creator credibility, team audits, and eventual agent evaluation.

---

## Content and distribution flywheel

A future media loop may:

1. identify a public market thesis;
2. translate it into explicit assumptions;
3. show what the market currently prices;
4. compare several suitable expressions and tradeoffs;
5. freeze the analysis at publication time;
6. track the result;
7. let viewers open or adapt the analysis inside MSOS.

Content should avoid declaring a universal “optimal strategy.” Prefer:

> **Here are several ways to trade this thesis, what each assumes, and who each may fit.**

The content loop can simultaneously generate education, product demonstration, acquisition, workflow research, historical validation, and product testing. Public content and execution-adjacent features require appropriate disclosures and legal review.

---

## Education and certification

Certification is a later-stage ecosystem, not MVP scope.

MSOS may eventually certify software competency in:

- interpreting market expectations;
- constructing and comparing scenarios;
- selecting instruments and modelling payoff/risk;
- preserving reproducible research and decision records;
- operating team workflows and controls.

MSOS certification must not be represented as replacing government, exchange, employer, or self-regulatory qualifications. Any recognized regulatory or professional pathway would require separate approval or partnership.

Potential long-term flywheel:

> learners seek MSOS competency → firms adopt MSOS because trained operators exist → job demand attracts more learners → ecosystem value increases.

---

## Platform-bloat gate

Add or deeply build a capability only when it satisfies at least three of the following:

- removes an application switch from the active decision workflow;
- operates on existing shared objects;
- is repeatedly observed in real trader behaviour;
- improves completed decisions, retention, trust, or learning;
- creates information useful elsewhere in MSOS;
- can be materially simplified or improved relative to alternatives;
- strengthens the current wedge or unlocks its next validated stage.

Otherwise integrate it, link to it, research it, or defer it.

---

## Sequence doctrine

Research may be broad. Architecture may remain platform-ready. BUILD must stay sequential.

1. stabilize the autobuilder and product-delivery system;
2. pass the current Minimum Credible Demo;
3. ingest observed trader workflows;
4. deliver one complete understanding-to-strategy loop;
5. add frozen records, monitoring, and paper execution;
6. add read-only portfolio and broker context;
7. earn the right to live execution and broader modules;
8. add team, content, education, and institutional layers only when supported by evidence.

**Research broadly, model the whole system, but build one complete user journey at a time.**

---

## Decision rules for agents and builders

- Treat this document as the destination, not the immediate backlog.
- Do not pull live execution, new assets, broad marketplace features, certification, or institutional controls into active scope without explicit steward SELECTION and supporting evidence.
- Preserve “belief to expression” as product doctrine while using ordinary external language.
- Prefer workflow coherence over feature count.
- Prefer shared objects over duplicate mini-app state.
- Prefer observable behaviour over requested feature lists.
- Prefer a small end-to-end product witness over a large partially connected platform surface.
- When a proposed feature is exciting but not required by the current complete user journey, record it and defer it.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-13 | v1 — company thesis, complete decision loop, initial customer, wedge, workflow import, expansion sequence, moat, content/certification vision, and anti-bloat doctrine |
