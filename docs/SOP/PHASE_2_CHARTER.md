# Phase 2 Charter — Desirability / Playability / UX

## 1. Title

**Official canonical phase name:** **PHASE 2 = Desirability / Playability / UX** (same phrase as this document’s heading).

## 2. Status / supersession

- **Phase 1** (one-screen BTC implied lab) **remains complete.** Exit criteria and confirmation are unchanged: `docs/SOP/PHASE_1_EXIT_CRITERIA.md`, `docs/SPRINT_1_SPEC.md`, and historical CLOSEOUT evidence referenced from `docs/SOP/CURRENT_FRONTIER.md`.
- **This charter explicitly supersedes** the previously documented **immediate** next-planning framing in `docs/SOP/CURRENT_FRONTIER.md` and `docs/SOP/HANDOFF.md` that named **paid beta / commercial wrapper** as the **next boundary to charter and execute**. That candidate was honest for its time; it is **no longer** the default “what we do next” without an explicit re-charter.
- **Commercial wrapper** (access, packaging, billing/trials, distribution-appropriate onboarding) is **deferred to a later phase** (control-plane shorthand: **Phase 3–class** unless re-labeled). It is **not canceled**—it requires its **own** charter before execution.
- **Implied-lab expansion (Phase 1 scope)** is **not reopened** by this charter. Follow-on implied-lab work is **out of band** unless there is a **real regression**, a **trust-breaking issue**, a **deterministic blocker** for Phase 2, or an **explicitly approved** follow-on story.
- **Repo/docs are source of truth** over chat memory (anti-hallucination discipline for stewards and agents).
- **SELECTION** (charter, sprint spec, frontier updates) stays **separate** from **BUILD** and **CLOSEOUT** unless an operating rule explicitly combines them.

## 3. Mission

Transform the **one-screen BTC implied lab** from **technically respectable** into **inviting, intuitive, rewarding, and demo-worthy**—without trading away the trust spine.

Make the surface feel more like a **living instrument / strategy sandbox** than a **dense finance form**, while keeping the same semantic backbone users rely on when decisions matter.

## 4. Product promise

- **Belief vs market** comparison should feel **interactive and meaningful**, not like a static report.
- A **smart non-expert** should feel **curiosity** quickly—not confusion or intimidation.
- A **serious user** should still feel **depth and integrity** (auditability, honest limits, no bait-and-switch certainty).

## 5. UX target / emotional arc (behavioral, not decorative)

1. **Understand the main thing quickly** (what object is “the lab” right now).
2. **See one obvious thing to touch** (a control, preset, or affordance—not a wall of equal-weight fields).
3. **Get immediate visual feedback** on the main object when they act.
4. **Understand in plain English what changed** (interpretation tied to the action, not jargon soup).
5. **Want to try another variation** (rewarding loop, not one-off trick).

_Internal shorthand “UX seduction” is optional flavor only; the official phase name remains **Desirability / Playability / UX**._

## 6. What remains sacred (non-negotiables)

- **Provenance** and honest disclosure of inputs/limits.
- **Market-data honesty** (including degraded/partial/cache-bound states).
- **Degraded-state honesty** (no silent “everything is fine” when it is not).
- **Verification / traceability** paths that still answer “why should I believe this?”.
- **Semantic stability of the core loop** (what things *mean* does not drift casually).
- **Fit is not recommendation** and the **exploration vs recommendation** boundary.
- **Beauty must not create false certainty** (visual emphasis cannot smuggle in new claims).

## 7. Allowed changes (this phase MAY do)

- **Layout hierarchy** (what is primary vs supporting vs advanced).
- **Defaults / starter state** (including intentional example/preload posture).
- **Invitation / framing copy** (orientation without rewriting contracts in prose).
- **Visibility of controls** (progressive disclosure; fewer simultaneous demands).
- **Presets / affordances** that encode safe, semantically-valid starting points.
- **Visual emphasis / grouping** that clarifies comparisons and causality.
- **Layering of advanced information** (still available; not deleted by default).

## 8. Forbidden changes without an explicit re-charter (this phase MAY NOT silently do)

