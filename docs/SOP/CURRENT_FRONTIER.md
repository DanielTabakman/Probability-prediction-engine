# CURRENT_FRONTIER

Purpose: live steering document for the current phase. Updateable; should reflect current reality.

**Feature slice sizing:** the frontier should support **a few larger, testable next–feature-slice options**—not only tiny patches—while still avoiding blind big-bang rewrites.

## Current phase
**Phase 1 (one-screen BTC implied lab) — COMPLETE** (2026-04-11, phase-exit confirmation CLOSEOUT).  
*(Spec anchor: `docs/SPRINT_1_SPEC.md`. Numbered increments are **feature slices**—e.g. feature slice 006—formerly referred to as “Sprint NNN”.)*

**Active phase (chartered):** **Phase 2 — Desirability / Playability / UX** — `docs/SOP/PHASE_2_CHARTER.md`.  
**Active sprint (spec exists):** **Sprint 001 — Phase 2** — `docs/SOP/SPRINT_001_PHASE_2.md`.  

**Steering continuity (doc-state, canonical):**
- **Phase 2 is active.**
- **Sprint 001 is active.**
- **Slices 001–004 are closed** (canonical ledger posture for Sprint 001 unless explicitly superseded by newer accepted docs).
- **Slice 005 (SELECTED, conceptual):** **Sprint 001 — Slice 005 — Starter state + one obvious first move (presets)**.

**Repo-state gate (operational, separate from steering):**

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` @ `9f5175f`
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **BUILD may proceed** from the clean baseline **without using parked branches** (use a fresh BUILD branch/worktree; obey preflight + single-plane rules). The parked deferred state remains **explicitly unaccepted** and does not gate baseline-based BUILD.

This does **not** erase or downgrade the steering state above; it only blocks execution.

**Honest supersession note:** `CURRENT_FRONTIER` / `HANDOFF` previously named **paid beta / commercial wrapper** as the **immediate** next planning boundary (also reflected in `docs/SOP/PHASE_1_EXIT_CRITERIA.md` as a **Phase 1 closeout snapshot** — e.g. “likely next phase” toward commercial wrapper). That snapshot is **not deleted**; for **operative planning after 2026-04-13**, this file plus `docs/SOP/PHASE_2_CHARTER.md` **supersede** it for **what executes next**. **Paid beta / commercial wrapper** remains a **valid later product boundary**, now treated as **Phase 3–class** (monetization / distribution / commercial wrapper layer) — **deferred, not canceled** — and still requires its **own** charter before BUILD.

**Optional engineering (unchanged posture):** bounded **state centralization** / runbook-only hardening remains **deferred** per `PHASE_1_EXIT_CRITERIA.md` section 6 and **Next best feature slice candidates** below, **unless** a future phase or incident—or a **deterministic Phase 2 blocker**—justifies a **separate enabling slice** (see Phase 2 charter anti–architecture-creep clause).

## Top goal (achieved for Phase 1)
The repo shipped a **coherent one-screen implied lab** matching `docs/SPRINT_1_SPEC.md`: fast comprehension, two-column layout, chart high on the page, clear mode/belief switches, summary stats; Sprint 1 **directional** state principle acknowledged without a state-centralization gate for exit (`docs/SOP/PHASE_1_EXIT_CRITERIA.md` section 4).

## Success condition for this phase (met)
A new user can in ~**15 seconds** answer: what the **market-implied** view shows, what **belief** they are expressing, what **trade/strategy shape** they are inspecting, and **payoff stats**—with advanced math tucked away and semantics consistent with `docs/SEMANTIC_CONTRACTS.md`. Trust/provenance and degraded market-data honesty are covered (feature slice **010** and verification payload fields such as `market_data_legibility`).

**Formal phase-exit rubric:** `docs/SOP/PHASE_1_EXIT_CRITERIA.md` (feature slice **011**). **Phase-exit confirmation** (same doc, section 5 + section 3 assessment): `python -m pytest -q` → **41** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260411_163249/ui_smoke_manifest.json` (page load, disagreement, strategy family block, trade ticket, **Verification** expander found).

## Current feature slice
**Sprint 001 — Slice 005 (SELECTED, conceptual):** **Starter state + one obvious first move (presets)**.  
**Next move:** **BUILD (allowed)** from the clean baseline (use a fresh BUILD branch/worktree; do not use parked branches).

**Ledger hygiene note (important):** The “Completed recently” list below contains **historical notes** that may include **local / unaccepted** product/harness/test deltas. **Do not treat those as canonized closures** unless they are backed by an accepted repo-state (commit/push) and reconciled against the repo-state gate. The canonical steering ledger for Phase 2/Sprint 001 is stated above under **Steering continuity (doc-state, canonical)**.

