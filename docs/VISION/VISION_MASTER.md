# VISION_MASTER

Stable **product vision** (long-range intent) for the Probability Prediction Engine. This is **intent**, not implementation. For the current build cycle’s focus, pair with `PHASE_VISION_CURRENT.md`.

## Product promise

Help people **see** how **market data** and **prediction markets** relate on comparable events—surfacing angles like arbitrage, near-arbitrage, and unusually high-probability setups—without pretending the tool is omniscient. Visualization and **legibility** are first-class; automation and derived questions grow **after** the core picture is trustworthy.

## Core user experience

- **Compare like with like** using **canonical events** (e.g. level-by-date style questions across assets and sources).
- **Understand priced information vs personal views**: what the market **prices** (risk-neutral / implied distribution) vs what the user **believes**, and the **structured gap** between them.
- **Explore structure**, not get a black-box ticket: modes such as strike-first vs payoff-first, strategy **families** as fit classes, and **verification** that ties numbers back to sources and assumptions.

## Must-have qualities

- **Honest labeling** — priced/implied ≠ “what the market truly believes”; disagreement is **descriptive**, not a buy/sell command.
- **Traceability** — major outputs link to data, time, and method (`docs/SEMANTIC_CONTRACTS.md` verification intent).
- **Local usability** — a credible path to run and inspect the product on a developer machine (`README.md`).

## Must-not-break truths

- **Semantic contracts** for market-implied distribution, user belief, disagreement, strategy family vs exact priced structure, fit vs recommendation — meanings must not silently drift.
- **Sign and source discipline** — conventions for debit/credit and source hierarchy stay consistent across UI and calculations.
- **Boundary honesty** — the product offers legibility and exploration, not guaranteed edge, portfolio advice, or execution advice (`docs/SEMANTIC_CONTRACTS.md` §13).

## Anti-goals

- **Recommendation theater** — no “recommended trade” voice unless an explicit advisory layer is built and scoped.
- **Scope smuggling** — no framing implied distributions as pure belief, or illustrative patterns as live optimized tickets.
- **Product vision as backlog** — this file does not replace phase specs, feature slices, or `docs/SOP/ORIGINAL_SPEC.md` for cycle execution.

## Design / interpretation principles

- **Clarity over cleverness** — users should grasp *what* is shown and *what it is not* quickly.
- **One coherent story per surface** — especially on dense screens: implied view, belief inputs, payoff, and stats should reinforce each other.
- **Defer depth** — advanced math and secondary detail stay available but out of the default path when the phase calls for it.

## What success should feel like

A thoughtful user leaves with **clear mental models**: what was **priced**, what they **assumed**, how a **structure** maps to that, and where to **check** the chain. The system feels **calm and inspectable**, not like a slot machine or a hidden model.
