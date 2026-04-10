# CURRENT_FRONTIER

Purpose: live steering document for the current phase. Updateable; should reflect current reality.

**Feature slice sizing:** the frontier should support **a few larger, testable next–feature-slice options**—not only tiny patches—while still avoiding blind big-bang rewrites.

## Current phase
**Phase: One-screen implied lab (manual exploration)**  
*(Spec anchor: `docs/SPRINT_1_SPEC.md`. Numbered increments are **feature slices**—e.g. feature slice 006—formerly referred to as “Sprint NNN”.)*

## Top goal
Ship a **coherent one-screen implied lab** that matches `docs/SPRINT_1_SPEC.md`: fast comprehension, two-column layout, chart high on the page, clear mode/belief switches, summary stats, centralized state for visible outputs.

## Success condition for this phase
A new user can in ~**15 seconds** answer: what the **market-implied** view shows, what **belief** they are expressing, what **trade/strategy shape** they are inspecting, and **payoff stats**—with advanced math tucked away and semantics consistent with `docs/SEMANTIC_CONTRACTS.md`.

## Current feature slice
**None active.** **Feature slice 007** (flatter **Trade ticket** path + review/layout copy alignment) is **formally closed** (Execution step 27, 2026-04-10): `python -m pytest -q` green (**36** tests); primary smoke **A_width_target_payoff** green — manifest `artifacts/ui_smoke/20260410_180727/ui_smoke_manifest.json` (`trade_ticket_found` **true**). **Smoke C** not required (layout/copy-only slice; per validation tiers). **Screenshot caveat:** scenario **A** still expands **Verification** and uses `full_page=False` capture — the default **A** PNG may show **Decision-ready review** linkage copy but **not** the **Belief vs market — at a glance** / **Trade ticket** stack; confirm the flatter path with a local scroll or ad-hoc capture when needed.

## Completed recently
- **Feature slice 007 (closed): Trade ticket path + linkage copy** — `right_ticket_slot` + `_implied_lab_trade_ticket_code_text` / `_render_implied_lab_trade_ticket_panel` in `src/viz/app.py` (ticket immediately after glance; **Strategy details** keeps table + “ticket above” caption only); `build_decision_ready_review_payload` copy order update in `src/viz/decision_ready_review.py`; tests `tests/test_decision_ready_review.py`, `tests/test_implied_lab_trade_ticket.py`. **Closeout:** pytest **PASS**; smoke A **PASS** (manifest above); single ticket render path (no duplicate leg block).
- **Feature slice 006 (closed): Trust / provenance strip** — `build_trust_strip_lines()` in `src/viz/implied_lab_provenance.py`; `_render_trust_strip` + `right_trust_slot` in `src/viz/app.py` (under Summary, above **Decision-ready review**); tests `tests/test_trust_strip.py`. **Closeout:** pytest **PASS**; smoke A **PASS** (manifest `artifacts/ui_smoke/20260410_171958/ui_smoke_manifest.json`); deep **Verification** expander unchanged in role.
- **Feature slice 005 (closed): Decision-ready trade review** — `src/viz/decision_ready_review.py` (`build_decision_ready_review_payload`); **Decision-ready review** UI between Summary and glance; tests in `tests/test_decision_ready_review.py`. **Closeout validation:** pytest **PASS**; smoke A **PASS** (`artifacts/ui_smoke/20260410_153957/ui_smoke_manifest.json`); smoke C **FAIL** on that closeout rerun — **live-data/scenario-sensitive** (`artifacts/ui_smoke/20260410_154209/ui_smoke_manifest.json`). **Live inspection:** smoke A screenshot shows structure/payoff/linkage copy + fit-not-recommendation caption adjacent to glance.
- **Feature slice 004 (closed): Scannable main-disagreement digest** — `build_disagreement_scan_payload()` → `digest_lines`, `fit_bridge_intro`, `fit_bridge_bullets` on `belief_vs_market_glance`; glance UI shows digest/bridge first, audit trail collapsed; tests extended. **Closeout validation:** `python -m pytest -q` **PASS** (21 tests); `python scripts/run_implied_lab_ui_smoke.py` **PASS**; `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>` **PASS** (see manifests `artifacts/ui_smoke/20260410_145441/`, `artifacts/ui_smoke/20260410_150352/`).
- **Feature slice 003: Belief uncertainty capture** — added an intuitive **±% move (1σ)** uncertainty input mode (with explicit σ_ln mapping and market-horizon comparison) while preserving the existing internal lognormal belief overlay model; added focused unit tests.
- Unit test harness in `tests/` (e.g. belief/disagreement hints).
- Implied lab support modules: derive, provenance, disagreement hints/thresholds; ongoing `src/viz/app.py` evolution.
- Primary automated UI smoke: `scripts/run_implied_lab_ui_smoke.py` + docs in `docs/IMPLIED_LAB_SMOKE.md`.
- Handoff updated: app launch, headless readiness, and local inspection path documented.
- **Feature slice 002: market-first top-of-screen layout closure** — implied-lab market view is now the opening anchor; price/prediction context demoted to a collapsed “Market context … reference only” block.

## Next best feature slice candidates
1. **One-screen lab layout & summary polish (bounded)** — With market-first ordering in place, tighten the first-screen answers (asset, horizon/expiry, “market-implied anchor”, and “where to state my view next”) without moving semantics or expanding features.
2. **Operational hardening (optional)** — If headless smoke runs ever hang with stale local Python/Streamlit processes, document “clear stuck processes before re-run”; keep scope to runbook only unless a reproducible harness bug appears.
3. **Lab state centralization pass** — Only if state complexity is now blocking incremental UX improvements; keep it constrained to viz/session ownership and use smoke+tests to prevent regressions.

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
2026-04-10 by agent (Execution step 27 — feature slice 007 closed; pytest + smoke A green; smoke A screenshot framing caveat for glance + trade ticket path documented)
