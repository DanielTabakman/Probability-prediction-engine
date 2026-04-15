# Sprint 001 — Phase 2 — First desirability / playability pass

**What this file is:** the **Sprint 001 spec / baseline** (scope + acceptance) for Phase 2.

**Execution status (ledger lives elsewhere):** this spec **does not assert** whether Sprint 001 has been executed, nor which slices are closed. Treat **execution status**, **closed slices**, and the **next pending execution step** as living in:
- `docs/SOP/CURRENT_FRONTIER.md` (authoritative ledger)
- `docs/SOP/HANDOFF.md` (minimal session-to-session summary; may temporarily drift)

**Parent charter:** `docs/SOP/PHASE_2_CHARTER.md`  
**Phase 1 completeness:** unchanged — `docs/SOP/PHASE_1_EXIT_CRITERIA.md`

---

## 1. Sprint mission

Deliver the **first rewarding interaction loop** on the one-screen BTC implied lab: from a **credible loaded state** to an **obvious move**, to a **visible change in the main object**, to a **plain-English readout of meaning**—without weakening trust, semantics, or the exploration-vs-recommendation boundary.

## 2. Primary target loop (non-negotiable for “done”)

**Loaded state → obvious move → visible change in main object → plain-English meaning**

If BUILD work cannot satisfy this loop without touching forbidden areas, **stop and escalate** per Section 7.

## 3. In scope (narrow)

Prioritize the **smallest coherent slice** that makes the loop real:

- **Preloaded starter / example state** (defaults that show the lab “already alive,” not an empty form).
- **One clear focal object** (the user always knows what the “main thing” is on first glance).
- A **small set** of **high-value visible controls and/or presets** (fewer simultaneous decisions; obvious first moves).
- A **plain-English “what changed?”** readout tied to the last meaningful interaction (not a dump of all state).
- **Surface de-cluttering / hierarchy** changes **only as needed** to support the loop (primary vs advanced).
- **Cheap, safe de-emphasis** of advanced information that currently competes with the loop (collapse, move down, reduce visual weight—**without hiding trust/provenance**).

## 4. Explicitly de-prioritized / mostly deferred

- **Major strategy-family area redesign** (large taxonomy/navigation rework).
- **Broad aesthetic refinement** (design-system overhaul, “make it pretty” without causal UX wins).
- **Motion systems** except **tiny, directly causal** motion (if any) that clarifies feedback—default is **none**.
- **Broader secondary-panel redesign** beyond what the primary loop requires.
- **Architecture cleanup** as a goal in itself.
- **State centralization** unless **separately escalated** as a **deterministic blocker** with a bounded enabling-slice proposal.

## 5. Acceptance criteria (observable, user-facing)

After BUILD + agreed validation:

1. **On first glance**, a user sees: **main object**, a short **invitation sentence**, a **few obvious controls/presets**, and a **populated** (non-empty-feeling) state.
2. **First action** can be taken **quickly** (single obvious path; no treasure hunt).
3. **First action** causes a **visible change** in the **main object** (not only marginal chrome).
4. **Plain-English interpretation** updates to reflect what changed (honest, contract-aligned wording).
5. **No regression** in trust/provenance posture vs Phase 1 bar (Verification path, degraded honesty, legibility payloads—whatever the repo currently treats as canonical; evidence in CLOSEOUT).
6. The product **feels more like an instrument / sandbox** and **less like a dense dashboard**—while remaining **BTC-first** and **semantically anchored**.

## 6. Constraints

- Preserve the **trust spine** (provenance, degraded-state honesty, verification discipline).
- Preserve **semantics** and documented contracts—**copy/layout only** unless a contract change is explicitly approved elsewhere.
- Preserve **fit-is-not-recommendation** and the **exploration vs recommendation** boundary.
- **Smallest coherent slice** rule: if it does not serve the primary loop, it waits.
- Do not scope-creep into **generic beauty work** or open-ended polish.

## 7. Stop / escalate

- If a **deterministic structural blocker** appears (e.g., session/widget structure makes the loop impossible), **stop** and propose a **separate enabling slice** with explicit scope, risk, and validation—**do not** silently broaden Sprint 001 into architecture or broad refactors.
- If work drifts toward **state centralization**, **engine rewrites**, or **monetization**, **reset to charter** and re-run **SELECTION**.

## 8. Evidence expectations (future BUILD CLOSEOUT)

CLOSEOUT for this sprint should be concise and evidence-backed:

- **Files changed** (paths; note if docs-only vs product).
- **User-facing changes** (bullet list tied to acceptance criteria).
- **Intentionally not changed** (deferrals; out-of-scope items untouched).
- **Before/after visuals** if available (screenshots or smoke artifacts—optional but valuable).
- **Regression / smoke evidence** (pytest; primary implied-lab smoke; any extra scenarios the sprint spec required).
- **Tradeoffs / rough edges** (honest list: what a follow-on sprint might pick up).

---

## Last updated

2026-04-13 — **SELECTION** pass: sprint spec narrowed and canonized. **No BUILD** executed in this pass.

