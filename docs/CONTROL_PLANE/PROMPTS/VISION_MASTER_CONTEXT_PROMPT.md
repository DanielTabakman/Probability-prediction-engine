# VISION_MASTER_CONTEXT_PROMPT

**Reusable instruction block** — paste into a future GPT (or similar) context window when you want **only** `docs/VISION/VISION_MASTER.md` created or revised. Control plane artifact; not product vision.

---

## Prompt (copy below this line)

You are **not** executing sprints, managing workers, or implementing code.

Your **only** job is to **create or revise** `docs/VISION/VISION_MASTER.md` in this repository.

**Do this in order:**

1. Read **`docs/CONTROL_PLANE/PROMPTS/VISION_MASTER_AUTHORING_STANDARD.md`** first and follow it completely.  
2. Read grounded docs as needed, for example: current `docs/VISION/VISION_MASTER.md` (if present), `docs/SOP/ORIGINAL_SPEC.md`, `README.md`, `docs/PLAN.md`, `docs/SEMANTIC_CONTRACTS.md`, and `docs/SOP/VISION_IMPORT_POLICY.md`. Use `docs/VISION/PHASE_VISION_CURRENT.md` and `docs/SOP/CURRENT_FRONTIER.md` only to detect contradiction or stale master wording — **do not** turn the master into a phase doc.  
3. **Preserve enduring product intent.** Do not replace honest boundaries (priced vs belief, fit vs recommendation, exploration vs advice) with vaguer language unless the human explicitly asked for that change.  
4. **Do not** turn the master into a sprint plan, changelog, or implementation/architecture spec.  
5. Use the **exact required H2 section order** from the authoring standard (Product promise → … → **Notes**). Keep `# VISION_MASTER` as the title; optional one short intro paragraph under the title is allowed.  
6. Keep the document **concise and high-signal**.  
7. **Do not create extra files** unless the user explicitly asked for additional paths.  
8. **Do not** edit app/code, SOP loops, or other VISION files unless the user explicitly asked you to.

**When done, report:**

1. Whether `docs/VISION/VISION_MASTER.md` was **created** or **updated**.  
2. **What changed** at a high level (1–5 bullets).  
3. Any **ambiguity** or **drift risks** you noticed (e.g. conflict between stable docs, or content that belongs in phase vision instead).

---

## Prompt (copy above this line)
