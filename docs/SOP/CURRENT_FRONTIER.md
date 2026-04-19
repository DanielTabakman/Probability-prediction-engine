# CURRENT_FRONTIER

Purpose: live steering document for the current phase. Updateable; should reflect current reality.

**Feature slice sizing:** the frontier should support **a few larger, testable next–feature-slice options**—not only tiny patches—while still avoiding blind big-bang rewrites.

## Current phase
**Phase 1 (one-screen BTC implied lab) — COMPLETE** (2026-04-11, phase-exit confirmation CLOSEOUT).  
*(Spec anchor: `docs/SPRINT_1_SPEC.md`. Numbered increments are **feature slices**—e.g. feature slice 006—formerly referred to as “Sprint NNN”.)*

**Active phase (chartered):** **Phase 2 — Desirability / Playability / UX** — `docs/SOP/PHASE_2_CHARTER.md`.  
**Sprint 001 — Phase 2 (wrapped / archive):** `docs/SOP/SPRINT_001_PHASE_2.md` — **primary loop complete** (2026-04-17, **outcome B**); **no active Sprint 001 BUILD slice**.  
**Sprint 002 — Phase 2 (active):** `docs/SOP/SPRINT_002_PHASE_2.md` — **lightweight sprint map** in **§6**; **Sprint002-Slice003** closed in **§9**; **Sprint002-Slice004** chartered in **§10** (pending **BUILD**). **Sprint002-Slice001 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`ff40b48deb7acf4b2d897a09287e69ed7148abd9`**). **Sprint002-Slice002 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`**). **Sprint002-Slice003 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`6e5f5635acb9371af17ce7d8621f70ceb0072215`** on `recovery/frontier-steward-v2_1-baseline`). **Current selected slice (BUILD boundary):** **Sprint002-Slice004** — **local region story / chart-adjacent meaning cue** (see **`docs/SOP/SPRINT_002_PHASE_2.md` §10**). **No slice in-flight** under **BUILD** until a BUILD pass branches from the clean baseline per preflight. **Next pending execution step:** **BUILD** — implement **Sprint002-Slice004** within **§10** bounds **or** steward **RECOVERY/SELECTION** adjustment if preflight blocks BUILD.  

**Steering continuity (doc-state, canonical):**
- **Phase 2 is active.**
- **Sprint 001 — primary interaction loop: COMPLETE (wrap posture)** as of **2026-04-17** control-plane **SELECTION** (demo coherence checklist vs `PHASE_2_CHARTER.md` §9 and `SPRINT_001_PHASE_2.md` §5; outcome **B** — no chartered **Slice 012**). Further one-screen UX under Sprint 001 would default to **polish drift** (layout/copy tweaks without a new fuzzy→legible category) relative to the closed loop: **loaded state → obvious move → visible main-object change → plain-English meaning → repeat-play affordances** (**Slices 005–011**).
- **Slices 001–011 are closed** (canonical ledger posture for Sprint 001 unless explicitly superseded by newer accepted docs).
- **Slice 005 (CLOSED):** **Sprint 001 — Slice 005 — Starter state + one obvious first move (presets)**.
- **Slice 006 (CLOSED):** **Sprint 001 — Slice 006 — Last-action meaning: plain-English “what changed?” readout** (preset-driven readout shipped on baseline).
- **Slice 007 (CLOSED):** **Sprint 001 — Slice 007 — Last-action meaning for non-preset interactions** (extend the “what changed?” readout beyond presets; shipped on accepted baseline).
- **Slice 008 (CLOSED):** **Sprint 001 — Slice 008 — Progressive disclosure & advanced de-emphasis (instrument hierarchy)** — shipped on accepted baseline (`99a54f2` and later; includes smoke-harness companion); bounded per `docs/SOP/SPRINT_001_PHASE_2.md` §3 (**trust/provenance** remains visible).
- **Slice 009 (CLOSED):** **Sprint 001 — Slice 009** — **not** the same identifier as legacy Phase 1 **Feature slice 009** (operator runbook, closed). Scope intent: bounded **repeat-play / follow-on interaction** quality within the Phase 2 primary loop (`docs/SOP/PHASE_2_CHARTER.md` §9 behavioral witness: clarity after a **second and third** meaningful interaction), **layout/copy/affordance-only** unless an approved contract note exists; no architecture program. **Shipped on accepted baseline.**
- **Slice 010 (CLOSED):** **Sprint 001 — Slice 010 (Phase 2)** — extend “What changed” to belief + target-payoff. **Shipped on accepted baseline.**
- **Slice 011 (CLOSED):** **Sprint 001 — Slice 011 (Phase 2)** — guided **“Try next”** follow-on affordances (one-click buttons on existing preset/meaning paths; **layout/copy/affordance-only** relative to semantic contracts). **Shipped on accepted baseline** (`29df0069cbbd14fdb96a8bfdda9c4b46329d7cea`).
- **Sprint002-Slice001 (CLOSED, product):** **Shape focus prompts + AOI scaffolding** — chart x-axis window control + post-interaction **where-to-look** copy (existing glance fields only); **`src/viz/app.py`**. **Shipped** at product commit **`ff40b48deb7acf4b2d897a09287e69ed7148abd9`** (ancestor of current baseline tip). **Closeout validation (Slice001):** `python -m pytest -q` → **51** passed; primary smoke **PASS** — `artifacts/ui_smoke/20260418_160804/ui_smoke_manifest.json`; `artifacts/ui_smoke/20260418_160804/A_width_target_payoff.png`.
- **Sprint002-Slice002 (CLOSED, product):** **Focus persistence / “return to my region”** — session **`st.session_state`** bookmark of last non–full-range **X-axis window** + **“Return to last chart view”** in the Slice001 shape-focus strip; **`src/viz/app.py`**. **Shipped on accepted baseline** at product commit **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`** (verify with `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline`). **Closeout validation:** `python -m pytest -q` → **51** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260418_163043/ui_smoke_manifest.json`; screenshot `artifacts/ui_smoke/20260418_163043/A_width_target_payoff.png`.
- **Sprint002-Slice003 (CLOSED, product):** **Vocabulary consistency / local region meaning alignment** — unified **shape window** / **underlying-price axis** wording across shape-focus strip, chart-adjacent hints, glance lead caption, and **“What changed?”** (incl. `shape_window` last-action); **`src/viz/app.py`**, **`src/viz/implied_lab_last_action.py`**, **`tests/test_implied_lab_last_action.py`**. **Shipped on accepted baseline** at product commit **`6e5f5635acb9371af17ce7d8621f70ceb0072215`** (verify with `git rev-parse HEAD`; verify product with `git merge-base --is-ancestor 6e5f5635acb9371af17ce7d8621f70ceb0072215 HEAD`). **Closeout validation:** `python -m pytest -q` → **52** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260418_220503/ui_smoke_manifest.json`; screenshot `artifacts/ui_smoke/20260418_220503/A_width_target_payoff.png`.

