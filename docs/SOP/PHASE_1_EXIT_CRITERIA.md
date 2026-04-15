# Phase 1 exit criteria — one-screen BTC implied lab

## 1. Purpose

This document is the **canonical checklist** for deciding whether the **current phase** (one-screen BTC implied lab, manual exploration) is **complete**, or whether **exactly one** additional **bounded feature slice** is still justified.

**Boundary:** this phase and this product surface only (`docs/SPRINT_1_SPEC.md`, `docs/SEMANTIC_CONTRACTS.md`). It is **not** a launch plan for paid beta, billing, or a commercial wrapper.

**Not covered here:** pricing, packaging, onboarding funnels, compliance, or go-to-market for a paid product. Those belong to a **later planning boundary** (see section 6).

---

## 2. Current phase definition (operational)

**Phase 1** means:

- **One-screen BTC implied lab** — Streamlit workbench (`src/viz/app.py` and related viz modules): market-implied view, belief inputs, disagreement interpretation, strategy-family exploration, payoff and summary, verification path.
- **Trustworthy, legible, demoable manual loop** — a steward or operator can run the app locally, adjust controls, and walk a viewer through the story without hiding degraded data or lying about provenance.
- **Bounded by Sprint 1 and semantic contracts** — layout, orientation, copy, and behavior stay within `docs/SPRINT_1_SPEC.md` outcomes and `docs/SEMANTIC_CONTRACTS.md` (e.g. fit vs recommendation, risk-neutral wording, illustrative vs exact structure).
- **Not a recommendation engine** — no “you should trade this” layer; exploration and verification only.
- **Not the commercial wrapper phase** — no requirement for paid access, self-serve signup, or productized packaging to finish this phase.

`docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md` is the operational companion for validation, smoke, and closeout **during** this phase.

---

## 3. Exit criteria (what must be true)

Treat these as **operational**, not aesthetic perfection. A steward confirms each item using the demo script in section 5 where helpful.

| Area | Must be true |
|------|----------------|
| **User-facing legibility** | A new viewer can in ~**15 seconds** (per Sprint 1) orient to: market-implied view, belief mode, trade/strategy shape, and payoff/summary — with advanced detail available in expanders, not blocking the first scan. |
| **Trust / provenance / degraded-state honesty** | When live data is missing, partial, or cache-bound, the UI **does not** present stale inputs as fully current exchange truth without qualification. Trust/provenance surfaces (e.g. trust strip, market-data status, verification payload fields such as `market_data_legibility` where implemented) support **honest** reading of the run. |
| **Core loop coherence** | The narrative chain is coherent end-to-end: implied distribution → user belief → disagreement → strategy families as **fit** (not recommendation) → decision-ready / glance / ticket linkage as built → verification. Wording matches semantic contracts. |
| **Bounded validation expectations** | **Tier 1** closeout posture is defined and used (`docs/SOP/OPERATING_RULES.md`): unit tests green for the tree; primary smoke **A** used for implied-lab regressions; **smoke C** only when classification/scenario/derivation/harness semantics change. Failures are classified (deterministic vs environment- vs live-data-sensitive) without relabeling operational noise as automatic product failure. |
| **Demo-readiness** | The app runs locally per HANDOFF/runbook; a short manual demo (section 5) can be executed without known **deterministic** broken behavior in the core path. |

---

## 4. Explicit non-requirements for phase exit

Ending **Phase 1** does **not** require:

- **Paid access, billing, entitlements, or commercial wrapper**
- **Self-serve onboarding** beyond what this manual lab phase needs (e.g. full signup, multi-tenant product shell)
- **Major architecture refactor** or engine/DB redesign
- **State centralization pass** — Sprint 1 states a **directional** technical principle (single visible-output source of truth). **Phase exit does not depend on** completing a dedicated Streamlit/session **state centralization** refactor; that remains optional hardening (see section 6 and `docs/SOP/CURRENT_FRONTIER.md` candidate list).
- **Framework migration** (e.g. off Streamlit)
- **Expanded market scope** beyond BTC-first implied lab as scoped in current docs
- **AI / recommendation expansion** — advisory or autonomous suggestion layers are out of scope for this phase by definition

---

## 5. Demo acceptance script (manual, few minutes)

**Audience:** steward or operator demonstrating **Phase 1** success to a technical reviewer.

**Prep:** follow preflight notes in `docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md` (clean instance, fresh port if automating; live data may affect some panels — classify honestly).

