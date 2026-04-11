# CURRENT_FRONTIER_CONTEXT_PROMPT

**Reusable instruction block** — paste into a future GPT (or similar) context window when you want **only** `docs/SOP/CURRENT_FRONTIER.md` created or revised. Control plane artifact; not the frontier itself.

---

## Prompt (copy below this line)

You are **not** executing feature slices, managing workers, or implementing code.

Your **only** job is to **create or revise** `docs/SOP/CURRENT_FRONTIER.md` in this repository.

**Do this in order:**

1. Read **`docs/CONTROL_PLANE/PROMPTS/CURRENT_FRONTIER_AUTHORING_STANDARD.md`** first and follow it completely.  
2. Read grounded docs as needed, prioritizing:  
   - `docs/SOP/CURRENT_FRONTIER.md` (current content; preserve reality unless superseded by evidence)  
   - `docs/VISION/PHASE_VISION_CURRENT.md` (phase intent, priorities, deferrals, drift risks)  
   - `docs/SOP/ORIGINAL_SPEC.md` (cycle anchor)  
   - `docs/SOP/HANDOFF.md` (what actually happened; verification evidence)  
   - `docs/SOP/MANAGER_LOOP.md` + `docs/SOP/WORKER_LOOP.md` + `docs/SOP/OPERATING_RULES.md` (execution posture, stop/escalate)  
   - `docs/SOP/SPRINT_TEMPLATE.md` (how to shape a feature slice spec)  
   Also consult `docs/SEMANTIC_CONTRACTS.md` and phase-relevant specs (e.g. `docs/SPRINT_1_SPEC.md`) if they constrain feature slice choices.  
3. Synthesize the **current phase** and a **tight shortlist** of “Next best feature slice candidates” that are **larger, testable** options with clear objectives and credible verification—avoid micro-patches and avoid blind big-bang rewrites.  
4. Keep the frontier **tight and action-driving**. Avoid generic filler. If you cannot justify a candidate with phase intent + credible verification, omit it.  
5. Use the **exact required H2 section order** from the authoring standard:  
   - `## Current phase`  
   - `## Top goal`  
   - `## Success condition for this phase`  
   - `## Current feature slice`  
   - `## Completed recently`  
   - `## Next best feature slice candidates`  
   - `## Avoid for now`  
   - `## Known risks / uncertainty`  
   - `## Stop / escalate conditions`  
   - `## Last updated`  
6. **Do not create extra files** unless the user explicitly asked for additional paths.  
7. **Do not** edit app/code files or unrelated SOP/VISION files unless the user explicitly asked you to.

**When done, report:**

1. Whether `docs/SOP/CURRENT_FRONTIER.md` was **created** or **updated**.  
2. **What changed** at a high level (1–5 bullets).  
3. Any **ambiguity** or **drift risks** you noticed (e.g. conflicts between phase product vision and frontier, missing evidence in handoff, candidates that felt under-verified).

---

## Prompt (copy above this line)
