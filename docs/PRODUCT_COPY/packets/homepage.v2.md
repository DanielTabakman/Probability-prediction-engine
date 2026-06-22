---
surface: homepage
version: 2
status: approved
content_file: apps/msos-web/src/content/homepage.ts
author: copy-agent
as_of: 2026-06-22
north_star: >-
  See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds.
notes: >-
  Operator 2026-06-22: h1 locked to v1 (B — reason-about thesis). Primary CTA = Try the BTC Options Lab
  (honest for current product size). Revisit Explore the platform when platform breadth ships.
  Problem/proof UI sections deferred — not on page today.
supersedes: docs/PRODUCT_COPY/packets/homepage.v1.md
---

# Homepage copy v2 (draft)

### Audience

Options traders with a market view — cold traffic, 5-second clarity test.

### Conversion job

Understand value → try BTC Options Lab (primary) or join research beta (secondary).

---

## Hero

#### hero.eyebrow
For traders with a market view

#### hero.h1
Turn your market thesis into a trade you can reason about.

#### hero.body
Market Structure OS helps traders compare market-implied probabilities with their own view, locate meaningful disagreement, and explore structures that fit the thesis — without hiding the assumptions.

#### hero.primaryCta
Try the BTC Options Lab

#### hero.secondaryCta
Open Command Center

#### hero.signInCta
Sign in

#### hero.pills
- Your thesis stays yours
- Expression, not recommendation
- Live BTC options preview

---

## Problem block (BUILD — section not in UI yet)

#### problem.title
Thesis to trade is harder than it sounds

#### problem.body
You often have a view — but the market may already price it. The hard part is seeing what options imply, where you actually differ, and whether any structure fits your conviction and risk. Spreadsheets and gut feel hide that gap.

---

## Product cards (benefits pass)

#### productCards.marketStructureOs.title
Market Structure OS

#### productCards.marketStructureOs.body
One workspace to go from market view to paper trade — thesis, comparison, and review in one place.

#### productCards.strategyLab.title
Strategy Lab

#### productCards.strategyLab.body
See live BTC options data, state your view, and compare it to what the market prices today.

#### productCards.probabilityEngine.title
Probability Engine

#### productCards.probabilityEngine.body
Find where options pricing agrees — or disagrees — with your thesis before you choose a structure.

---

## Proof block (BUILD — section not in UI yet)

#### proof.line
Built for options traders and macro thinkers who want a faster path from belief to payoff — paper trading only today.

---

## Features row (unchanged structure — tightened bodies)

#### features.read.title
See what the market implies

#### features.read.body
Start with live BTC options — what's priced in, and what range the market expects.

#### features.state.title
Add your thesis

#### features.state.body
State your view in plain terms so you can compare it to the market, not just hold it in your head.

#### features.fit.title
Explore possible expressions

#### features.fit.body
See payoff shapes that fit your view and risk — paper only, no live orders.

#### features.learn.title
Track what happened

#### features.learn.body
Review what you believed, what the market implied, and how the thesis played out over time.

---

## CTA repeat (BUILD — section not in UI yet)

#### ctaRepeat.primary
Try the BTC Options Lab

#### ctaRepeat.secondary
Join research beta and shape the workflow

---

## Metadata

#### metadata.title
Market Structure OS — Compare your thesis to options pricing

#### metadata.description
See where your market view disagrees with BTC options. Compare implied probabilities, explore structures that fit — paper trading only.

---

## Three-pass notes (hero.h1)

| Pass | Text |
|------|------|
| Literal | Compare your thesis to options-implied probabilities |
| Value | See whether the market already prices your view |
| Action | Find disagreement worth expressing — then choose a structure that fits |

**Shipped candidate:** See where your market view disagrees with options pricing.

---

## Operator decisions (2026-06-22)

| key | Choice | Rationale |
|-----|--------|-----------|
| hero.h1 | **B — v1** (reason about) | Operator preference over sharp disagreement line |
| hero.primaryCta | **A — Try the BTC Options Lab** | Honest entry while product is lab-first; not full platform yet |
| hero.primaryCta (future) | **Explore the platform** | When Command Center + surfaces feel like a big platform |
| problem/proof sections | **Skip for now** | No UI blocks on homepage — hero + features enough today |

## v1 → v2 shipped delta

| key | v1 | v2 (shipped) | why |
|-----|----|----|-----|
| hero.h1 | (same) | (same) | Operator locked B |
| hero.primaryCta | Explore the platform | Try the BTC Options Lab | Specific, honest demo path |

---

## Copy agent checklist

- [ ] Operator picks h1 (v2 sharp vs v1 reason vs 15s north-star literal)
- [ ] CTA routes unchanged (Strategy Lab + research offer URL)
- [ ] Problem/proof/ctaRepeat — BUILD slice if approved
- [ ] Validator after hero/features promotion