**Repo-state gate (operational, separate from steering):**

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` (use branch **tip**; verify with `git rev-parse HEAD`)
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **BUILD may proceed** from the clean baseline **without using parked branches** (use a fresh BUILD branch/worktree; obey preflight + single-plane rules) **after** the next **SELECTION** names a slice boundary. The parked deferred state remains **explicitly unaccepted** and does not gate baseline-based BUILD.

This does **not** erase or downgrade the steering state above; it only blocks execution.

**Honest supersession note:** `CURRENT_FRONTIER` / `HANDOFF` previously named **paid beta / commercial wrapper** as the **immediate** next planning boundary (also reflected in `docs/SOP/PHASE_1_EXIT_CRITERIA.md` as a **Phase 1 closeout snapshot** — e.g. “likely next phase” toward commercial wrapper). That snapshot is **not deleted**; for **operative planning after 2026-04-13**, this file plus `docs/SOP/PHASE_2_CHARTER.md` **supersede** it for **what executes next**. **Paid beta / commercial wrapper** remains a **valid later product boundary**, now treated as **Phase 3–class** (monetization / distribution / commercial wrapper layer) — **deferred, not canceled** — and still requires its **own** charter before BUILD.

**Optional engineering (unchanged posture):** bounded **state centralization** / runbook-only hardening remains **deferred** per `PHASE_1_EXIT_CRITERIA.md` section 6 and **Next best feature slice candidates** below, **unless** a future phase or incident—or a **deterministic Phase 2 blocker**—justifies a **separate enabling slice** (see Phase 2 charter anti–architecture-creep clause).

## Top goal (achieved for Phase 1)
The repo shipped a **coherent one-screen implied lab** matching `docs/SPRINT_1_SPEC.md`: fast comprehension, two-column layout, chart high on the page, clear mode/belief switches, summary stats; Sprint 1 **directional** state principle acknowledged without a state-centralization gate for exit (`docs/SOP/PHASE_1_EXIT_CRITERIA.md` section 4).

## Success condition for this phase (met)
A new user can in ~**15 seconds** answer: what the **market-implied** view shows, what **belief** they are expressing, what **trade/strategy shape** they are inspecting, and **payoff stats**—with advanced math tucked away and semantics consistent with `docs/SEMANTIC_CONTRACTS.md`. Trust/provenance and degraded market-data honesty are covered (feature slice **010** and verification payload fields such as `market_data_legibility`).

**Formal phase-exit rubric:** `docs/SOP/PHASE_1_EXIT_CRITERIA.md` (feature slice **011**). **Phase-exit confirmation** (same doc, section 5 + section 3 assessment): `python -m pytest -q` → **41** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260411_163249/ui_smoke_manifest.json` (page load, disagreement, strategy family block, trade ticket, **Verification** expander found).