- **Semantic contract** changes (`docs/SEMANTIC_CONTRACTS.md` and related invariants).
- **Trust semantics** (what “verified”, “degraded”, “partial”, etc. mean operationally).
- **Recommendation boundary** shifts (exploration must not masquerade as advice).
- **Market scope** expansion beyond **BTC-first** positioning.
- **Commercial wrapper systems** (billing, accounts, paywalls, distribution packaging).
- **Broad AI / prediction-market expansion** or unrelated product surfaces.
- **Major architecture programs** or **major engine rewrites**—unless a **separately approved enabling slice** proves they are the **only** deterministic fix for an agreed blocker.

## 9. Success criteria (includes a behavioral witness)

Phase 2 succeeds when the lab is **more playable** *and* **as trustworthy** as Phase 1—measured both by inspection and by discipline.

**Desirability / playability bar (retained and tightened):**

- A **new user** can identify the **main object** quickly.
- They can make **one meaningful change** in roughly **~10 seconds** (order-of-magnitude; network/data caveats apply).
- They can **explain in plain English what changed** after that action.
- They **voluntarily try at least two more interactions** in a short session (guided demo counts if observed).
- They can still **locate trust/provenance** when prompted (it did not disappear into ornament).

## 10. Anti-architecture-creep clause

If Phase 2 work—or **Sprint 001** specifically—surfaces a **deterministic blocker** caused by **state/layout structure** (for example, unfixable contradictions in Streamlit session ownership that prevent the sprint loop), **stop** and propose a **separate bounded enabling slice** with its own acceptance criteria and evidence.

Do **not** silently expand “desirability” into **architecture hardening**, **state centralization programs**, or broad refactors. **State centralization** is **not** a hidden requirement of this charter; it may appear only as an **explicit enabling slice** if it becomes a **blocker**, not a default “while we are here” project.

## 11. Scope boundary

- **BTC-first** remains the product scope for this lab phase unless re-chartered.
- **Commercial wrapper** is explicitly **later** (Phase 3–class) unless re-chartered again.
- This phase is **not generic polish**: it is a **real product phase** aimed at **desirability, playability, and UX quality** under the constraints above.

## 12. Last updated

2026-04-13 — control-plane **SELECTION** pass: charter canonized (`docs/SOP/PHASE_2_CHARTER.md`); sprint spec `docs/SOP/SPRINT_001_PHASE_2.md`; `CURRENT_FRONTIER` / `HANDOFF` aligned. **No product BUILD** in this pass.

# Phase 2 Charter — Desirability / Playability / UX

## 1. Title

**Official canonical phase name:** **PHASE 2 = Desirability / Playability / UX** (same phrase as this document’s heading).

## 2. Status / supersession

- **Phase 1** (one-screen BTC implied lab) **remains complete.** Exit criteria and confirmation are unchanged: `docs/SOP/PHASE_1_EXIT_CRITERIA.md`, `docs/SPRINT_1_SPEC.md`, and historical CLOSEOUT evidence referenced from `docs/SOP/CURRENT_FRONTIER.md`.
- **This charter explicitly supersedes** the previously documented **immediate** next-planning framing in `docs/SOP/CURRENT_FRONTIER.md` and `docs/SOP/HANDOFF.md` that named **paid beta / commercial wrapper** as the **next boundary to charter and execute**. That candidate was honest for its time; it is **no longer** the default “what we do next” without an explicit re-charter.
- **Commercial wrapper** (access, packaging, billing/trials, distribution-appropriate onboarding) is **deferred to a later phase** (control-plane shorthand: **Phase 3–class** unless re-labeled). It is **not canceled**—it requires its **own** charter before execution.
- **Implied-lab expansion (Phase 1 scope)** is **not reopened** by this charter. Follow-on implied-lab work is **out of band** unless there is a **real regression**, a **trust-breaking issue**, a **deterministic blocker** for Phase 2, or an **explicitly approved** follow-on story.
- **Repo/docs are source of truth** over chat memory (anti-hallucination discipline for stewards and agents).
- **SELECTION** (charter, sprint spec, frontier updates) stays **separate** from **BUILD** and **CLOSEOUT** unless an operating rule explicitly combines them.

## 3. Mission

Transform the **one-screen BTC implied lab** from **technically respectable** into **inviting, intuitive, rewarding, and demo-worthy**—without trading away the trust spine.

Make the surface feel more like a **living instrument / strategy sandbox** than a **dense finance form**, while keeping the same semantic backbone users rely on when decisions matter.

## 4. Product promise

