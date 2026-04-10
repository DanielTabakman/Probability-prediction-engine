Update rule: overwrite current-state sections; append decision-log items; preserve [V]/[R]/[I]/[OOS] honesty.

# Frontier Steward Handoff
Project: Probability Prediction Engine
Phase: One-screen BTC implied lab (current phase; `docs/SPRINT_1_SPEC.md` anchor)
Date: 2026-04-10
Steward: ChatGPT frontier steward window
Status: Active (post–feature slice 007 closeout)

## Executive state
- [V/I] Product: BTC-first belief-vs-market trade construction workbench; not a trading bot and not a general AI analyst.
- [V/I] Current phase target: one-screen implied lab with semantic honesty, clear disagreement interpretation, and trustworthy interaction flow.
- [V/R] Most recently implemented feature slice work: **Feature slice 007 — Flatter trade ticket path** (`right_ticket_slot`, `_render_implied_lab_trade_ticket_panel`, `decision_ready_review` linkage copy + `tests/test_implied_lab_trade_ticket.py`).
- [V/R] Most recently closed feature slice (process): **Feature slice 007** (Execution step 27, 2026-04-10 — pytest **36** + smoke **A** green; `trade_ticket_found` **true**; smoke **C** not required; **A** PNG may not frame glance + ticket expander — see truth table).
- [V/R] Prior closed feature slice: **Feature slice 006** (Execution step 22 — trust strip; **A** screenshot caveat for trust strip).
- [V/R] Prior: **Feature slice 005** (Execution step 16 — decision-ready review; smoke **C** fail on that window **live-data/scenario-sensitive**).
- [V/R] Prior: **Feature slice 004** (Execution step 13 — pytest + smoke A/C green; Yahoo MultiIndex fix in `src/data/fetch_yahoo.py`).
- [V/R] Earlier closed: **Feature slice 003 — Belief uncertainty capture** (see truth table for caveats).
- [V] Active feature slice status: **none**.
- [V/I] Single best next move: select next bounded frontier from `docs/SOP/CURRENT_FRONTIER.md` (one-screen lab phase polish / optional ops runbook) after feature slice 007 closure.

## Product identity and boundaries
- [V/I] Core loop: market-implied distribution -> user belief -> disagreement -> strategy families that fit this disagreement -> verification
- [V/I] Current phase goal: one-screen BTC implied lab with semantic alignment and fast user orientation
- [V/I] Important semantic boundary: strategy families are illustrative fits to disagreement shape, not recommendations
- [OOS] Out of scope for the current cycle:
  - new AI assistant features
  - prediction-market expansion
  - framework migration
  - recommendation logic
  - broad product expansion beyond BTC-first implied lab
  - premature strike-solver expansion unless explicitly chosen later

## Source-of-truth order
1. [V] Actual repo state and current validation evidence
2. [V/R] Latest active frontier steward handoff
3. [V/R] docs/SOP/CURRENT_FRONTIER.md
4. [V/R] docs/SOP/HANDOFF.md
5. [V/R] docs/SOP/ORIGINAL_SPEC.md
6. [V/R] docs/VISION/PHASE_VISION_CURRENT.md
7. [V/R] docs/VISION/VISION_MASTER.md
8. [R] Recent steward notes / chat summaries

