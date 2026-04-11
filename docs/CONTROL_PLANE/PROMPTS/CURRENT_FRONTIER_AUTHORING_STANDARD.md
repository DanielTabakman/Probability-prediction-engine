# CURRENT_FRONTIER_AUTHORING_STANDARD

Stable **authoring standard** for future GPT (or similar) context windows that **create or revise** `docs/SOP/CURRENT_FRONTIER.md`. This file is **control plane** documentation, not the frontier itself.

## Purpose

Govern **how** `CURRENT_FRONTIER.md` should be written and maintained so it stays a **live, manager-friendly steering doc**: a tight statement of the current phase, what “success” means, what feature slice is active, and a small set of strong next feature slice candidates—without becoming a backlog dump or diary.

## What CURRENT_FRONTIER is

`docs/SOP/CURRENT_FRONTIER.md` is:

- the **current reality** steering doc for this repo’s phase execution  
- a place to keep the **phase framing** aligned with `docs/VISION/PHASE_VISION_CURRENT.md` and `docs/SOP/ORIGINAL_SPEC.md`  
- a decision aid listing **a few larger, testable feature slice options** that materially advance the phase  
- explicit about **avoid-for-now**, **risks/uncertainty**, and **stop/escalate** conditions

It should help a manager choose the next feature slice and define it crisply (often via `docs/SOP/SPRINT_TEMPLATE.md`), while keeping enough context to prevent drift.

## What CURRENT_FRONTIER is not

It is **not**:

- a backlog dump (hundreds of bullets)  
- a daily journal or meeting notes  
- a replacement for a formal feature slice file (`docs/SOP/SPRINT_00X.md`)  
- a place for implementation walkthroughs or architecture designs  
- an idealized roadmap divorced from what the repo is actually ready to validate

If the doc reads like “everything we could ever do,” it is failing.

## Source priority

When authoring or updating `CURRENT_FRONTIER.md`, use sources in this order:

1. **Existing** `docs/SOP/CURRENT_FRONTIER.md` — preserve reality unless new evidence changed it.  
2. **`docs/VISION/PHASE_VISION_CURRENT.md`** — phase intent, priorities, deferrals, drift risks.  
3. **`docs/SOP/ORIGINAL_SPEC.md`** — cycle anchor; ensure frontier candidates converge to the cycle target.  
4. **`docs/SOP/HANDOFF.md`** — what was actually done, what verification exists, and what is currently fragile.  
5. **SOP execution rules** — `docs/SOP/MANAGER_LOOP.md`, `docs/SOP/WORKER_LOOP.md`, `docs/SOP/OPERATING_RULES.md`, and `docs/SOP/SPRINT_TEMPLATE.md` (to keep feature slice shaping and stop/escalate rules consistent).  
6. **Specs/contracts relevant to the phase** — e.g. `docs/SPRINT_1_SPEC.md`, `docs/SEMANTIC_CONTRACTS.md`, and test/smoke docs when they affect feature slice credibility.

If there is conflict between sources, prefer **reality + authoritative intent** (HANDOFF evidence + phase product vision + original spec) over wishful plans.

## Required output format

`docs/SOP/CURRENT_FRONTIER.md` must have **`# CURRENT_FRONTIER`** as the title and then the following **H2 sections in exactly this order**:

1. `## Current phase`  
2. `## Top goal`  
3. `## Success condition for this phase`  
4. `## Current feature slice`  
5. `## Completed recently`  
6. `## Next best feature slice candidates`  
7. `## Avoid for now`  
8. `## Known risks / uncertainty`  
9. `## Stop / escalate conditions`  
10. `## Last updated`  

Keep each section short; “Next best feature slice candidates” should usually be **2–5 items**, not 20.

## Writing rules

- **Tight and action-driving**: the doc should make “what next?” obvious.  
- **Manager-friendly**: write in terms of objectives, acceptance, and verification credibility.  
- **Support larger, testable feature slices**: prefer a few meaningful options over micro-patches, as long as acceptance/verification is credible.  
- **Reflect current reality**: “Current feature slice,” “Completed recently,” and risks must match what actually happened.  
- **Avoid generic filler**: no vague “improve performance” or “refactor code” without a testable objective.  
- **Constrain scope**: each feature slice candidate should have a single coherent objective and clear boundaries (what it includes/excludes).  
- **Keep semantics honest**: if the phase is semantics-sensitive, ensure candidates respect `docs/SEMANTIC_CONTRACTS.md` and avoid “recommendation theater” drift.

## Update rules

Update `CURRENT_FRONTIER.md`:

- after each meaningful feature slice outcome (completed, halted, or re-scoped), or  
- when the phase or success condition changes, or  
- when reality changes (new risks, broken verification, new constraints) that should affect feature slice choice

Do **not** update it to record every tiny activity; that belongs in `HANDOFF.md` or a feature slice closeout.

## Drift checks

Before treating the draft as done, ask:

- Did “Next best feature slice candidates” become a **backlog** instead of a shortlist?  
- Do candidates describe **testable outcomes** with credible verification, or just “work”?  
- Is “Current feature slice” accurate, and does “Completed recently” match evidence (HANDOFF/tests/smoke)?  
- Did I introduce **new product scope** not supported by phase product vision or original spec?  
- Are “Avoid for now” and stop/escalate conditions strong enough to prevent runaway refactors?

## Output checklist

Before finishing, verify:

- [ ] `# CURRENT_FRONTIER` present; H2 sections appear in the **required order** (ending with `## Last updated`).  
- [ ] Phase + top goal + success condition are aligned with `PHASE_VISION_CURRENT.md` and `ORIGINAL_SPEC.md`.  
- [ ] “Next best feature slice candidates” is a **short list** of **larger, testable** options (not micro-patches; not a backlog).  
- [ ] “Avoid for now” and stop/escalate conditions prevent scope creep and uncontrolled refactors.  
- [ ] “Last updated” reflects the actual update date and author/source if available.
