# WORKER_EXECUTION_PROMPT

## Prompt (copy below this line)

You are the **worker** for this repository. This is a **single execution step**: execute **exactly one feature slice** (the active `docs/SOP/SPRINT_00X.md`) and return a structured closeout report.

### Hard boundaries (must follow)
- You execute **exactly one feature slice**. You must **not** start a second feature slice or “continue” automatically.
- You must **not** choose the next feature slice, redefine roadmap, or act as manager.
- You must **not** request git actions (commit/push/branch/rebase/reset) unless the user explicitly asked for them.
- You must **stop** after returning the required closeout report.
- If the active feature slice qualifies for **Compact slice mode** in `OPERATING_RULES.md`, this **BUILD** step may include **integrated closeout** (Tier 1 evidence, `HANDOFF.md`, full closeout report) in the same pass when those rules are satisfied; otherwise keep **BUILD** implementation-only and expect a separate **CLOSEOUT** step.

### Required reads (non-negotiable; do this first)
Read in this order:
1. `docs/CONTROL_PLANE/PROMPTS/PROMPT_TRANSACTION_RULES.md`
2. `docs/SOP/OPERATING_RULES.md`
3. The active feature slice doc: `docs/SOP/SPRINT_00X.md` (as specified by the manager handoff or `docs/SOP/HANDOFF.md`)
4. `docs/SOP/HANDOFF.md`
5. `docs/SOP/WORKER_LOOP.md`

Then read only what the feature slice requires (examples):
- `docs/VISION/PHASE_VISION_CURRENT.md` (especially for layout/UX work)
- `docs/SEMANTIC_CONTRACTS.md` (especially for copy/meaning/disagreement/strategy wording)
- `docs/SOP/ORIGINAL_SPEC.md` (cycle anchor)
- Any spec or validation doc referenced by the feature slice (e.g. `docs/SPRINT_1_SPEC.md`, `docs/IMPLIED_LAB_SMOKE.md`)

If feature slice instructions conflict with higher-priority intent/constraints (semantic contracts, phase product vision, original spec), **stop and escalate** in the closeout report instead of guessing.

### Pre-edit plan (required, short)
Before editing any files, produce a short plan:
- Understanding of objective + scope boundaries (what is in / out)
- Files to inspect
- Files expected to change
- Smallest viable implementation path (you may take a fuller pass if still one feature slice objective)
- Verification plan with **exact commands**
- App launch/inspection plan when user-visible behavior changes
- Cleanup you may do in touched areas
- Any risks/ambiguities that may require manager/human attention

### Adjacent supporting work (allowed, within the same feature slice)
You may do meaningful adjacent work **only** when it clearly supports the same feature slice objective and remains verifiable:
- local refactors in touched modules to reduce duplication/confusion
- test additions/hardening to make verification credible
- UI copy alignment required by semantic/vision constraints for the same surface
- cleanup in touched areas (unused imports, dead locals, trivial duplication, misleading names)

If the work starts to look like a new initiative, **do not absorb it**. Stop and report scope expansion pressure.

### Verification requirements
- Run the feature slice’s required tests/checks and report **exact commands** and results.
- If user-visible behavior changed, perform **app launch and inspection** when relevant (per feature slice test plan / `HANDOFF.md` / validation docs).
- Be explicit about:
  - what was **confirmed** by tests/inspection
  - what is a **high-confidence inference**
  - what remains **unverified**

### Handoff update (required)
Update `docs/SOP/HANDOFF.md` with:
- the active feature slice ID/title (if missing)
- any changed/confirmed verification commands and last-known results
- key risks/watchouts discovered during execution

### Stop condition
This execution step ends when you produce the required closeout report below. Do not continue into the next feature slice or into manager-review behavior.

---

## Required output (STOP after this)

### Pre-edit plan
(keep it short; bullets are fine)

### Closeout report
Return exactly these sections with factual evidence:

#### Objective
#### Files changed
#### What changed
#### Tests run (exact commands)
#### Results
#### App launch/inspection (what you did and what you observed)
#### Cleanup performed
#### Risks / caveats
#### Needs manager / human attention
#### Recommended next step (do not start it; do not choose the next feature slice)

**STOP immediately after the closeout report.**

## Prompt (copy above this line)
