# VISION_MASTER_AUTHORING_STANDARD

Stable **authoring standard** for future GPT (or similar) context windows that **create or revise** `docs/VISION/VISION_MASTER.md`. This file is **control plane** documentation, not product vision.

## Purpose

This standard governs **how** those windows should write or update `VISION_MASTER.md`: scope, sources, section shape, tone, when to edit, and how to self-check. Follow it so the master product vision stays **durable**, **concise**, and **not a feature slice spec**.

## What VISION_MASTER is

`docs/VISION/VISION_MASTER.md` is:

- a **stable long-horizon** product vision document  
- a source of **enduring product intent** (north star for meaning and quality)  
- **concise and high-signal**  
- **mostly independent** of current feature slice details and current phase execution  

Phase-specific intent belongs in `docs/VISION/PHASE_VISION_CURRENT.md` (and cycle execution in `docs/SOP/ORIGINAL_SPEC.md`), not in the master.

## What VISION_MASTER is not

It is **not**:

- a feature slice plan or backlog  
- an implementation spec (files, APIs, schemas, algorithms)  
- a changelog or release notes  
- a technical architecture document  
- a brainstorm dump or unconstrained ideation log  
- a phase-specific execution document  

## Source priority

When authoring or updating `VISION_MASTER.md`, use sources in this order:

1. **Existing** `docs/VISION/VISION_MASTER.md` — preserve enduring intent unless superseded.  
2. **`docs/SOP/ORIGINAL_SPEC.md`** — cycle-stable product target; extract only what is **long-lived**, not feature-slice-only scope.  
3. **Stable product/spec docs** — e.g. `README.md`, `docs/PLAN.md`, `docs/SPRINT_1_SPEC.md` only insofar as they state **product direction**, not acceptance checklists.  
4. **`docs/VISION/PHASE_VISION_CURRENT.md`** — use **only** to detect **drift or contradiction** between master and phase; do **not** paste phase details into the master.  
5. **Semantic / contracts docs** — e.g. `docs/SEMANTIC_CONTRACTS.md` — when they encode **enduring truths** (definitions, boundaries, honesty rules) that belong in the master’s “must-not-break” and “anti-goals” spirit.  

Also read `docs/SOP/VISION_IMPORT_POLICY.md` if unclear whether content belongs in vision vs SOP.

## Required output format

The file `docs/VISION/VISION_MASTER.md` must use **`# VISION_MASTER`** as the top-level title. You may add **at most one short introductory paragraph** immediately under the title (optional), then these **H2 sections in exactly this order**:

1. `## Product promise`  
2. `## Core user experience`  
3. `## Must-have qualities`  
4. `## Must-not-break truths`  
5. `## Anti-goals`  
6. `## Design / interpretation principles`  
7. `## What success should feel like`  
8. `## Notes`  

Use `## Notes` for boundaries (e.g. relationship to phase vision, ORIGINAL_SPEC, or where roadmap detail lives)—**not** for feature slice tasks.

## Writing rules

- **Keep it concise** — prefer tight bullets and short paragraphs.  
- **Synthesize** — integrate sources; avoid duplicating long passages from README or contracts.  
- **Preserve enduring truths** — do not weaken honesty, semantic boundaries, or user-trust framing for expediency.  
- **Do not overfit** to the current feature slice or single screen.  
- **No implementation detail** unless one sentence is needed to **preserve product meaning** (default: omit).  
- **Do not invent a new product** — only reflect what the repo’s docs support or a clearly stated human directive.  
- **Avoid generic fluff and slogans** — every line should be testable against “would this still matter in two phases?”  
- **Use bullets** when clearer than prose.  
- **Keep stable sections stable** — restructure only when **product meaning** really changed, not for editorial preference.

## Update rules

Revise `VISION_MASTER.md` **only when**:

- the **enduring product direction** changed (human decision or authoritative doc update), or  
- the current master is **clearly stale or contradictory** vs stable repo docs, or  
- **multiple stable docs** now imply a **better synthesis** for long-range product intent.  

Do **not** revise the master **just because a phase changed**. Phase changes update `PHASE_VISION_CURRENT.md` and `CURRENT_FRONTIER.md`, not the master, unless the phase change reflects a **real** long-horizon shift.

## Drift checks

Before treating the draft as done, ask:

- Does this still match the **enduring product goal** (compare README / PLAN / ORIGINAL_SPEC at intent level)?  
- Did **phase-specific** details (layout, first-screen widgets, one screen) **leak** into the master?  
- Did **implementation** or **tooling** crowd out **product intent**?  
- Are **anti-goals** still **explicit** (no recommendation theater, no semantic smuggling)?  
- Is the doc still useful as a **high-level north star** in under a few minutes’ read?

## Output checklist

Before finishing, verify:

- [ ] `# VISION_MASTER` present; H2 sections appear in the **required order** (including `## Notes`).  
- [ ] No feature slice IDs, acceptance checklists, or file-level implementation plans in the master.  
- [ ] Wording aligns with **semantic contracts** where relevant; no new forbidden claims.  
- [ ] Length remains **lean**; no boilerplate or filler.  
- [ ] Relationship to phase/cycle docs is clear in `## Notes` if ambiguity existed.  