## Current feature slice
**Sprint002-Slice004 (selected — pending BUILD).** **Sprint002-Slice001**, **Sprint002-Slice002**, and **Sprint002-Slice003** are **closed/shipped** on the accepted baseline. **Verify repo tip:** `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline` (post–Slice004 **SELECTION** docs). **Verify Slice003 product on that tip:** `git merge-base --is-ancestor 6e5f5635acb9371af17ce7d8621f70ceb0072215 HEAD`. Spec anchor: **`docs/SOP/SPRINT_002_PHASE_2.md` §10**.

**Sprint 001 — Slice 011** — **closed/shipped** (demo coherence **outcome B**, 2026-04-17); no **Slice 012**.

**Next pending execution step:** **BUILD** — **Sprint002-Slice004** per **`docs/SOP/SPRINT_002_PHASE_2.md` §10** (bounded **chart-adjacent / glance-adjacent** descriptive meaning; **no** recommendation logic; **no** major contract rewrite; **no** new metrics if existing glance / last-action / shape-window fields can be reused; **no** broad memory/comparison subsystem). **This pass:** **SELECTION** (control-plane only; **no product delta**).

**Selection posture (Bellman / MDP, Slice004):** After find → return → **consistent naming**, the highest **next-state quality** at bounded cost is a **single compact descriptive “what’s going on here” read** for the **active local region**, improving **interpretability** and **mental model carry** while preserving **option value** for later **§6.C** affordances (still **non-advisory**, **contract-grounded**).

**Ledger hygiene note (important):** The “Completed recently” list below contains **historical notes** that may include **local / unaccepted** product/harness/test deltas. **Do not treat those as canonized closures** unless they are backed by an accepted repo-state (commit/push) and reconciled against the repo-state gate. The canonical steering ledger for Phase 2/Sprint 001 is stated above under **Steering continuity (doc-state, canonical)**.

## Completed recently
- **Sprint002-Slice003 (CLOSED, product):** shape-window vocabulary alignment — **`6e5f563`**; pytest **52** passed; primary smoke **PASS** (`artifacts/ui_smoke/20260418_220503/`).
- **Sprint002-Slice002 (CLOSED, product):** return-to-last-chart-view persistence — **`bd12b7c`**; pytest **51** passed; primary smoke **PASS** (`artifacts/ui_smoke/20260418_163043/`).
- **Sprint002-Slice001 (CLOSED, product):** shape focus + AOI scaffolding — **`ff40b48`**; pytest **51** passed; primary smoke **PASS** (`artifacts/ui_smoke/20260418_160804/`).
- **Sprint 001 — Slice 011 (CLOSED, product):** guided **“Try next”** one-click affordances under **“What changed?”** (existing presets/meaning readout) — shipped on accepted baseline (`29df0069cbbd14fdb96a8bfdda9c4b46329d7cea`).
- **Sprint 001 — Slice 008 (CLOSED, product + smoke harness):** progressive disclosure & advanced de-emphasis (instrument hierarchy) — shipped on accepted baseline (`99a54f2` and later; baseline tip includes transactional starter `scripts/frontier_start_pass.py`).
- **Sprint 001 — Slice 009 (CLOSED):** repeat-play / follow-on interaction quality within the Phase 2 primary loop — shipped/closed on accepted baseline.
- **Sprint 001 — Slice 010 (CLOSED):** extend “What changed” to belief + target-payoff — shipped/closed on accepted baseline.
- **Sprint 001 — Slice 006 (CLOSED, product):** plain-English preset “what changed?” readout — shipped on accepted baseline (`519d6d7` and later).
- **Sprint 001 — Slice 007 (CLOSED, product):** last-action meaning for **non-preset** interactions — shipped on accepted baseline (precedes current baseline tip).
- **Feature slice 011 (docs-only): Phase 1 exit criteria and demo acceptance** — `docs/SOP/PHASE_1_EXIT_CRITERIA.md`; control-plane alignment. **Closeout evidence:** documentation review only (no product code changes claimed in this slice closeout record).
- **Feature slice 009 (closed): Implied lab operator runbook** — `docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md`; HANDOFF/CURRENT_FRONTIER cross-links; `docs/IMPLIED_LAB_SMOKE.md`, `docs/Frontier_Steward_Handoff.md`. **Closeout:** docs-only; pytest/smoke not required for that slice.
- **Feature slice 008 (local / unaccepted notes): Glance-first orientation polish** — historical implementation notes only; **do not treat as accepted closure** unless repo-state is reconciled and committed.
- **Legacy Phase 1 increment (older “Sprint/Feature 006” id — trust / provenance strip):** **CLOSED** — distinct from **Sprint 001 — Slice 006** (Phase 2 last-action readout).
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
2026-04-18 by agent (**CONTROL-PLANE SELECTION — Frontier Steward 2.2**): **Sprint002-Slice004** **selected** (charter **`docs/SOP/SPRINT_002_PHASE_2.md` §10**); **next** = **BUILD**. **No product code** in this pass. Prior same day: **CLOSEOUT** Slice003 (`6e5f563`); **BUILD** + promotion Slice003; **SELECTION** Slice003; **CLOSEOUT** Slice002 (`bd12b7c`).
