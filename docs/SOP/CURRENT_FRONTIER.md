# CURRENT_FRONTIER

Purpose: live steering document for the current phase. Updateable; should reflect current reality.

**Feature slice sizing:** the frontier should support **a few larger, testable next–feature-slice options**—not only tiny patches—while still avoiding blind big-bang rewrites.

## Current phase
**Phase 1 (one-screen BTC implied lab) — COMPLETE** (2026-04-11, phase-exit confirmation CLOSEOUT).  
*(Spec anchor: `docs/SPRINT_1_SPEC.md`. Numbered increments are **feature slices**—e.g. feature slice 006—formerly referred to as “Sprint NNN”.)*

**Active phase (chartered):** **Phase 2 — Desirability / Playability / UX** — `docs/SOP/PHASE_2_CHARTER.md`.  
**Sprint 001 — Phase 2 (wrapped / archive):** `docs/SOP/SPRINT_001_PHASE_2.md` — **primary loop complete** (2026-04-17, **outcome B**); **no active Sprint 001 BUILD slice**.  
**Sprint 002 — Phase 2 (wrapped / archive):** `docs/SOP/SPRINT_002_PHASE_2.md` — **primary loop complete** (2026-04-18: coherence **SELECTION outcome A** + **WRAP CLOSEOUT**; ledger **`docs/SOP/SPRINT_002_PHASE_2.md` §11–§12**). **Sprint002-Slice001 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`ff40b48deb7acf4b2d897a09287e69ed7148abd9`**). **Sprint002-Slice002 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`**). **Sprint002-Slice003 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`6e5f5635acb9371af17ce7d8621f70ceb0072215`**). **Sprint002-Slice004 — CLOSED / shipped** (2026-04-18 **CLOSEOUT**; product **`6be6d7c5401c489bb702fb1ea40b4bee93ad8907`** on `recovery/frontier-steward-v2_1-baseline`; verify `git merge-base --is-ancestor 6be6d7c5401c489bb702fb1ea40b4bee93ad8907 HEAD`). **No further Sprint 002 BUILD slice** selected; **§6.C** map items remain **deferred candidates only**.  
**Sprint 003 — Phase 2 (chartered, narrow):** `docs/SOP/SPRINT_003_PHASE_2.md` — **Pilot-driven evidence-plane hardening (relay-assisted)** — chartered **2026-04-20** as a deliberately narrow sprint to carry **tiny, pilot-evidence-driven evidence-plane hardening slices** executed via `docs/SOP/RELAY_RUNTIME_V0.md`. **Not** a Phase 2 product UX sprint; does **not** advance Phase 2 product acceptance and does **not** reopen Sprint 001 / Sprint 002. **Sprint003-Slice001 — SELECTED** (2026-04-20, **first real relay-assisted slice**; see §1.A below). **Next pending execution step:** **BUILD via relay-assisted execution** — operator invokes `run_selected_slice_v1` (Job Registry v1 §3.1) with `slice_id = "Sprint003-Slice001"`, `sprint_spec_path = "docs/SOP/SPRINT_003_PHASE_2.md"`, `declared_plane = "EVIDENCE-PLANE"`; §15 decision, promotion, and CONTROL-CLOSEOUT follow per `RELAY_RUNTIME_V0.md` §7.2 and `CODEX_AUTONOMY_V1.md` §§2, 9, 14–15.  

**Steering continuity (doc-state, canonical):**
- **Phase 2 is active** (`docs/SOP/PHASE_2_CHARTER.md`). **Sprint 002** is **wrapped**. **Sprint 003** is **chartered** (2026-04-20) as a **narrow pilot-driven evidence-plane hardening sprint** (`docs/SOP/SPRINT_003_PHASE_2.md`); it is **not** a Phase 2 product UX sprint and does **not** advance the Phase 2 product charter's desirability/playability acceptance. **Sprint003-Slice001** is **SELECTED** — the **first real relay-assisted slice** following successful Relay Runtime V0 pilots (read-only, staged/manual-resume, forensic-replay).
- **Sprint 002 — wrapped / archive (2026-04-18):** **SELECTION outcome A** (no **Sprint002-Slice005**) + **WRAP CLOSEOUT**; shipped spine **find → return → name → situate** (**Slices 001–004**). Optional/deferred ideas (**`SPRINT_002_PHASE_2.md` §6.C** and similar) stay **deferred** — not selected by wrap.
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
- **Sprint002-Slice004 (CLOSED, product):** **Local region story / chart-adjacent meaning cue** — compact **local region** read (chart column + shape-strip cue) from existing **shape window** + glance fields; **`src/viz/app.py`**, **`src/viz/implied_lab_last_action.py`**, **`tests/test_implied_lab_last_action.py`**. **Shipped on accepted baseline** at product commit **`6be6d7c5401c489bb702fb1ea40b4bee93ad8907`** (verify `git merge-base --is-ancestor 6be6d7c5401c489bb702fb1ea40b4bee93ad8907 HEAD`). **Closeout validation:** `python -m pytest -q` → **55** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260418_222621/ui_smoke_manifest.json`; screenshot `artifacts/ui_smoke/20260418_222621/A_width_target_payoff.png`.

