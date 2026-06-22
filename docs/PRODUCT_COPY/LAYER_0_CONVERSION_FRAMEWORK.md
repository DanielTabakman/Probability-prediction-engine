# Layer 0b — Conversion framework (MSOS copy)

**Load with Layer 0** when drafting or revising visitor copy. This doc translates general website copy doctrine into MSOS-specific rules. It does **not** replace compliance in [`MSOS_PUBLIC_COPY_V1.md`](../SOP/MSOS_PUBLIC_COPY_V1.md).

**Core insight (non-negotiable):** Good copy helps the visitor decide — *Is this for me? Do I understand the value? Do I trust it enough to take the next step?* — not “explain what the product is.”

---

## The spine formula

```text
Audience → Pain/Desire → Promise → Proof → Path
```

| Step | MSOS meaning | Layer 0 anchor |
|------|--------------|----------------|
| **Audience** | Options trader with a market view | Eyebrow / identity line |
| **Pain** | Thesis → tradable structure is messy; market may already price your view | Problem copy (often missing today) |
| **Promise** | See implied probabilities, find disagreement, explore fit | North star + hero h1 |
| **Proof** | Live BTC demo, paper-only honesty, built-for-traders | Pills, preview window, footer |
| **Path** | One obvious next click | Primary CTA |

---

## Visitor decision funnel (answer in order)

The visitor silently asks:

1. **Do I get it?** → Hero h1 + subhead (5-second test)
2. **Is this for me?** → Eyebrow + specificity (BTC options, market view)
3. **Do I care?** → Pain / before-after tension
4. **Do I believe you?** → Proof (demo tag, live lens, honest limits)
5. **What do I do next?** → Primary CTA (after 1–4, never before)

**Failure mode:** “Sign up now” before “sign up for what?” — same as pushing Command Center before the value is clear.

---

## Copy strength hierarchy (homepage should live at 3–5)

| Level | Weak (avoid as hero) | Strong (prefer) |
|-------|----------------------|-----------------|
| 1 — What it is | “A probability prediction engine” | — |
| 2 — What it does | “Shows implied distributions from options” | Subhead, product cards (lower fold) |
| 3 — What it helps me do | “Compare your thesis to the market” | Hero body, features |
| 4 — Why that matters | “See if your view is actually tradable” | Pain section, h1 candidates |
| 5 — Identity / aspiration | “For traders who reason belief → payoff” | Eyebrow, proof line |

**MSOS rule:** Deep philosophy (market structure, thesis lifecycle, interaction modes) belongs **below the fold** or on `/learn` — after “Oh, I need that.”

---

## Benefits before features

Every feature string gets a “so what?” pass:

| Feature (internal) | Benefit (visitor) |
|--------------------|-------------------|
| Implied distribution + chart | See what options are already pricing |
| Saved snapshots / history | Track what you believed vs what the market implied |
| BTC options lab | Stop guessing whether your thesis is tradable |
| Belief presets | State your view in one click — compare to the market |
| Expression planning | Choose a payoff shape that fits your view — paper only |

**Three-pass rewrite** (use for every major string):

1. **Literal** — what the product does (*Compare thesis to options-implied probabilities*)
2. **Customer value** — why it matters (*See if the market already agrees*)
3. **Decision / action** — what they can do (*Choose a structure that fits before you trade*)

Ship pass 2–3 on homepage; pass 1 only in docs or `/learn`.

---

## Above the fold (three questions)

| Question | MSOS answer location |
|----------|----------------------|
| Who is this for? | `hero.eyebrow` — “For traders with a market view” |
| What problem does it solve? | `hero.h1` + optional pain block |
| What happens if I click? | Primary CTA label + route |

**Sharp h1 candidates** (test against v1):

- *See where your market view disagrees with options pricing.* (GPT-aligned, disagreement-first)
- *Turn a BTC market thesis into a structure you can evaluate in under 15 seconds.* (north-star literal)
- v1 today: *Turn your market thesis into a trade you can reason about.* (softer — “reason about” vs “disagrees” / “tradable”)

---

## One page = one job

