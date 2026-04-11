# PHASE_VISION_AUTHORING_STANDARD

Stable **authoring standard** for future GPT (or similar) context windows that **create or revise** `docs/VISION/PHASE_VISION_CURRENT.md`. This file is **control plane** documentation, not product vision.

## Purpose

Govern **how** `PHASE_VISION_CURRENT.md` should be written and maintained so it stays **phase-specific**, **manager-useful**, and **high-signal**: clear outcomes, UX/semantic priorities, explicit deferrals, and drift risks—without turning into a feature slice spec.

## What PHASE_VISION_CURRENT is

`docs/VISION/PHASE_VISION_CURRENT.md` is:

- the **current phase’s** vision for this repository (cycle-scoped, not evergreen)  
- a **manager steering aid** for choosing and shaping feature slices (what matters most right now)  
- a place to capture **phase outcomes**, **UX priorities**, **semantic/labeling constraints**, and **drift risks**  
- concise enough to read in a minute or two

It should align with the active frontier (`docs/SOP/CURRENT_FRONTIER.md`) but remain **vision-level**: the “why/what must stay true in this phase,” not “how we implement it.”

## What PHASE_VISION_CURRENT is not

It is **not**:

- a feature slice plan, backlog, or acceptance checklist  
- a technical design or architecture doc (files/APIs/schemas/algorithms)  
- a changelog, diary, or status report  
- a substitute for `docs/SOP/ORIGINAL_SPEC.md` (cycle execution anchor)  
- a rewrite of `docs/VISION/VISION_MASTER.md` (enduring product vision)

If you find yourself listing many tasks, PR-sized steps, or file paths, you are drifting into SOP / feature slice territory.

## Source priority

When authoring or updating `PHASE_VISION_CURRENT.md`, use sources in this order:

1. **Existing** `docs/VISION/PHASE_VISION_CURRENT.md` — preserve phase intent unless superseded.  
2. **`docs/SOP/CURRENT_FRONTIER.md`** — current phase framing, top goal, success condition, and constraints that should be reflected at vision level.  
3. **`docs/SOP/ORIGINAL_SPEC.md`** — cycle target; extract **phase-relevant outcomes** (not acceptance checklists).  
4. **`docs/VISION/VISION_MASTER.md`** — ensure phase intent does not contradict durable product promises/anti-goals.  
5. **Semantic truth docs** — especially `docs/SEMANTIC_CONTRACTS.md` when the phase touches labeling, “fit vs recommendation,” belief vs priced distribution, disagreement wording, verification/traceability expectations.  
6. **Phase-adjacent specs** (e.g. `docs/SPRINT_1_SPEC.md`) — use to ground **what this phase means**, but do not paste implementation rules or convert into a feature slice checklist.

If unsure whether content belongs in vision vs SOP, consult `docs/SOP/VISION_IMPORT_POLICY.md` and keep the separation rule.

## Required output format

`docs/VISION/PHASE_VISION_CURRENT.md` must have **`# PHASE_VISION_CURRENT`** as the title and then the following **H2 sections in exactly this order**:

1. `## Current phase`  
2. `## What this phase is trying to achieve`  
3. `## Done enough for this phase`  
4. `## Current UX priorities`  
5. `## Current semantic priorities`  
6. `## Defer for now`  
7. `## Current drift risks`  
8. `## Notes`  

The content should be predominantly bullets or short paragraphs; `## Notes` is for brief clarifications (e.g. alignment pointers, boundaries, or known ambiguities), not for task lists.

## Writing rules

- **Phase-specific**: write for the current phase scope; do not restate the entire master product vision.  
- **Manager-friendly**: emphasize decision constraints (“what matters / what to defer / what to watch”), not step-by-step execution.  
- **Concise and high-signal**: every line should help shape feature slice objectives or protect semantics/UX.  
- **No implementation detail by default**: avoid file paths, module names, and refactor prescriptions; only mention an implementation constraint if needed to preserve product meaning (rare).  
- **Avoid generic filler**: no slogans; prefer concrete user-outcome statements (“a new user can answer X quickly”) and crisp semantic constraints.  
- **Preserve semantic honesty**: keep contract-sensitive distinctions intact (priced/implied vs belief, fit vs recommendation, disagreement descriptive).  
- **Defer explicitly**: name out-of-scope items so feature slices don’t accrete “nice-to-haves.”  

## Update rules

Update `PHASE_VISION_CURRENT.md` when:

- the **phase changes** (new focus, new success condition), or  
- the frontier or cycle docs imply a materially different **phase outcome**, or  
- drift risks/deferrals need refresh because recent work changed reality

Do **not** update it for every feature slice’s micro-detail. The doc should remain stable across multiple feature slices inside the same phase.

## Drift checks

Before treating the draft as done, ask:

- Did I accidentally write a **feature slice spec** (tasks, acceptance steps, file-level plans)?  
- Did I leak **implementation details** that belong in a feature slice spec or tech note?  
- Is the “Done enough” bar phrased as **user-visible comprehension/outcomes**, not internal completeness?  
- Are the **semantic priorities** consistent with `docs/SEMANTIC_CONTRACTS.md` (no “market truly believes,” no recommendation voice)?  
- Does this phase contradict `VISION_MASTER.md` (promise/anti-goals), or merely specialize it?  
- Is “Defer for now” truly defer (not quietly smuggled back via wording)?

## Output checklist

Before finishing, verify:

- [ ] `# PHASE_VISION_CURRENT` present; H2 sections appear in the **required order** (ending with `## Notes`).  
- [ ] Doc is **phase-specific** and **concise**; no backlog dump or implementation checklist.  
- [ ] “Done enough” defines a **clear bar** a manager can use to accept feature slice progress.  
- [ ] UX and semantic priorities are phrased as **constraints** and **clarity goals**, not tasks.  
- [ ] Deferrals and drift risks are explicit and aligned with current reality/frontier.  