## Completed recently
- **Feature slice 011 (docs-only): Phase 1 exit criteria and demo acceptance** — `docs/SOP/PHASE_1_EXIT_CRITERIA.md`; control-plane alignment. **Closeout evidence:** documentation review only (no product code changes claimed in this slice closeout record).
- **Feature slice 009 (closed): Implied lab operator runbook** — `docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md`; HANDOFF/CURRENT_FRONTIER cross-links; `docs/IMPLIED_LAB_SMOKE.md`, `docs/Frontier_Steward_Handoff.md`. **Closeout:** docs-only; pytest/smoke not required for that slice.
- **Feature slice 008 (local / unaccepted notes): Glance-first orientation polish** — historical implementation notes only; **do not treat as accepted closure** unless repo-state is reconciled and committed.
- **Feature slice 007 (local / unaccepted notes): Trade ticket path + linkage copy** — historical implementation notes only; **do not treat as accepted closure** unless repo-state is reconciled and committed.
- **Feature slice 006 (local / unaccepted notes): Trust / provenance strip** — historical implementation notes only; **do not treat as accepted closure** unless repo-state is reconciled and committed.
- **Feature slice 005 (local / unaccepted notes): Decision-ready trade review** — historical implementation notes only; **do not treat as accepted closure** unless repo-state is reconciled and committed.
- **Feature slice 004 (closed): Scannable main-disagreement digest** — `build_disagreement_scan_payload()` → `digest_lines`, `fit_bridge_intro`, `fit_bridge_bullets` on `belief_vs_market_glance`; glance UI shows digest/bridge first, audit trail collapsed; tests extended. **Closeout validation:** `python -m pytest -q` **PASS** (21 tests); `python scripts/run_implied_lab_ui_smoke.py` **PASS**; `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>` **PASS** (see manifests `artifacts/ui_smoke/20260410_145441/`, `artifacts/ui_smoke/20260410_150352/`).
- **Feature slice 003: Belief uncertainty capture** — added an intuitive **±% move (1σ)** uncertainty input mode (with explicit σ_ln mapping and market-horizon comparison) while preserving the existing internal lognormal belief overlay model; added focused unit tests.
- Unit test harness in `tests/` (e.g. belief/disagreement hints).
- Implied lab support modules: derive, provenance, disagreement hints/thresholds; ongoing `src/viz/app.py` evolution.
- Primary automated UI smoke: `scripts/run_implied_lab_ui_smoke.py` + docs in `docs/IMPLIED_LAB_SMOKE.md`.
- Handoff updated: app launch, headless readiness, and local inspection path documented.
- **Feature slice 002: market-first top-of-screen layout closure** — implied-lab market view is now the opening anchor; price/prediction context demoted to a collapsed “Market context … reference only” block.

## Next best feature slice candidates
**Phase 2 execution** is governed by **`docs/SOP/PHASE_2_CHARTER.md`** and **`docs/SOP/SPRINT_001_PHASE_2.md`**—do not use this list to bypass sprint scope or smuggle architecture work.

Use the **Phase 1–oriented** list below **only** when `docs/SOP/PHASE_1_EXIT_CRITERIA.md` shows a **remaining gap** or a **regression**; otherwise prefer **Phase 2** sprint work (post-SELECTION) over picking Phase 1 polish for its own sake.

1. **Further one-screen lab polish (bounded, optional)** — Feature slice 008 closed **glance-first orientation** (captions, grouping, chart-adjacent context). Remaining tweaks (e.g. summary density, spacing) only if still needed after review—no semantics expansion.
2. **Operational hardening (optional)** — If headless smoke runs ever hang with stale local Python/Streamlit processes, document “clear stuck processes before re-run”; keep scope to runbook only unless a reproducible harness bug appears.
3. **Lab state centralization pass** — **Not** a Phase 1 exit requirement (`PHASE_1_EXIT_CRITERIA.md`). **Not** a default Phase 2 requirement. Only if state complexity is a **deterministic blocker** for an agreed UX slice; keep it constrained to viz/session ownership and use smoke+tests to prevent regressions—prefer a **separate enabling slice** over silent expansion.

## Avoid for now
- New AI features, Polymarket/prediction-market integration spikes, framework migration (`docs/SPRINT_1_SPEC.md`).
- Cross-cutting engine/DB refactors unless a feature slice explicitly targets them and acceptance tests exist.

## Known risks / uncertainty
- **External data** (Deribit/Yahoo) can fail or rate-limit; automated smoke may be environment-dependent. In particular, if spot/quotes are unavailable the app can show **"Need BTC spot price for implied distribution"** and UI smoke will flap (treat as operational/data, not automatically product regression).
- **Streamlit** session state: centralization touches many widgets—need clear state owner and regression checks.
- **Copy vs contracts**: disagreement/strategy wording must stay aligned with `docs/SEMANTIC_CONTRACTS.md`.

## Stop / escalate conditions
- **Stop / escalate** if verification is failing (unit tests, primary smoke, or agreed launch-and-inspect) and the fix path is unclear.
- **Stop / escalate** if work drifts from `ORIGINAL_SPEC.md` / one-screen lab phase acceptance or if refactors sprawl beyond the feature slice boundary without manager/human agreement.
- **Stop / escalate** if repo hygiene degrades (conflicting patterns, duplicate sources of truth) in a way that blocks the next increment.

## Last updated
2026-04-13 by agent (**DOCS-ONLY control-plane** — Phase 2 charter + Sprint 001 spec + workflow metrics added; `CURRENT_FRONTIER` / `HANDOFF` aligned). Prior: 2026-04-11 by agent (CLOSEOUT — Phase 1 declared complete after phase-exit confirmation vs `PHASE_1_EXIT_CRITERIA.md`; pytest **41** + smoke **A** `artifacts/ui_smoke/20260411_163249/`).
