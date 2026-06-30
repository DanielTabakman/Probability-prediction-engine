# MSOS UX Design Philosophy v1

**Purpose:** Canon interaction and visual design principles for **user-facing MSOS modules** — the surfaces traders actually open and use.

**Scope:** Applies to MSOS-owned UI (`apps/msos-web/`, module routes, Command Center cards, embed shells) and to PPE surfaces when rendered inside MSOS or as standalone trader tools. Does **not** govern control-plane scripts, relay automation, or internal admin tooling.

**As-of:** 2026-06-30

**Related (do not duplicate):**

| Doc | Role |
|-----|------|
| [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) | Platform ownership, module boundaries |
| [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) | Analytical modules, tiers, pillars |
| [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) | P0–P8 waterfall, product hierarchy |
| [`PHASE_2_CHARTER.md`](PHASE_2_CHARTER.md) | PPE implied-lab desirability track (subset of this philosophy) |
| [`SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md) | Honest market/belief language |
| [`docs/agents/ux_legibility_reviewer.md`](../agents/ux_legibility_reviewer.md) | Agent review checklist |

---

## North star

**Market Structure OS** is a **collection of useful market tools** traders want to open, use, and return to — not a single workflow locked to one mental model.

The long arc still includes thesis → market structure → expression → review. **This philosophy governs the side quest that matters now:** make each module feel as immediately playable as the best video games and casino apps — while optimizing for **competence and trust**, not compulsion or false certainty.

**We borrow interaction craft from high-engagement games and casinos. We refuse their exploitation patterns.**

---

## Product frame

| Layer | What it is |
|-------|------------|
| **MSOS** | Platform shell — navigation, identity, workflow glue, module hosting |
| **User-facing module** | One bounded tool answering one primary market question (see module registry) |
| **Examples today** | Options Horizon, Strategy Lab / implied distribution, Exposure menu, forward consistency, cross-venue gap — more over time |

**Pillars** (from module registry): **workflow**, **edge**, **legibility**. A module may serve one pillar primarily; the platform should still feel like one coherent cockpit.

**Not the whole story:** disagreement / belief-vs-market is **one** relationship mode (mainly Strategy Lab). Other modules are chart-first, consistency radar, exposure paths, event gaps, etc. Design each module around **its** primary question — shared mechanics below still apply.

---

## Aesthetic target

**Serious game / trading cockpit / casino instrument panel** — not a generic finance dashboard or dense quant form.

- Dark, high-contrast market cockpit where appropriate (storyboard v0.6 direction).
- One hero object per screen; everything else supports or expands.
- Motion and sound are **punctuation** on insight moments, not noise on every click.
- Depth exists; the first screen is never a wall of equal-weight fields.

---

## Core principles

1. **One-screen first, depth second** — primary read + primary control visible without a treasure hunt.
2. **Trust / provenance is first-class** — compact, always findable; never debug-only ornament.
3. **Fit and exploration, not recommendation** — no trade signals, guaranteed edge, or autonomous authority language unless an explicit advisory layer is chartered.
4. **Human controls** — sliders, presets, regions, chips; not raw parameter dumps.
5. **Progressive disclosure** — advanced math, order books, provenance behind clear expanders.
6. **Module identity on load** — user knows *which tool* they are in and *what question it answers* within ~15 seconds.
7. **Platform coherence** — shared nav, trust patterns, and density; each module keeps its own hero object.

---

## Interaction mechanics (game / casino craft, ethical use)

These patterns create pull **without** dark patterns. Every user-facing module should implement as many as apply.

### 1. Zero-friction first action

User does something meaningful in seconds. No tutorial wall before the first feedback moment.

**MSOS:** preloaded chart/state, one obvious preset or control, short invitation copy on load.

### 2. Tight feedback loops

Every meaningful input produces visible change with low perceived latency. Cause and effect stay on the same screen.

**MSOS:** control → chart / summary / card update in place (not “submit then scroll”).

### 3. Variable insight (not variable reward)

Curiosity stays high because outcomes differ — sometimes flat, sometimes a sharp read. Unpredictability of **insight**, not of money.

**MSOS:** consistency flags light up, horizon regions shift, exposure paths reorder — not jackpot fanfare.

### 4. One hero object

One primary object owns attention: the chart, the insight card, the slip-like summary strip. Secondary panels orbit.

**MSOS:** Options Horizon = price×time canvas; Strategy Lab = distribution + headline read; Exposure = path menu — each picks **one** nucleus.

### 5. Progressive disclosure

Simple first path; depth on demand. Tabs and expanders, not deletion of rigor.

**MSOS:** Greeks, archive provenance, cross-venue detail behind “more” affordances.

### 6. Session continuity

The product remembers context across visits.

**MSOS:** last asset, saved thesis, monitor cards, “market moved since you last looked” (when workflow tier ships).

### 7. Ambient aliveness

Surface feels live — freshness, trust state, market context — without fake social proof or manufactured urgency.

**MSOS:** trust strip, degraded/partial data labels, live vs cached badges.

### 8. Sensory punctuation (restrained)

Subtle highlight or motion on **insight moments** — region selected, disagreement classified, gap found. Celebrate understanding, not P&amp;L.

**MSOS:** card emphasis, overlay transition; never confetti-on-trade.

### 9. Asymmetric feedback (anti-casino)

Strong reads get light emphasis. Empty, low-trust, or watch-only states stay **calm and explicit** — restraint is product behavior, not a broken screen.

**MSOS:** “no candidate,” thin market, stale data — explain why, show provenance.

### 10. Focal-action / thumb-zone design

Primary action sits where attention and motor effort naturally go. Mobile-aware even when desktop-first.

**MSOS:** preset chips adjacent to chart; primary CTA in stable strip, not buried in settings.

---

## Emotional arc (per session, any module)

1. **Orient** — “what is this tool showing me?”
2. **Touch** — one obvious move
3. **See** — hero object updates
4. **Understand** — plain-English what changed
5. **Explore** — voluntary second and third variations
6. **Restrain** — honest empty/degraded/watch-only when data or rules require it

---

## Module frame template

For each user-facing module at **T2+** (see module registry), document:

| Field | Question |
|-------|----------|
| **Module** | Registry id + route |
| **Primary question** | One sentence |
| **Hero object** | What owns the screen |
| **First action** | Default preset / control |
| **Feedback** | What updates on touch |
| **Plain-English read** | Headline strip or card |
| **Trust cue** | Freshness, source, limits |
| **Restraint state** | Empty / degraded / watch-only copy |
| **Return hook** | Why come back |

---

## Insight collect (living module frames)

**Insight collect** = keep this section updated when a user-facing module ships or materially changes. Each row is the module frame template filled from **current product truth** (routes in `apps/msos-web/`, display APIs in `src/viz/`). BUILD agents and UX review use this as the fast spec — not a Figma board.

**When to run insight collect:** module closeout (T2+), major UX slice merge, or after a guided trader session surfaces a framing gap.

### `options_horizon` — `/options-horizon`

| Field | Value |
|-------|-------|
| **Primary question** | How does BTC (or selected asset) structure look in **price × time**, and what does options imply inside a region I care about? |
| **Hero object** | Price × time chart (spot, volume, implied forward curve) |
| **First action** | Drag a **thesis region** on the chart (or switch expiry on forward curve) |
| **Feedback** | Region box + implied-mass preview string; optional distribution side panel |
| **Plain-English read** | “Implied mass in region: X%” (+ method label) |
| **Trust cue** | Payload `as_of_utc`, live vs loading state, thin-chain handling |
| **Restraint state** | Preview fails → calm “could not compute” (not a crash) |
| **Return hook** | Deep link to Strategy Lab with region context; expiry / surface moves daily |

**Game/casino steal:** map is the slot reel — drag region = pull lever; preview line = slip payout text.

### `implied_distribution` — `/strategy-lab`

| Field | Value |
|-------|-------|
| **Primary question** | What outcome distribution do options **price** at this expiry, and how does **my view** compare? |
| **Hero object** | Distribution chart + **“What this means”** outcome headline |
| **First action** | Belief preset chip or nudge (bullish / bearish / vol up) — not blank sliders |
| **Feedback** | Overlay curve + outcome headline + disagreement read updates in place |
| **Plain-English read** | `outcome.headline` under “What this means” |
| **Trust cue** | `trust_state` banners (thin chain, degraded); live vs fixture mode |
| **Restraint state** | Market tuning = no false “edge found”; watch-only when trust insufficient |
| **Return hook** | Asset picker parity, CSV download, workflow steps (confirm → expression) |

**Game/casino steal:** belief chips = odds taps; headline strip = bet slip hero anchored while chart moves.

### `exposure_menu` — `/exposure`

| Field | Value |
|-------|-------|
| **Primary question** | What **paths exist** to get exposure to this asset (spot, options, planned rails) under my direction and horizon? |
| **Hero object** | Ranked **path cards** stack (not a single chart) |
| **First action** | Tap direction chip (long / short / neutral) or horizon chip (3m / 12m) |
| **Feedback** | Path list refreshes; spot line + status note update |
| **Plain-English read** | Each card `headline` + `capital_shape` |
| **Trust cue** | Per-path `trust_badge`; page-level live vs sample paths note |
| **Restraint state** | `insufficient_chain` → thin chain note; fixture fallback labeled honest |
| **Return hook** | Card `deep_link` into Strategy Lab / expression when wired |

**Game/casino steal:** intake chips = sportsbook market filter; path cards = parlay legs you can inspect one-by-one.

### `expression_planner` — `/strategy-lab/expression`

| Field | Value |
|-------|-------|
| **Primary question** | What **structure fits** my view under constraints (simulation only)? |
| **Hero object** | Suggested expression summary + payoff preview |
| **First action** | Arrive from lab workflow or open with thesis context |
| **Feedback** | Structure / legs update when inputs change |
| **Plain-English read** | Fit language — not “buy this” |
| **Trust cue** | Simulation-only footer; link back to lab trust state |
| **Restraint state** | No expression promoted when materiality low |
| **Return hook** | Save to monitor / paper track |

### Command Center — `/` (authenticated home)

| Field | Value |
|-------|-------|
| **Primary question** | What should I **open next** in my trading process? |
| **Hero object** | Calibration / reviews-due strip + module entry cards |
| **First action** | Tap a module card (Horizon, Strategy Lab, Exposure) |
| **Feedback** | Card highlights; counts update after monitor actions |
| **Plain-English read** | Short module one-liners on cards |
| **Trust cue** | Live / Soon / Planned labels honest |
| **Restraint state** | Empty monitor = invitation, not error |
| **Return hook** | Reviews due, return visits without scheduled demo |

### Monitor + History — `/monitor`, `/history`

| Field | Value |
|-------|-------|
| **Primary question** | What did I save, and **was I right** after the horizon? |
| **Hero object** | Snapshot / paper-trade list → detail drill-down |
| **First action** | Open a snapshot with review due |
| **Feedback** | Post-mortem form → KPI strip updates |
| **Plain-English read** | Review status + class summary copy |
| **Trust cue** | Frozen evaluation provenance on detail |
| **Restraint state** | “Review not due yet” calm state |
| **Return hook** | Learning spine — track record over time |

### Planned / partial (fill on ship)

| Module | Route | Note |
|--------|-------|------|
| `forward_consistency` | `/forward-consistency` (planned) | Radar flags = variable insight moments |
| `cross_venue_event_gap` | Strategy Lab card / artifacts | Gap found = highlight; thin history = restraint |
| Public homepage | `/` | Product window = zero-login first action; CTA into app |

---

## Reference apps (pattern library)

Use as **interaction inspiration**, not visual clone targets.

### DraftKings / FanDuel (sportsbook slip)

| Their pattern | MSOS translation |
|---------------|------------------|
| Tap odds → instant slip update | Tap preset / region → instant summary + chart |
| Bet slip as persistent hero | Headline insight strip anchored while exploring |
| Payout recalc live | Payoff / structure preview updates in place |
| Cannot place bet (rules) | Watch-only / degraded — calm blocker copy |
| Bet history | Monitor / saved thesis / freeze ledger |

**Steal:** hero summary stays visible while browsing controls.  
**Refuse:** boost promos, parlay nudges, fake “people are betting this.”

### Robinhood (options chain + contract sheet)

| Their pattern | MSOS translation |
|---------------|------------------|
| Chain row highlight + bottom sheet | Strike/expiry/region selection → detail card |
| P/L chart follows selection | Main chart follows control surface |
| % chance / plain labels | Market-implied read in English |
| Greeks behind expand | Provenance / math behind expand |
| Risk / level gates | Trust strip + materiality gates |

**Steal:** one dimension changes → chart animates.  
**Refuse:** confetti, volume badges, certainty theater.

### Polymarket (event page)

| Their pattern | MSOS translation |
|---------------|------------------|
| Question + probability bar hero | Headline read + implied structure |
| Yes/No as primary primitive | Priced probability / region as primary UI unit |
| Resolution rules visible | Falsification / expiry / source rules in expander |
| Low liquidity warning | Thin market / partial data in trust strip |
| Related markets | Cross-module links (horizon ↔ lab ↔ consistency) |

**Steal:** probability and structure are **headline**, not footnotes.  
**Refuse:** comment hype, volume-as-pressure.

### Video games (general)

| Their pattern | MSOS translation |
|---------------|------------------|
| Tutorial through play | Loaded state + one obvious first move |
| HUD always visible | Trust strip + module title + hero metrics |
| Skill expression via controls | Presets for beginners, depth for experts |
| Save slots | Thesis / freeze / monitor |
| Empty state as design | “No gap found” with explanation, not error |

---

## Ethical boundary (refuse list)

Do **not** import from gambling or predatory fintech UX:

- Countdown urgency pushing action
- Fake live-user counts or social proof
- Loss-chasing or FOMO copy (“you’re missing edge”)
- Recommended trade / signal / guaranteed-profit language
- Visual confidence exceeding data confidence
- Hiding fees, edge, provenance, or degraded state
- Infinite feeds of noise “opportunities”
- Dark patterns on paywall, consent, or data retention

**Rule:** beauty must not create false certainty.

---

## Relationship to the longer journey

This philosophy supports **trader desirability now** without replacing the platform roadmap:

- Modules can ship **standalone value** (horizon chart, exposure menu, consistency radar) before full workflow integration.
- Strategy Lab / disagreement remains **one module**, not the identity of the whole product.
- Workflow hooks (T4) layer on when a module earns repeat use — don’t block T2 polish on full thesis loop.

When in doubt: **would a trader open this again tomorrow?** If yes, the module is doing its job.

---

## Acceptance bar (user-facing modules)

Observable in demo or witness:

1. User identifies **which tool** and **main object** quickly.
2. User completes **one meaningful action** in ~10 seconds (order-of-magnitude).
3. **Hero object** updates visibly; plain-English read reflects the action.
4. User **voluntarily tries** at least two more interactions in a short session.
5. **Trust / provenance** still findable when prompted.
6. **Restraint states** feel intentional, not broken.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-29 | v1 — MSOS platform scope, game/casino mechanics, module template, reference apps |
| 2026-06-30 | Insight collect — living module frames for live MSOS routes |
