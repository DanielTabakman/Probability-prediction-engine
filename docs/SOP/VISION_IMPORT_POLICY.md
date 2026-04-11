# VISION_IMPORT_POLICY

How **product vision** (intent) relates to **SOP** (process) and how managers/workers should load it.

## Rule of separation

| Layer | Lives in | Purpose |
|--------|-----------|--------|
| **Process** | `docs/SOP/` | How work runs: loops, handoff, feature slices, operating rules, git posture. |
| **Product vision** | `docs/VISION/` | What the product should **mean** and **feel like** for users over time and within a phase. |

SOP tells you **how** to execute; product vision tells you **why** and **what must stay true**. Do not merge them into one mega-doc.

## What product vision docs are

- **`docs/VISION/VISION_MASTER.md`** — long-range promise, UX qualities, anti-goals, principles. Stable; rarely churns sentence-by-sentence.  
- **`docs/VISION/PHASE_VISION_CURRENT.md`** — current phase outcomes, UX/semantic priorities, deferrals, drift risks. Updates when the phase changes.  
- **`docs/VISION/VISION_TEMPLATE.md`** — pattern for future phase/initiative vision files.  
- **Optional assets** — screenshots/mockups under `docs/VISION/assets/` with text notes (see below).

**`docs/SOP/ORIGINAL_SPEC.md`** remains the **cycle execution anchor** (what this build cycle is building toward). Product vision docs **inform** it; they do not replace feature slice acceptance or `CURRENT_FRONTIER.md` for day-to-day steering.

## Manager: when to read/import full vision

**Import or read `VISION_MASTER.md` when:**

- Onboarding as manager for the repo or after a long gap.  
- Choosing between **strategic** directions (phase change, large scope fork, new major surface).  
- Resolving **arguments about product meaning** (e.g. recommendation vs fit, belief vs priced distribution).  
- Drafting or rewriting **`ORIGINAL_SPEC.md`** or a **new phase** in `PHASE_VISION_CURRENT.md`.

**Import or read `PHASE_VISION_CURRENT.md` when:**

- Every **new feature slice** creation or approval (at least skim).  
- Updating **`CURRENT_FRONTIER.md`** or **acceptance** for the current phase.  
- **Stop/escalate** decisions where the question is “are we still building the same phase?”

The manager may **skim** `VISION_MASTER.md` on routine feature slice turnover if the phase is unchanged and risk is low; for **semantic-heavy** or **UX-layout** feature slices, read **both** master + phase.

## Worker: feature slice extract vs full vision

**Default — worker gets only a feature slice–level extract**

- Paste a short **`## Product vision constraints`** block inside the active `docs/SOP/SPRINT_00X.md` (see below). Older specs may still use `## Vision constraints`.  
- That is enough when the feature slice is **localized** (bugfix, copy tweak, single component) and the manager has already aligned scope to the phase.

**Worker should read full product vision docs when:**

- The feature slice **changes** primary layout, **navigation**, or **default user story** for the phase.  
- The feature slice touches **semantic contracts** broadly (new concepts, renaming, strategy/disagreement/belief flows).  
- The manager **explicitly instructs** full read of `VISION_MASTER.md` and/or `PHASE_VISION_CURRENT.md`.  
- The worker hits **ambiguity** that the feature slice extract does not resolve — then **stop and escalate** rather than invent.

## Screenshots and mockups

- **Store** under `docs/VISION/assets/` with descriptive filenames (e.g. `2026-04-01_implied-lab-two-column.png`).  
- **Pair** each asset with a short **text note** in the vision doc (or feature slice **Product vision constraints**): what the image **is**, what is **in scope**, what is **out of scope**, and **date**.  
- Do not rely on images alone; agents need **searchable text** for constraints.  
- No secrets, credentials, or PII in assets.

## Recommended feature slice section: `## Product vision constraints`

Add to each `SPRINT_00X.md` (after copying `SPRINT_TEMPLATE.md`). **Keep to a handful of bullets** the worker actually needs:

```markdown
## Product vision constraints
- `<e.g. Phase: one-screen implied lab — chart high, two columns, summary visible.>`
- `<e.g. Semantic: market-implied = priced/risk-neutral; no "market truly believes".>`
- `<e.g. Strategy copy: families to explore / fit — not "recommended trade".>`
- `<e.g. Deferred this feature slice: Polymarket wiring, new AI, framework migration.>`
```

The **manager** owns filling this section when creating the feature slice. The worker **must** treat it as binding for the feature slice alongside acceptance criteria.

## Quick reference

| Role | Routine feature slice | Semantic/layout feature slice | Phase change |
|------|------------------------|-------------------------------|--------------|
| Manager | Phase vision + ORIGINAL_SPEC + FRONTIER | + VISION_MASTER | VISION_MASTER + new PHASE_VISION + ORIGINAL_SPEC |
| Worker | Feature slice spec + Product vision constraints | + PHASE_VISION_CURRENT (+ MASTER if instructed) | As instructed; escalate if unclear |