| Page | Single job | Primary path |
|------|------------|--------------|
| **Homepage** | Understand value → try demo | Strategy Lab (or research beta) |
| **Strategy Lab** | Experience thesis → market → payoff | Belief builder → chart |
| **Command Center** | Resume work | Open lab / review KPI |
| **Monitor** | Watch thesis health | (authenticated) |
| **Learn** | Trust founder / vision | Read → optional beta |

Bad copy explains everything on every page. Good copy **creates a path**.

---

## Homepage skeleton (ideal vs current)

| Section | Ideal job | Current site |
|---------|-----------|--------------|
| Hero | Promise + CTA | ✅ HeroSection |
| Problem | Name the pain (thesis → structure is hard) | ❌ **Gap** — no dedicated block |
| Solution | New workflow in one paragraph | ⚠️ Partial — hero body only |
| How it works | 3–4 steps | ✅ FeaturesRow (4 steps) |
| Proof | Credibility, demo, audience identity | ⚠️ Partial — pills + preview, no prose proof |
| CTA repeat | Try lab / research beta | ⚠️ Partial — hero CTAs only |

**Process note:** Problem + Proof blocks may need **BUILD** (new regions) — charter separately from copy packet. Copy agent drafts strings; BUILD adds sections if missing.

---

## Customer language vs founder language

**Use on homepage (customer):**

- What is the market pricing?
- Where do I disagree?
- Is there a trade here?
- What structure fits my view?

**Defer lower or to product cards (founder — use sparingly):**

- Probability Engine (required on product card per canon — not in h1)
- Thesis lifecycle, expression families, market structure OS as jargon
- Disagreement surface, cognition, belief expression

**Steal from users:** [`VALIDATION_REALITY_CHECKS.md`](../SOP/VALIDATION_REALITY_CHECKS.md) and operator session notes when available.

---

## Pre-publish checklist (every page)

| Test | Question |
|------|----------|
| **Clarity** | Stranger understands in 5 seconds? |
| **Specificity** | Who is it for + what action? |
| **Desire** | Real pain or decision moment? |
| **Proof** | Reason to believe (even early-stage)? |
| **Action** | Next step obvious? |
| **Language** | Would a customer say this? |
| **Compliance** | Non-advisory, honest live/demo (MSOS_PUBLIC_COPY_V1) |

Plus **“So what?”** on every sentence — if you cannot answer, cut or deepen.

---

## MSOS copy stack (approved variants)

Use as palette when drafting — operator picks per surface:

| Variant | Line |
|---------|------|
| **Plain** | Turn your market thesis into a tradable options structure. |
| **Sharp** | See where your market view disagrees with options pricing. |
| **Complete** | Compare your thesis to market-implied probabilities, then explore payoff structures that fit your view. |
| **Emotional** | Stop jumping from thesis to trade. First see what the market is pricing. |
| **Expert** | Move from belief → implied distribution → payoff expression in one workflow. |

**North star (15s):** See what BTC options imply, where you disagree, and what payoff fits.

**GPT-recommended pair for hero test:**

- h1: *See where your market view disagrees with options pricing.*
- sub: *Compare your thesis to market-implied probabilities, then explore payoff structures that fit your view.*

---

## Tension shape (before → after)

Use in Problem section or hero subhead:

| Before | After |
|--------|-------|
| You have a view; translating to a trade is messy | See implied distribution, compare belief, choose structure |
| “I’m bullish” | “This payoff fits my view — and the market disagrees here” |
| Spreadsheet rabbit hole | Fast read on what options price |

---

## Template (repeatable)

```text
For [options traders with a market view] who struggle with [turning a thesis into a structure],
[MSOS / Strategy Lab] helps you [compare your view to market-implied probabilities]
so you can [find tradable disagreement and explore fit]
without [hiding assumptions or getting a recommendation].
```

---

## Where this doc is used

| Agent action | Apply |
|--------------|-------|
| Discuss page strategy | Funnel + one-page-one-job |
| Draft packet | Three-pass + copy stack + skeleton gaps |
| Review v1 homepage | Sharp h1 candidates + missing Problem/Proof |
| Promote to content | Pre-publish checklist + validator |

**History:** Layer 0b added 2026-06-22 — synthesizes external copy doctrine with MSOS canon.