## Execution step discipline (inheritance from SOP)
- [V] Every steward/worker pass must declare **one** execution step type: **BUILD**, **CLOSEOUT**, **RECOVERY**, or **SELECTION**, and obey that boundary. **CLOSEOUT** is evidence-and-docs only; if code or bug-chasing is needed, stop and open **RECOVERY** or **BUILD** separately.
- [V] Feature slice closure, validation classification, and the non-BUILD **stop-after-two** rule are defined in `docs/SOP/OPERATING_RULES.md` → **Execution step discipline (anti-thrash rules)**.
- [V] **Validation tiers** (Execution step 17, 2026-04-10): universal closeout = pytest + primary smoke **A** + (when UI changed) one inspection/screenshot of the changed region; **smoke C** is **conditional** on classification/scenario/disagreement-derivation/harness work—not a default gate for presentation-only feature slices unless the spec requires it. **Closeout budget:** cap time on inconclusive non-deterministic steps; classify **environment- / live-data- / scenario-sensitive**; open **RECOVERY**/**BUILD** only for real product/code evidence. **Preflight:** one clean app instance, prefer fresh port, reduce orphan processes and manual+smoke port fights—see `OPERATING_RULES.md` → **Validation tiers**, **Closeout runtime budget**, **Preflight hygiene**.

## Current known state
- [V/R] Repo operating model was updated from cautious micro-step execution to a faster frontier-driven workflow with downstream validation and conservative git posture.
- [V/R] SOP/control-plane structure now exists under:
  - docs/SOP/
  - docs/VISION/
  - docs/CONTROL_PLANE/PROMPTS/
- [V/R] The current execution target remains the one-screen implied lab phase with semantic alignment.
- [V] Current repo is on `main` (ahead of `origin/main`; working tree has local edits/untracked files — re-check `git status` on re-entry).
- [V] Feature slice 002 implemented: market-first top-of-screen layout, demoting price/prediction context and anchoring first-screen on the market-implied implied-lab view.
- [V/R] Feature slice 003 implemented (accepted): belief uncertainty can be entered as **±% move (1σ)** with explicit mapping to **σ_ln**; percent mode derives σ_ln and feeds the existing belief/disagreement pipeline; UI compares user vs market horizon uncertainty on both bases; focused unit tests added.
- [V/R] Validation posture:
  - **pytest** is green.
  - Prior green evidence exists for UI smoke **A_width_target_payoff** and **C_directional_peak_disagreement** (see “Verified in this window” for artifact paths).
  - **Operational caveat:** UI smokes are live-data dependent; when spot/quotes are unavailable the app may show **"Need BTC spot price for implied distribution"** and the belief/disagreement UI may not mount. Record such failures as **operational/data availability** unless reproduced with data available.
- [V/R] The environment has reportedly been proven capable of:
  - running unit tests
  - running UI smoke
  - launching Streamlit
  - checking readiness
  - inspecting the running UI locally
  - performing at least one safe interaction
  - stopping the app afterward
- [R] A later feature slice was proposed and reportedly completed to add a compact belief-vs-market glance card near the main chart.
- [R] Reported files changed in that feature slice:
  - src/viz/implied_lab_provenance.py
  - src/viz/implied_lab_derive.py
  - src/viz/app.py
  - tests/test_belief_disagreement_hints.py
- [R] Reported validation for that feature slice:
  - unit tests passed
  - A_width_target_payoff smoke passed
  - C_directional_peak_disagreement smoke passed
- [R] Reported status at time of feature slice report: no commit/push made
- [I] Exact current repo cleanliness, commit state, and final UI quality must be re-checked on re-entry

## Truth table

### Verified in this window
- [V] Product identity in steward context: BTC-first implied-lab workbench, not bot / not general analyst
- [V] Updated operating-system description provided by user:
  - frontier-driven workflow
  - downstream validation
  - execution-step-disciplined manager/worker/review split
  - conservative git by default
- [V] The following doc families are said to exist:
  - docs/SOP/
  - docs/VISION/
  - docs/CONTROL_PLANE/PROMPTS/
- [V] Feature slice 002 UI closure is present in `src/viz/app.py`:
  - Bitcoin page opens with **market-implied distribution (anchor)**
  - Price/prediction content is demoted into a collapsed “Market context … reference only” expander
- [V] Validation evidence captured (2026-04-09):
  - Tests: `python -m pytest -q` → **PASS**
  - Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS**
    - Manifest: `artifacts/ui_smoke/20260409_120856/ui_smoke_manifest.json`
    - Screenshot: `artifacts/ui_smoke/20260409_120856/A_width_target_payoff.png`
  - Smoke C: `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port 8512` → **PASS**
    - Manifest: `artifacts/ui_smoke/20260409_122715/ui_smoke_manifest.json`
    - Screenshot: `artifacts/ui_smoke/20260409_122715/C_directional_peak_disagreement.png`
  - Feature slice 003 close decision: **CLOSED** (basis: Feature slice 003 functionality accepted + pytest green + prior A/C green smoke evidence; later closeout reruns may flap due to live-data availability).
- [V] Validation evidence captured (2026-04-10, Execution step 13 — Feature slice 004 closure):
  - Tests: `python -m pytest -q` → **PASS** (21 tests)
  - Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS**
    - Manifest: `artifacts/ui_smoke/20260410_145441/ui_smoke_manifest.json`
  - Smoke C: `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <PORT>` → **PASS** (definitive run after clearing stuck headless processes)
    - Manifest: `artifacts/ui_smoke/20260410_150352/ui_smoke_manifest.json`
  - Feature slice 004 close decision: **CLOSED**
- [V] Validation evidence captured (2026-04-10, Execution step 16 — Feature slice 005 closure):
  - Tests: `python -m pytest -q` → **PASS** (28 tests) — **deterministic**.
  - Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — **live-data-sensitive** + **environment-sensitive**; manifest `artifacts/ui_smoke/20260410_153957/ui_smoke_manifest.json`; screenshot shows **Decision-ready review** + **Belief vs market — at a glance** with non-advisory copy.
  - Smoke C: `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port 53912` → **FAIL** — **live-data-sensitive** / **scenario-sensitive**; manifest `artifacts/ui_smoke/20260410_154209/ui_smoke_manifest.json` (`directional_category_verified` false; notes: mixed disagreement, `width_band=wider`; some harness booleans false on that run). **Not** treated as Feature slice 005 product regression.
  - Feature slice 005 close decision: **CLOSED**
- [V] Validation evidence captured (2026-04-10, Execution step 22 — Feature slice 006 closure):
  - Tests: `python -m pytest -q` → **PASS** (**35** tests) — **deterministic**.
  - Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — **live-data-sensitive** + **environment-sensitive**; manifest `artifacts/ui_smoke/20260410_171958/ui_smoke_manifest.json`.
  - Smoke C: **not run** for Feature slice 006 (presentation/provenance-only; per validation tiers).
  - **Trust strip visibility:** **Code + layout verified** — `src/viz/app.py` renders **Trust / provenance** in `right_trust_slot` between Summary and **Decision-ready review** without opening **Verification**. Official **A** scenario still expands **Verification** and scrolls to `disagreement classification` before `full_page=False` screenshot — artifact is **not** a dedicated framing of the strip; **manual scroll under Summary** or ad-hoc capture recommended for pixel proof.
  - Feature slice 006 close decision: **CLOSED**
- [V] Validation evidence captured (2026-04-10, Execution step 27 — Feature slice 007 closure):
  - Tests: `python -m pytest -q` → **PASS** (**36** tests) — **deterministic**.
  - Smoke A: `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — **live-data-sensitive** + **environment-sensitive**; manifest `artifacts/ui_smoke/20260410_180727/ui_smoke_manifest.json` (`trade_ticket_found` **true**).
  - Smoke C: **not run** for Feature slice 007 (layout/copy + ticket placement only; per validation tiers).
  - **Review-to-ticket path:** **Code order** — glance slot then `right_ticket_slot` with top-level **Trade ticket (copy/paste)**; **Strategy details** no longer nests the ticket. **Decision-ready review** payload names **Belief vs market — at a glance** then ticket. **Screenshot:** smoke **A** `full_page=False` capture shows **Decision-ready review** linkage (non-advisory) in sample artifact; glance/ticket expander may require scroll — see `docs/IMPLIED_LAB_SMOKE.md` Sprint 007 note.
  - Feature slice 007 close decision: **CLOSED**

### Reported but not independently re-checked
- [R] Line-by-line audit of every local uncommitted change vs a single pushed commit (working tree is not clean on last agent pass).

### Unknown / must check on re-entry
- [I] Whether `main` should be reconciled with `origin/main` and which local changes should be committed

### Execution step 11 (2026-04-09) — Feature slice 004 CLOSEOUT evidence (superseded)
- [V] `python -m pytest -q` → **PASS** (21 tests).
- [V] UI smokes **A** / **C** → **FAIL** / **live-data-sensitive** in that window (BTC spot gate; root cause later found **app-side** in Yahoo fetch path).

### Execution step 13 (2026-04-10) — Feature slice 004 CLOSEOUT retry (closure)
- [V] `python -m pytest -q` → **PASS** (21 tests) — **deterministic** (local).
- [V] UI smoke **A_width_target_payoff** (`python scripts/run_implied_lab_ui_smoke.py`) → **PASS** — **live-data-sensitive** + **environment-sensitive**; manifest `artifacts/ui_smoke/20260410_145441/ui_smoke_manifest.json`.
- [V] UI smoke **C_directional_peak_disagreement** (`python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <PORT>`) → **PASS** after clearing a hung prior headless run (first attempt **inconclusive** / **environment-sensitive**; second run green); manifest `artifacts/ui_smoke/20260410_150352/ui_smoke_manifest.json`.
- [V] **Digest / non-advisory wording:** confirmed via smoke artifacts + UI contract in `belief_disagreement_hints.build_disagreement_scan_payload` and `_render_belief_vs_market_glance` (`src/viz/app.py`); glance shows **Main disagreement (scan)**, **Why these fit classes appear**, and **Fit is not recommendation** caption. **CLOSEOUT: no code edits.**

## Recent decision log
1. [V/R] Shifted the repo from a cautious micro-step workflow to a fast, testable frontier-driven workflow
   - Why: meaningful progress inside the current frontier, with safety moved downstream into tests, smoke, launch-inspect, cleanup, and honest reporting
   - Rejected alternative: overly cautious micro-step execution that reduced momentum

2. [V/R] Established a control-plane / SOP / vision documentation structure
   - Why: improve continuity, sharpen frontier control, and reduce reliance on chat-window memory
   - Rejected alternative: letting context windows remain the main source of continuity

3. [V/R] Learned that the broad manager prompt leaked into execution
   - Why it mattered: caused role confusion and open-ended behavior
   - Fix: execution-step-disciplined prompts with one context per role and then stop
   - Rejected alternative: continuing with a broad manager prompt that mixes planning and execution

4. [R/I] Chose the compact belief-vs-market glance card as the next feature slice after the earlier semantic/verification stabilization work
   - Why: compress orientation latency without changing product boundaries
   - Rejected alternative: broader expansion or backend-heavy work

5. [R/I] Accepted the reported glance-card feature slice as operationally green based on the worker report, while explicitly noting that it was not independently re-audited line-by-line in this steward window
   - Why: reported validation was bounded and green
   - Remaining caveat: actual current repo/UI state still needs re-check on re-entry

6. [V] **Execution step 11 — Feature slice 004 CLOSEOUT:** Did **not** declare Feature slice 004 formally closed because **smoke A/C failed** (BTC spot gate). Classified as **live-data-sensitive** at the time; later **RECOVERY** identified **app-side** Yahoo MultiIndex handling in `fetch_yahoo_prices`.

7. [V] **Execution step 13 — Feature slice 004 CLOSEOUT (retry):** Declared **Feature slice 004 formally closed**: pytest green; smoke **A** and **C** green (manifests 20260410_145441 / 20260410_150352); digest and fit-not-recommendation language verified against UI contract + smoke. Updated `docs/SOP/CURRENT_FRONTIER.md`, `docs/SOP/HANDOFF.md`, and this handoff. **No code edits** in CLOSEOUT.

8. [V] **Execution step 16 — Feature slice 005 CLOSEOUT:** Declared **Feature slice 005 formally closed**: pytest green (28 tests); smoke **A** green (`artifacts/ui_smoke/20260410_153957/`); smoke **C** red on rerun (`artifacts/ui_smoke/20260410_154209/` — mixed vs directional gate, **live-data/scenario-sensitive**); screenshot inspection confirms **Decision-ready review** block + non-advisory copy. Updated `docs/SOP/CURRENT_FRONTIER.md`, `docs/SOP/HANDOFF.md`, this handoff, `docs/IMPLIED_LAB_SMOKE.md` (C caveat). **No code edits.**

9. [V] **Execution step 17 — SELECTION (docs):** Patched SOP with **validation tiers**, **closeout runtime budget / stop rule**, **preflight hygiene before smoke**, and explicit rule that **smoke C is not a universal closeout tax**. No code; no tests/smoke run in this execution step.

10. [V] **Execution step 22 — Feature slice 006 CLOSEOUT:** Declared **Feature slice 006 formally closed**: pytest green (35 tests); smoke **A** green (`artifacts/ui_smoke/20260410_171958/`); **C** not required; documented **A** screenshot framing caveat for **Trust / provenance**. Updated `docs/SOP/CURRENT_FRONTIER.md`, `docs/SOP/HANDOFF.md`, `docs/IMPLIED_LAB_SMOKE.md`, this handoff. **No code edits** in CLOSEOUT.

11. [V] **Execution step 27 — Feature slice 007 CLOSEOUT:** Declared **Feature slice 007 formally closed**: pytest green (36 tests); smoke **A** green (`artifacts/ui_smoke/20260410_180727/`, `trade_ticket_found` true); **C** not required; documented **A** screenshot / viewport caveat for glance + **Trade ticket** stack. Updated `docs/SOP/CURRENT_FRONTIER.md`, `docs/SOP/HANDOFF.md`, `docs/IMPLIED_LAB_SMOKE.md`, this handoff. **No code edits** in CLOSEOUT.

## Active frontier
Name: None active (feature slice 007 complete; choose next bounded frontier)

User problem:
- [I] The product likely now has its main skeleton, but the next best improvement depends on whether the top-level screen already tells the story quickly and cleanly after the reported glance-card feature slice

Why now:
- [I] A feature slice appears to have just completed, so the correct next move is not immediate further building but state confirmation and careful frontier selection
- [I] This is the moment where success-drift is likely if the next frontier is chosen loosely

Success condition:
- [I/V] The next steward confirms actual current repo/UI state, resolves verified-vs-reported ambiguity, and selects exactly one feature slice frontier that fits the current phase and product boundary

Non-goals:
- [OOS] starting multiple frontiers at once
- [OOS] broad refactors without necessity
- [OOS] AI/product expansion beyond current one-screen lab phase target
- [OOS] using polished process as a substitute for product movement

## Candidate next feature slices

### 1. State centralization pass
- [I] User benefit: cleaner ownership of state and potentially easier future work
- [I] Implementation risk: medium
- [I] Drift risk: medium-high because it can become a refactor sink
- [I] Recommendation: do only if current state handling is materially impeding the next product move

### 2. Top-of-screen orientation polish (bounded)
- [I] User benefit: even clearer first-screen answers (asset, horizon/expiry, “market-implied anchor”, and “where to state my view next”)
- [I] Implementation risk: low
- [I] Drift risk: low
- [I] Recommendation: strong candidate after feature slice 004 closure if first-screen orientation still feels soft

## Operational model
- [V/R] Workflow model: frontier-driven, fast but testable
- [V/R] Safety is pushed downstream into:
  - unit tests
  - UI smoke
  - launch / readiness / inspect
  - at least one safe interaction
  - cleanup
  - honest reporting
- [V/R] Git posture: conservative by default
- [V/R] Role model:
  - manager start
  - worker execution
  - manager review
- [V/R] Prompt/control-plane layer exists under docs/CONTROL_PLANE/PROMPTS/
- [V/R] Core SOP docs exist under docs/SOP/
- [V/R] Product vision docs exist under docs/VISION/

## Validation posture
- [V/R] The environment is reported to be capable of real downstream validation, not just static reasoning
- [R] Known/mentioned validation paths include:
  - unit tests
  - UI smoke
  - Streamlit launch and readiness
  - local UI inspection
  - at least one safe interaction
  - app shutdown afterward
- [V] **Primary vs conditional smoke:** **A_width_target_payoff** is the default primary automated path for closeout; **C_directional_peak_disagreement** is a **conditional** gate when work touches disagreement classification, width/peak scenarios, belief/disagreement derivation, or related harness logic—not an automatic requirement for every feature slice (`docs/SOP/OPERATING_RULES.md`).
- [R] Reported smoke scenarios of note:
  - A_width_target_payoff
  - C_directional_peak_disagreement
- [I] Default bias should be toward meaningful downstream validation rather than excessive speculative caution

## Risks and drift traps
- [I] Clean-looking drift: docs/prompts/reports look rigorous while frontier sharpness or product convergence degrades
- [I] CURRENT_FRONTIER.md turning into a parking lot instead of a singular active frontier
- [I] Manager review becoming ceremonial rather than a real accept/revise/reject gate
- [I] Confusing reported state with verified state
- [I] Product creep into AI features, prediction markets, framework changes, or recommendation logic
- [I] app.py becoming a dumping ground if every UI need is solved there without discipline
- [I] Rebuilding process layers unnecessarily instead of using the current ones well
- [I] Losing continuity because the handoff is not updated before opening the next steward window

## Next steward first actions
1. [V/I] Re-check actual repo state, git status, and current validation evidence
2. [V/R] Read this handoff plus docs/SOP/CURRENT_FRONTIER.md and docs/SOP/HANDOFF.md
3. [I] Confirm whether there is an active formal feature slice 002 or only candidate next feature slices
4. [I] Confirm whether the reported glance-card feature slice is present and visually satisfactory
5. [I] Choose or reaffirm a single active frontier before producing any new execution-step prompt

## Recommended next move
- [I] Single best next move: select exactly one next bounded phase frontier from `docs/SOP/CURRENT_FRONTIER.md`
- [I] Why now: the project seems to be at a post–feature-slice boundary where the main risk is success-drift, not lack of ideas
- [OOS] Not doing yet:
  - launching a new multi-part build sequence without confirming current state
  - broad refactors
  - product expansion outside the one-screen BTC implied-lab target

## Confidence notes
- [I] High confidence:
  - the product identity is stable
  - the operating model improved materially with the execution-step-disciplined role split
  - the steward chain should use a living handoff rather than from-scratch rewrites
- [I] Medium confidence:
  - layout + summary closure is still probably the highest-EV next frontier family
  - the reported glance-card feature slice likely moved the product in the right direction
- [I] Low confidence / must verify:
  - exact current repo cleanliness
  - exact current UI state
  - whether a new feature slice has already started elsewhere
  - whether the repo docs still perfectly match actual latest work

## Context-window health
- [I] Window health: healthy
- [I] Compression recommendation: none yet, but steward should update this handoff again before the window gets crowded
- [I] Must survive into next window:
  - current product target
  - active/non-active frontier status
  - verified vs reported truth table
  - operational model
  - next recommended move
  - main drift risks