# Sprint 001 — Phase 2 — First desirability / playability pass

**What this file is:** the **Sprint 001 spec / baseline** (scope + acceptance) for Phase 2.

**Execution status (ledger lives elsewhere):** this spec **does not assert** whether Sprint 001 has been executed, nor which slices are closed. Treat **execution status**, **closed slices**, and the **next pending execution step** as living in:
- `docs/SOP/CURRENT_FRONTIER.md` (authoritative ledger)
- `docs/SOP/HANDOFF.md` (minimal session-to-session summary; may temporarily drift)

**Parent charter:** `docs/SOP/PHASE_2_CHARTER.md`  
**Phase 1 completeness:** unchanged — `docs/SOP/PHASE_1_EXIT_CRITERIA.md`

---

## 1. Sprint mission

Deliver the **first rewarding interaction loop** on the one-screen BTC implied lab: from a **credible loaded state** to an **obvious move**, to a **visible change in the main object**, to a **plain-English readout of meaning**—without weakening trust, semantics, or the exploration-vs-recommendation boundary.

## 2. Primary target loop (non-negotiable for “done”)

**Loaded state → obvious move → visible change in main object → plain-English meaning**

If BUILD work cannot satisfy this loop without touching forbidden areas, **stop and escalate** per Section 7.

## 3. In scope (narrow)

Prioritize the **smallest coherent slice** that makes the loop real:

- **Preloaded starter / example state** (defaults that show the lab “already alive,” not an empty form).
- **One clear focal object** (the user always knows what the “main thing” is on first glance).
- A **small set** of **high-value visible controls and/or presets** (fewer simultaneous decisions; obvious first moves).
- A **plain-English “what changed?”** readout tied to the last meaningful interaction (not a dump of all state).
- **Surface de-cluttering / hierarchy** changes **only as needed** to support the loop (primary vs advanced).
- **Cheap, safe de-emphasis** of advanced information that currently competes with the loop (collapse, move down, reduce visual weight—**without hiding trust/provenance**).

## 4. Explicitly de-prioritized / mostly deferred

- **Major strategy-family area redesign** (large taxonomy/navigation rework).
- **Broad aesthetic refinement** (design-system overhaul, “make it pretty” without causal UX wins).
- **Motion systems** except **tiny, directly causal** motion (if any) that clarifies feedback—default is **none**.
- **Broader secondary-panel redesign** beyond what the primary loop requires.
- **Architecture cleanup** as a goal in itself.
- **State centralization** unless **separately escalated** as a **deterministic blocker** with a bounded enabling-slice proposal.

## 5. Acceptance criteria (observable, user-facing)

After BUILD + agreed validation:

1. **On first glance**, a user sees: **main object**, a short **invitation sentence**, a **few obvious controls/presets**, and a **populated** (non-empty-feeling) state.
2. **First action** can be taken **quickly** (single obvious path; no treasure hunt).
3. **First action** causes a **visible change** in the **main object** (not only marginal chrome).
4. **Plain-English interpretation** updates to reflect what changed (honest, contract-aligned wording).
5. **No regression** in trust/provenance posture vs Phase 1 bar (Verification path, degraded honesty, legibility payloads—whatever the repo currently treats as canonical; evidence in CLOSEOUT).
6. The product **feels more like an instrument / sandbox** and **less like a dense dashboard**—while remaining **BTC-first** and **semantically anchored**.

## 6. Constraints

- Preserve the **trust spine** (provenance, degraded-state honesty, verification discipline).
- Preserve **semantics** and documented contracts—**copy/layout only** unless a contract change is explicitly approved elsewhere.
- Preserve **fit-is-not-recommendation** and the **exploration vs recommendation** boundary.
- **Smallest coherent slice** rule: if it does not serve the primary loop, it waits.
- Do not scope-creep into **generic beauty work** or open-ended polish.

## 7. Stop / escalate

- If a **deterministic structural blocker** appears (e.g., session/widget structure makes the loop impossible), **stop** and propose a **separate enabling slice** with explicit scope, risk, and validation—**do not** silently broaden Sprint 001 into architecture or broad refactors.
- If work drifts toward **state centralization**, **engine rewrites**, or **monetization**, **reset to charter** and re-run **SELECTION**.

## 8. Evidence expectations (future BUILD CLOSEOUT)

CLOSEOUT for this sprint should be concise and evidence-backed:

- **Files changed** (paths; note if docs-only vs product).
- **User-facing changes** (bullet list tied to acceptance criteria).
- **Intentionally not changed** (deferrals; out-of-scope items untouched).
- **Before/after visuals** if available (screenshots or smoke artifacts—optional but valuable).
- **Regression / smoke evidence** (pytest; primary implied-lab smoke; any extra scenarios the sprint spec required).
- **Tradeoffs / rough edges** (honest list: what a follow-on sprint might pick up).

---

## Last updated

2026-04-13 — **SELECTION** pass: sprint spec narrowed and canonized. **No BUILD** executed in this pass.
