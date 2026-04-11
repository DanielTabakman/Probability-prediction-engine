# SPRINT_AUTHORING_STANDARD

Stable **authoring standard** for future GPT (or similar) context windows that **create or revise** `docs/SOP/SPRINT_00X.md`. This file is **control plane** documentation, not a feature slice spec itself.

## Purpose

Govern how feature slice specs (`SPRINT_00X.md`) are authored so each feature slice is **meaningful**, **bounded**, and **testable**—a manager/worker contract that advances the current phase without becoming a vague wishlist, a tiny “caution slice,” or an implementation diary.

## What a feature slice spec is

A feature slice spec (`docs/SOP/SPRINT_00X.md`) is:

- a **one-feature-slice execution contract**: objective, boundaries, acceptance, verification, and escalation triggers
- a **worker-facing constraint set**: what must stay true (preserve behavior, semantic constraints, avoid list)
- a **test plan** with exact commands and required inspection when behavior is user-visible
- a **definition of done** and a required closeout report structure

It should let a worker take a fuller, coherent pass **inside** one feature slice objective without guessing what “done” means.

## What a feature slice spec is not

It is **not**:

- a backlog dump or “everything we might do”
- a vague wishlist (“improve UI”, “refactor code”) without testable outcomes
- a multi-feature-slice roadmap or phase rewrite
- an implementation diary (step-by-step narration of edits)
- an architecture treatise (unless the feature slice explicitly requires a small, bounded design constraint)
- a place to silently change product meaning or semantics

If the spec can’t be verified, or could justify almost anything, it is failing.

## Source priority

When authoring or revising a feature slice spec, use sources in this order:

1. **Existing** `docs/SOP/SPRINT_00X.md` (if revising) — preserve intent unless superseded by evidence
2. `docs/SOP/CURRENT_FRONTIER.md` — current phase framing and candidate feature slice shapes
3. `docs/VISION/PHASE_VISION_CURRENT.md` — phase outcomes, UX/semantic priorities, deferrals, drift risks
4. `docs/SOP/ORIGINAL_SPEC.md` — cycle anchor (ensure the feature slice converges to cycle intent)
5. `docs/SOP/HANDOFF.md` — reality: last verification, commands, known fragility
6. Execution constraints — `docs/SOP/OPERATING_RULES.md`, `docs/SOP/MANAGER_LOOP.md`, `docs/SOP/WORKER_LOOP.md`
7. Phase constraints — `docs/SEMANTIC_CONTRACTS.md` and any phase spec referenced by frontier / feature slice (e.g. `docs/SPRINT_1_SPEC.md`)
8. Validation docs referenced by the feature slice (e.g. `docs/IMPLIED_LAB_SMOKE.md`) to make verification credible

If sources conflict, prefer **authoritative intent + verified reality** over speculative plans.

## Required output format

Feature slice specs must follow `docs/SOP/SPRINT_TEMPLATE.md` exactly: keep the same H2 section titles and order. Do not invent new required sections.

Minimum required structure (copied from the template; keep headings as-is):

- `## Sprint ID`
- `## Title`
- `## Objective`
- `## Scope in`
- `## Scope out`
- `## Files likely to change`
- `## Current behavior to preserve`
- `## Desired behavior`
- `## Acceptance criteria`
- `## Test plan`
- `## Cleanup expectations`
- `## Escalation triggers`
- `## Definition of done`
- `## Pre-edit plan template`
- `## Closeout report template`

You may add short bullets within sections, but do not add a new top-level format.

## Writing rules

- **Meaningful, not tiny**: a feature slice should move the phase materially forward, not just “do the smallest safe change.” Bigger is fine if acceptance and verification are credible.
- **Still bounded**: one coherent objective; adjacent work allowed only when it supports that objective.
- **Testable**: every acceptance criterion must map to verification (tests, smoke, app launch/inspection when relevant).
- **Phase-convergent**: align to current phase product vision + frontier; avoid new product scope.
- **Semantics-safe**: if copy/meaning is involved, explicitly bind to `docs/SEMANTIC_CONTRACTS.md` (and include constraints in the spec).
- **No implementation diary**: do not prescribe step-by-step file edits; specify outcomes and constraints.
- **Be explicit about non-regressions**: list “current behavior to preserve” that is known important.
- **Prefer exact commands**: test plan must be runnable as written (no “run tests”).

## Update rules (revising an existing feature slice spec)

Update a feature slice spec only when:

- evidence shows the objective/scope/test plan is wrong or incomplete, or
- new constraints were discovered that must be made explicit, or
- manager explicitly re-scoped the feature slice

When updating:
- keep the original objective intact unless explicitly re-scoped
- record changes as edits to the relevant sections; do not add a changelog section
- re-check that acceptance criteria and test plan still line up

## Drift checks

Before finalizing a feature slice spec, ask:

- Is the objective **one coherent thing** or a bundle of unrelated tasks?
- Are scope boundaries crisp (what is out, including tempting adjacent initiatives)?
- Could a worker verify “done” without guessing? Are commands exact?
- Did I accidentally add phase/roadmap changes that belong in `CURRENT_FRONTIER.md` or product vision?
- Does the feature slice respect semantic contracts (no recommendation theater, no priced-vs-belief collapse)?
- Does it encourage a **full pass inside one feature slice** (allowed) without enabling silent scope creep (forbidden)?

## Output checklist

Before finishing, verify:

- [ ] Feature slice spec follows `docs/SOP/SPRINT_TEMPLATE.md` section order and headings exactly.
- [ ] Objective is meaningful and phase-convergent; not a tiny caution slice.
- [ ] Scope in/out are explicit and bounded.
- [ ] Acceptance criteria are testable and map to the test plan.
- [ ] Test plan lists exact commands and includes app launch/inspection when user-visible behavior changes.
- [ ] Cleanup expectations allow safe, local improvement without cross-cutting sprawl.
- [ ] Escalation triggers are explicit (what must be surfaced instead of guessed).
- [ ] Closeout report template remains intact and requires evidence.