**Repo-state gate (operational, separate from steering):**

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` (use branch **tip**; verify with `git rev-parse HEAD`)
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **BUILD may proceed** from the clean baseline **without using parked branches** (use a fresh BUILD branch/worktree; obey preflight + single-plane rules) **after** the next **SELECTION** yields an explicit **chartered** slice boundary (**Sprint 002** is **wrapped** — **no** Sprint 002 BUILD work pending). The parked deferred state remains **explicitly unaccepted** and does not gate baseline-based BUILD.

This does **not** erase or downgrade the steering state above; it only blocks execution.

**Honest supersession note:** `CURRENT_FRONTIER` / `HANDOFF` previously named **paid beta / commercial wrapper** as the **immediate** next planning boundary (also reflected in `docs/SOP/PHASE_1_EXIT_CRITERIA.md` as a **Phase 1 closeout snapshot** — e.g. “likely next phase” toward commercial wrapper). That snapshot is **not deleted**; for **operative planning after 2026-04-13**, this file plus `docs/SOP/PHASE_2_CHARTER.md` **supersede** it for **what executes next**. **Paid beta / commercial wrapper** remains a **valid later product boundary**, now treated as **Phase 3–class** (monetization / distribution / commercial wrapper layer) — **deferred, not canceled** — and still requires its **own** charter before BUILD.

**Optional engineering (unchanged posture):** bounded **state centralization** / runbook-only hardening remains **deferred** per `PHASE_1_EXIT_CRITERIA.md` section 6 and **Next best feature slice candidates** below, **unless** a future phase or incident—or a **deterministic Phase 2 blocker**—justifies a **separate enabling slice** (see Phase 2 charter anti–architecture-creep clause).

## Top goal (achieved for Phase 1)
The repo shipped a **coherent one-screen implied lab** matching `docs/SPRINT_1_SPEC.md`: fast comprehension, two-column layout, chart high on the page, clear mode/belief switches, summary stats; Sprint 1 **directional** state principle acknowledged without a state-centralization gate for exit (`docs/SOP/PHASE_1_EXIT_CRITERIA.md` section 4).

## Success condition for this phase (met)
A new user can in ~**15 seconds** answer: what the **market-implied** view shows, what **belief** they are expressing, what **trade/strategy shape** they are inspecting, and **payoff stats**—with advanced math tucked away and semantics consistent with `docs/SEMANTIC_CONTRACTS.md`. Trust/provenance and degraded market-data honesty are covered (feature slice **010** and verification payload fields such as `market_data_legibility`).

**Formal phase-exit rubric:** `docs/SOP/PHASE_1_EXIT_CRITERIA.md` (feature slice **011**). **Phase-exit confirmation** (same doc, section 5 + section 3 assessment): `python -m pytest -q` → **41** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — manifest `artifacts/ui_smoke/20260411_163249/ui_smoke_manifest.json` (page load, disagreement, strategy family block, trade ticket, **Verification** expander found).

## Current feature slice
**Sprint003-Slice001 — SELECTED (2026-04-20, first real relay-assisted slice).** Title: **`control_plane_consistency_check` placeholder-literal suppression.** Declared plane: **EVIDENCE-PLANE**. Spec anchor: **`docs/SOP/SPRINT_003_PHASE_2.md` §7** (slice definition), **§8** (execution posture). Sprint-level spec: **`docs/SOP/SPRINT_003_PHASE_2.md` §§1–6, §9 (ledger)**.

**Grounding (pilot evidence):** first read-only relay pilot surfaced 3 benign warnings from `control_plane_consistency_check` caused by documentation template placeholders (`SPRINT_00X.md`, `SPRINT_00X_PHASE_Y.md`) in `docs/SOP/OPERATING_RULES.md`, `docs/SOP/CODEX_AUTONOMY_V1.md`, and `docs/SOP/JOB_REGISTRY_V1.md`. Those placeholders are intentional SOP template variables and must stay as-is; the fix lives in the **checker**, not in the docs. Artifact class: `artifacts/health/<timestamp>/control_plane_consistency_report.json`.

**Exact target of the slice BUILD diff:** `scripts/relay_runtime_v0.py` (function `dispatch_control_plane_consistency_check`, step 3 — backtick-quoted reference resolution) and `tests/test_relay_runtime_v0.py` (positive-suppression + negative-still-flagged unit tests). **No writes** under `docs/SOP/**`, `docs/CONTROL_PLANE/**`, `src/viz/**`, or `orchestrator/`.

**Sprint 002 — closed/shipped on accepted baseline.** **Sprint002-Slice001–Slice004** remain **closed/shipped**. **Verify repo tip:** `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline` (must include Sprint 002 **WRAP CLOSEOUT** — `docs/SOP/SPRINT_002_PHASE_2.md` **§12** present on branch tip). **Verify Slice004 product on that tip:** `git merge-base --is-ancestor 6be6d7c5401c489bb702fb1ea40b4bee93ad8907 HEAD`. Spec anchors: **`docs/SOP/SPRINT_002_PHASE_2.md` §7–§12**.

**Sprint 001 — Slice 011** — **closed/shipped** (demo coherence **outcome B**, 2026-04-17); no **Slice 012**.

**Next pending execution step:** **BUILD via relay-assisted execution** — operator invokes `run_selected_slice_v1` (`docs/SOP/JOB_REGISTRY_V1.md` §3.1) with:
- `slice_id = "Sprint003-Slice001"`
- `sprint_spec_path = "docs/SOP/SPRINT_003_PHASE_2.md"`
- `declared_plane = "EVIDENCE-PLANE"`
- `baseline_branch = recovery/frontier-steward-v2_1-baseline` (verify with `git rev-parse HEAD`)
- `build_branch` = fresh (must not pre-exist locally or on remote)
- `retry_budget_max = 2` (`CODEX_AUTONOMY_V1` §7 default)

Dispatch model: **staged / manual-resume** (`docs/SOP/RELAY_RUNTIME_V0.md` §7.2). **No** product SHA yet. **No** CONTROL-CLOSEOUT until the relay emits a §14.1 payload with `stop_condition == null` and `relay_gate_decision` returns §15 `CONTINUE`; CONTROL-CLOSEOUT then remains **steward-only** per `CODEX_AUTONOMY_V1` §§2, 10 and `RELAY_RUNTIME_V0` §10.

**Why this is the first real relay-assisted slice:** directly pilot-grounded, evidence-plane-only, single function / single rule / single pair of unit tests, no product exposure, no control-plane doc churn at BUILD, clean stop-and-return-to-SELECTION failure mode if the narrow rule cannot be expressed without widening scope.

**Closeout posture (Bellman / MDP, Slice004):** Shipped **local region story** **compresses interpretive ambiguity** at the **active shape window** (find → return → **name** → **situate**), improving **legibility of what the user is looking at** without paying **§6.C** affordance or **contract** transition cost in this slice.

**Steward-facing next posture:** **Sprint 002** is **wrapped**; execute **SELECTION** for **Sprint 003** or **phase** next — **not** implicit **§6.C** BUILD.

**Autonomy posture (Sprint 003 onward, optional):** `docs/SOP/CODEX_AUTONOMY_V1.md` is available as an **opt-in** protocol for Codex BUILD runs once a slice is selected. Authority boundary: **PREFLIGHT -> BUILD -> bounded repair -> BUILD-CLOSEOUT -> PROMOTION** for **one** slice only. **SELECTION** and **CONTROL-CLOSEOUT** remain steward-driven. Not a default; activated only by explicit declaration or sprint-spec pre-authorization.

**Ledger hygiene note (important):** The “Completed recently” list below contains **historical notes** that may include **local / unaccepted** product/harness/test deltas. **Do not treat those as canonized closures** unless they are backed by an accepted repo-state (commit/push) and reconciled against the repo-state gate. The canonical steering ledger for Phase 2/Sprint 001 is stated above under **Steering continuity (doc-state, canonical)**.

## Completed recently
- **Sprint 003 (CHARTERED, control-plane only, 2026-04-20):** `docs/SOP/SPRINT_003_PHASE_2.md` — **Pilot-driven evidence-plane hardening (relay-assisted)**, deliberately narrow. **Sprint003-Slice001 SELECTED** as the **first real relay-assisted slice** following successful Relay Runtime V0 local pilots (read-only, staged/manual-resume, forensic-replay). No product code changed; no protocol / registry / runtime-spec amendments.
- **Relay Runtime V0 (local pilots complete, 2026-04-20):** read-only pilot **PASS**; staged/manual-resume pilot **PASS**; forensic-replay pilot **PASS**. Spec anchor: `docs/SOP/RELAY_RUNTIME_V0.md`; implementation anchor: `scripts/relay_runtime_v0.py` (commit **`bc1b9ac`**); decision-enum reconciliation with `CODEX_AUTONOMY_V1` §15.1 at **`894ca60`**.
- **Sprint002-Slice004 (CLOSED, product):** local region story / chart-adjacent meaning cue — **`6be6d7c`**; pytest **55** passed; primary smoke **PASS** (`artifacts/ui_smoke/20260418_222621/`).
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
2026-04-20 by agent (**CONTROL-PLANE SELECTION — Frontier Steward 2.2**): **Sprint 003 chartered** as narrow **pilot-driven evidence-plane hardening (relay-assisted)** (`docs/SOP/SPRINT_003_PHASE_2.md`); **Sprint003-Slice001 SELECTED** as the **first real relay-assisted slice** (`control_plane_consistency_check` placeholder-literal suppression). Pilot-grounded in `artifacts/health/<timestamp>/control_plane_consistency_report.json`. **Next pending execution step:** **BUILD via relay-assisted execution** (`run_selected_slice_v1`, `Sprint003-Slice001`, declared plane `EVIDENCE-PLANE`). **No product code** in this pass; **no** writes under `src/viz/**`; **no** protocol / registry / runtime-spec amendments. Prior: Relay Runtime V0 local pilots complete (read-only, staged, forensic-replay). Baseline tip includes **`894ca60`** (relay-runtime decision-enum reconciliation).

2026-04-18 by agent (**CONTROL-PLANE WRAP CLOSEOUT — Frontier Steward 2.2**): **Sprint 002** **wrapped** (**SELECTION outcome A** canonized + wrap ledger **§12**); **Phase 2** remains **active**; **next** = **SELECTION** (**Sprint 003** vs **phase transition**). **No product code** in this pass. Prior: **SELECTION** outcome A (`cd78917` steering chain); Slice004 product **`6be6d7c`**.
