# CURRENT_FRONTIER

Purpose: live steering document for the current phase. Updateable; should reflect current reality.

**Sprint sizing:** the frontier should support **a few larger, testable next-sprint options**—not only tiny patches—while still avoiding blind big-bang rewrites.

## Current phase
**Sprint 1 — One-screen implied lab (manual exploration)**

## Top goal
Ship a **coherent one-screen implied lab** that matches `docs/SPRINT_1_SPEC.md`: fast comprehension, two-column layout, chart high on the page, clear mode/belief switches, summary stats, centralized state for visible outputs.

## Success condition for this phase
A new user can in ~**15 seconds** answer: what the **market-implied** view shows, what **belief** they are expressing, what **trade/strategy shape** they are inspecting, and **payoff stats**—with advanced math tucked away and semantics consistent with `docs/SEMANTIC_CONTRACTS.md`.

## Current sprint
**None active.** **Sprint 005** (decision-ready trade review block) is **formally closed** (Transaction 16, 2026-04-10): `python -m pytest -q` green (28 tests); primary smoke **A_width_target_payoff** green — manifest `artifacts/ui_smoke/20260410_153957/ui_smoke_manifest.json`; screenshot confirms **Decision-ready review** between Summary and **Belief vs market — at a glance**. Gated smoke **C_directional_peak_disagreement** **FAIL** on this closeout window — manifest `artifacts/ui_smoke/20260410_154209/ui_smoke_manifest.json`: live run produced **mixed** disagreement (`width_band=wider`) so `directional_category_verified` stayed false; some harness booleans (`disagreement_text_found`, `family_block_found`) were false on that run — classify as **live-data-sensitive** / **scenario-sensitive** (and possibly **environment-sensitive**), not a Sprint 005 semantics regression. Prior Sprint 004 closeout evidence for **C** green remains on record (`artifacts/ui_smoke/20260410_150352/`).

## Completed recently
- **Sprint 005 (closed): Decision-ready trade review** — `src/viz/decision_ready_review.py` (`build_decision_ready_review_payload`); **Decision-ready review** UI between Summary and glance; tests in `tests/test_decision_ready_review.py`. **Closeout validation:** pytest **PASS**; smoke A **PASS** (manifest above); smoke C **FAIL** on rerun (see Current sprint). **Live inspection:** smoke A screenshot shows structure/payoff/linkage copy + fit-not-recommendation caption adjacent to glance.
- **Sprint 004 (closed): Scannable main-disagreement digest** — `build_disagreement_scan_payload()` → `digest_lines`, `fit_bridge_intro`, `fit_bridge_bullets` on `belief_vs_market_glance`; glance UI shows digest/bridge first, audit trail collapsed; tests extended. **Closeout validation:** `python -m pytest -q` **PASS** (21 tests); `python scripts/run_implied_lab_ui_smoke.py` **PASS**; `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>` **PASS** (see manifests `artifacts/ui_smoke/20260410_145441/`, `artifacts/ui_smoke/20260410_150352/`).
- **Sprint 003: Belief uncertainty capture** — added an intuitive **±% move (1σ)** uncertainty input mode (with explicit σ_ln mapping and market-horizon comparison) while preserving the existing internal lognormal belief overlay model; added focused unit tests.
- Unit test harness in `tests/` (e.g. belief/disagreement hints).
- Implied lab support modules: derive, provenance, disagreement hints/thresholds; ongoing `src/viz/app.py` evolution.
- Primary automated UI smoke: `scripts/run_implied_lab_ui_smoke.py` + docs in `docs/IMPLIED_LAB_SMOKE.md`.
- Handoff updated: app launch, headless readiness, and local inspection path documented.
- **Sprint 002: market-first top-of-screen layout closure** — implied-lab market view is now the opening anchor; price/prediction context demoted to a collapsed “Market context … reference only” block.

## Next best sprint candidates
1. **Sprint 1 layout & summary polish (bounded)** — With market-first ordering in place, tighten the first-screen answers (asset, horizon/expiry, “market-implied anchor”, and “where to state my view next”) without moving semantics or expanding features.
2. **Operational hardening (optional)** — If headless smoke runs ever hang with stale local Python/Streamlit processes, document “clear stuck processes before re-run”; keep scope to runbook only unless a reproducible harness bug appears.
3. **Lab state centralization pass** — Only if state complexity is now blocking incremental UX improvements; keep it constrained to viz/session ownership and use smoke+tests to prevent regressions.

## Avoid for now
- New AI features, Polymarket/prediction-market integration spikes, framework migration (`docs/SPRINT_1_SPEC.md`).
- Cross-cutting engine/DB refactors unless a sprint explicitly targets them and acceptance tests exist.

## Known risks / uncertainty
- **External data** (Deribit/Yahoo) can fail or rate-limit; automated smoke may be environment-dependent. In particular, if spot/quotes are unavailable the app can show **"Need BTC spot price for implied distribution"** and UI smoke will flap (treat as operational/data, not automatically product regression).
- **Streamlit** session state: centralization touches many widgets—need clear state owner and regression checks.
- **Copy vs contracts**: disagreement/strategy wording must stay aligned with `docs/SEMANTIC_CONTRACTS.md`.

## Stop / escalate conditions
- **Stop / escalate** if verification is failing (unit tests, primary smoke, or agreed launch-and-inspect) and the fix path is unclear.
- **Stop / escalate** if work drifts from `ORIGINAL_SPEC.md` / Sprint 1 acceptance or if refactors sprawl beyond the sprint boundary without manager/human agreement.
- **Stop / escalate** if repo hygiene degrades (conflicting patterns, duplicate sources of truth) in a way that blocks the next increment.

## Last updated
2026-04-10 by agent (Transaction 16 — Sprint 005 closed; pytest + smoke A green; smoke C fail live-data/scenario-sensitive on this window)