- **Belief vs market** comparison should feel **interactive and meaningful**, not like a static report.
- A **smart non-expert** should feel **curiosity** quickly—not confusion or intimidation.
- A **serious user** should still feel **depth and integrity** (auditability, honest limits, no bait-and-switch certainty).

## 5. UX target / emotional arc (behavioral, not decorative)

1. **Understand the main thing quickly** (what object is “the lab” right now).
2. **See one obvious thing to touch** (a control, preset, or affordance—not a wall of equal-weight fields).
3. **Get immediate visual feedback** on the main object when they act.
4. **Understand in plain English what changed** (interpretation tied to the action, not jargon soup).
5. **Want to try another variation** (rewarding loop, not one-off trick).

_Internal shorthand “UX seduction” is optional flavor only; the official phase name remains **Desirability / Playability / UX**._

## 6. What remains sacred (non-negotiables)

- **Provenance** and honest disclosure of inputs/limits.
- **Market-data honesty** (including degraded/partial/cache-bound states).
- **Degraded-state honesty** (no silent “everything is fine” when it is not).
- **Verification / traceability** paths that still answer “why should I believe this?”.
- **Semantic stability of the core loop** (what things *mean* does not drift casually).
- **Fit is not recommendation** and the **exploration vs recommendation** boundary.
- **Beauty must not create false certainty** (visual emphasis cannot smuggle in new claims).

## 7. Allowed changes (this phase MAY do)

- **Layout hierarchy** (what is primary vs supporting vs advanced).
- **Defaults / starter state** (including intentional example/preload posture).
- **Invitation / framing copy** (orientation without rewriting contracts in prose).
- **Visibility of controls** (progressive disclosure; fewer simultaneous demands).
- **Presets / affordances** that encode safe, semantically-valid starting points.
- **Visual emphasis / grouping** that clarifies comparisons and causality.
- **Layering of advanced information** (still available; not deleted by default).

## 8. Forbidden changes without an explicit re-charter (this phase MAY NOT silently do)

- **Semantic contract** changes (`docs/SEMANTIC_CONTRACTS.md` and related invariants).
- **Trust semantics** (what “verified”, “degraded”, “partial”, etc. mean operationally).
- **Recommendation boundary** shifts (exploration must not masquerade as advice).
- **Market scope** expansion beyond **BTC-first** positioning.
- **Commercial wrapper systems** (billing, accounts, paywalls, distribution packaging).
- **Broad AI / prediction-market expansion** or unrelated product surfaces.
- **Major architecture programs** or **major engine rewrites**—unless a **separately approved enabling slice** proves they are the **only** deterministic fix for an agreed blocker.

## 9. Success criteria (includes a behavioral witness)

Phase 2 succeeds when the lab is **more playable** *and* **as trustworthy** as Phase 1—measured both by inspection and by discipline.

**Desirability / playability bar (retained and tightened):**

- A **new user** can identify the **main object** quickly.
- They can make **one meaningful change** in roughly **~10 seconds** (order-of-magnitude; network/data caveats apply).
- They can **explain in plain English what changed** after that action.
- They **voluntarily try at least two more interactions** in a short session (guided demo counts if observed).
- They can still **locate trust/provenance** when prompted (it did not disappear into ornament).

## 10. Anti-architecture-creep clause

If Phase 2 work—or **Sprint 001** specifically—surfaces a **deterministic blocker** caused by **state/layout structure** (for example, unfixable contradictions in Streamlit session ownership that prevent the sprint loop), **stop** and propose a **separate bounded enabling slice** with its own acceptance criteria and evidence.

Do **not** silently expand “desirability” into **architecture hardening**, **state centralization programs**, or broad refactors. **State centralization** is **not** a hidden requirement of this charter; it may appear only as an **explicit enabling slice** if it becomes a **blocker**, not a default “while we are here” project.

## 11. Scope boundary

- **BTC-first** remains the product scope for this lab phase unless re-chartered.
- **Commercial wrapper** is explicitly **later** (Phase 3–class) unless re-chartered again.
- This phase is **not generic polish**: it is a **real product phase** aimed at **desirability, playability, and UX quality** under the constraints above.

## 12. Last updated

2026-04-13 — control-plane **SELECTION** pass: charter canonized (`docs/SOP/PHASE_2_CHARTER.md`); sprint spec `docs/SOP/SPRINT_001_PHASE_2.md`; `CURRENT_FRONTIER` / `HANDOFF` aligned. **No product BUILD** in this pass.