1. **Launch** — Start the implied lab (`python -m streamlit run src/viz/app.py` per `docs/SOP/HANDOFF.md`). Confirm the page loads.
2. **15-second story** — Without deep scrolling, point to: **market-implied** anchor, **belief** controls/view, **mode** (exact strikes vs target payoff), **summary / payoff stats**, and where **advanced math** lives (expanders).
3. **Trust surface** — Show **Trust / provenance** (or equivalent) and, if the run is degraded/partial, **Market data status (this run)** (or equivalent) so the viewer sees **honest** sourcing — not a false “everything is live” impression.
4. **Fit, not recommendation** — Open **Belief vs market — at a glance** (or equivalent) and confirm language matches **fit / exploration**, not “recommended trade,” per `docs/SEMANTIC_CONTRACTS.md`.
5. **Verification** — Expand **Verification** and show that major outputs are traceable (inputs, assumptions, payload fields as implemented).
6. **Optional interaction** — Change one safe control (e.g. belief band or mode) and show payoff/summary update coherently.

**Evidence that matters most:** coherent story, contract-aligned copy, degraded-state honesty, and verification visibility — not pixel-perfect layout or optional polish items.

---

## 6. Deferred work boundary (planning only, not a roadmap promise)

**Likely next phase (product/business boundary):** **Paid beta / commercial wrapper** — packaging, access control, billing or trials, support posture, and onboarding appropriate to a paid or semi-public offering. **Out of scope** for Phase 1 exit.

**Likely later engineering boundary:** **Architecture hardening** — including an explicit **state centralization** pass if widget/session complexity becomes the main blocker for safe changes; broader refactors; non-urgent harness improvements. Treat these as **separate initiatives** chosen deliberately, not as implicit Phase 1 finish lines.

Phrasing here is a **boundary** for planning and steward selection, not a commitment to sequence or dates.

---

## 7. Decision rule

- If the current product **meets section 3** (verified with section 5 where needed), **Phase 1 may be declared complete** by steward/product agreement. Update `docs/SOP/CURRENT_FRONTIER.md` and `docs/SOP/HANDOFF.md` to reflect **phase closure** and the honest **next planning step** (e.g. SELECTION for a new phase charter, not an endless string of “011-like” polish slices).
- If **any section 3 item fails** in a **deterministic**, contract-breaking, or trust-breaking way, **do not** declare the phase complete. Choose **at most one** next **bounded feature slice**, close it with normal validation, then **re-run this checklist**.

**Anti-drift:** do not redefine “done” mid-review. If work expands into paid beta or architecture programs, **stop** and re-charter explicitly.

---

## 8. Known tolerances (do not auto-block exit)

The following **alone** do **not** automatically block Phase 1 exit if section 3 remains satisfied and the core loop is **trustworthy and demoable** (conservative list, grounded in accepted docs and closeout history):

- **Smoke A PNG viewport** — Scenario **A** `full_page=False` captures may omit lower right-column regions; DOM checks may still pass. Supplement with scroll or ad-hoc capture when pixel proof matters (`docs/IMPLIED_LAB_SMOKE.md`, HANDOFF).
- **Smoke C flaps** when **live data or scenario classification** disagrees with harness gates, while **pytest** and **smoke A** are green with good preflight — classify as **live-data/scenario-sensitive**, not automatic regression (e.g. historical feature slice 005 closeout).
- **External data outages** — Deribit/Yahoo unavailable leading to gated messaging (e.g. spot required for distribution); operational classification when not reproduced with data available.
- **One-off smoke timeouts** or environment friction — after preflight and bounded retries per `OPERATING_RULES.md`; not a default excuse for ignoring **deterministic** test failure.
- **Optional layout polish** listed as “if still needed” on the frontier — absence of an extra polish slice is **not** an automatic fail if Sprint 1 orientation and section 3 are met.
- **Ideal “centralized state” vs current implementation** — technical debt here is **real** but **not** a Phase 1 exit gate per section 4.

When in doubt, run section 5 and record **UNKNOWN** rather than overstating pass/fail.

---

## Related documents

| Document | Role |
|----------|------|
| `docs/SPRINT_1_SPEC.md` | Phase product outcomes |
| `docs/SEMANTIC_CONTRACTS.md` | Wording and meaning constraints |
| `docs/SOP/CURRENT_FRONTIER.md` | Active slice, candidates, risks |
| `docs/SOP/HANDOFF.md` | Session entry, commands, next step |
| `docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md` | Validation and closeout procedure |
| `docs/SOP/OPERATING_RULES.md` | Execution steps, validation tiers |
| `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` | Steward workflow and closeout modes |

---

## Last updated

2026-04-11 — Feature slice **011** (Phase 1 exit criteria and demo acceptance); docs-only.
