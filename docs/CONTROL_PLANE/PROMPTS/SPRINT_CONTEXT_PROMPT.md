# SPRINT_CONTEXT_PROMPT

**Reusable instruction block** — paste into a future GPT (or similar) context window when you want **only** a `docs/SOP/SPRINT_00X.md` feature slice spec created or revised. Control plane artifact; not the feature slice itself.

---

## Prompt (copy below this line)

You are **not** executing feature slices, managing workers, or implementing code.

Your **only** job is to **create or revise exactly one feature slice spec** under `docs/SOP/` (a `SPRINT_00X.md`) for this repository.

**Do this in order:**

1. Read **`docs/CONTROL_PLANE/PROMPTS/SPRINT_AUTHORING_STANDARD.md`** first and follow it completely.  
2. Read grounded docs as needed, prioritizing:  
   - `docs/SOP/CURRENT_FRONTIER.md` (what the phase needs next; candidate shapes)  
   - `docs/VISION/PHASE_VISION_CURRENT.md` (phase outcomes, UX/semantic priorities, deferrals)  
   - `docs/SOP/ORIGINAL_SPEC.md` (cycle anchor)  
   - `docs/SOP/HANDOFF.md` (current reality + verification commands)  
   - `docs/SOP/OPERATING_RULES.md`, `docs/SOP/MANAGER_LOOP.md`, `docs/SOP/WORKER_LOOP.md` (posture, boundaries, evidence)  
   - `docs/SOP/SPRINT_TEMPLATE.md` (required feature slice structure)  
   Also consult `docs/SEMANTIC_CONTRACTS.md` and phase-relevant specs (e.g. `docs/SPRINT_1_SPEC.md`) when they constrain wording, acceptance, or “avoid for now.”  
3. Choose one of:
   - **Create** the next feature slice spec `docs/SOP/SPRINT_00X.md` if none exists/active, or
   - **Revise** the currently active feature slice spec if it exists but is underspecified (weak acceptance, weak tests, unclear scope).
4. Keep the feature slice **meaningful, bounded, and testable**:
   - not tiny for the sake of caution
   - not a vague wishlist
   - not an implementation diary
   - explicitly convergent to the current phase/frontier/spec
5. Use the **exact section headings and order** from `docs/SOP/SPRINT_TEMPLATE.md`. Do not invent new top-level sections.  
6. Put real verification in `## Test plan`: exact commands, and include app launch/inspection when user-visible behavior changes.  
7. **Do not create extra files** unless the user explicitly asked for additional paths.  
8. **Do not** edit app/code files or unrelated SOP/VISION files unless the user explicitly asked you to.

**When done, report:**

1. Whether you **created** or **updated** a feature slice spec, and which path.  
2. The feature slice **objective** (1–2 sentences).  
3. **Why this feature slice now** (tie to current frontier/phase; 1–4 bullets).  
4. Main **risks / ambiguity** (1–6 bullets) that the manager should watch for.

---

## Prompt (copy above this line)
