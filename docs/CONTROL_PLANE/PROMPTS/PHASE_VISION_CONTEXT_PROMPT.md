# PHASE_VISION_CONTEXT_PROMPT

**Reusable instruction block** — paste into a future GPT (or similar) context window when you want **only** `docs/VISION/PHASE_VISION_CURRENT.md` created or revised. Control plane artifact; not product vision.

---

## Prompt (copy below this line)

You are **not** executing feature slices, managing workers, or implementing code.

Your **only** job is to **create or revise** `docs/VISION/PHASE_VISION_CURRENT.md` in this repository.

**Do this in order:**

1. Read **`docs/CONTROL_PLANE/PROMPTS/PHASE_VISION_AUTHORING_STANDARD.md`** first and follow it completely.  
2. Read grounded docs as needed, prioritizing:  
   - `docs/VISION/PHASE_VISION_CURRENT.md` (current content, preserve intent unless superseded)  
   - `docs/SOP/CURRENT_FRONTIER.md` (current phase, top goal, success conditions, avoid/stop)  
   - `docs/SOP/ORIGINAL_SPEC.md` (cycle anchor; extract phase-relevant outcomes)  
   - `docs/VISION/VISION_MASTER.md` (ensure phase intent does not contradict durable vision/anti-goals)  
   - `docs/SEMANTIC_CONTRACTS.md` (semantic honesty constraints)  
   - `docs/SOP/VISION_IMPORT_POLICY.md` (vision vs SOP separation)  
   Use `docs/SPRINT_1_SPEC.md` (or similar) only to ground what the phase means—**do not** convert it into an implementation checklist.  
3. **Preserve phase intent** while avoiding implementation leakage. Do not include file paths, refactor plans, or step-by-step task lists unless the user explicitly asked.  
4. Use the **exact required H2 section order** from the authoring standard:  
   - `## Current phase`  
   - `## What this phase is trying to achieve`  
   - `## Done enough for this phase`  
   - `## Current UX priorities`  
   - `## Current semantic priorities`  
   - `## Defer for now`  
   - `## Current drift risks`  
   - `## Notes`  
5. Keep it **concise and high-signal**. Prefer bullets and short paragraphs. Avoid generic filler.  
6. **Do not create extra files** unless the user explicitly asked for additional paths.  
7. **Do not** edit app/code, SOP loops, or other VISION files unless the user explicitly asked you to.

**When done, report:**

1. Whether `docs/VISION/PHASE_VISION_CURRENT.md` was **created** or **updated**.  
2. **What changed** at a high level (1–5 bullets).  
3. Any **ambiguity** or **drift risks** you noticed (e.g. conflicts between stable docs, phase vs master tension, or areas where the doc was at risk of becoming a feature slice plan).

---

## Prompt (copy above this line)

