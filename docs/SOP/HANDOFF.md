# HANDOFF

Purpose: minimum context needed for the next work session.

**Steward workflow (role, source-of-truth order, compact vs non-compact closeout, window ledger):** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). Optional **workflow health** there may include roundtrips, raw copy-pastes, and **Cursor turnaround** (packet → usable return)—still not a pass/fail gate.

**Implied lab — validate, smoke, artifacts, closeout:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Execution step rules (inherit from SOP)

Declare **exactly one** execution step type per session (**BUILD**, **CLOSEOUT**, **RECOVERY**, **SELECTION**) and stay inside its allowed scope. Full anti-thrash rules—CLOSEOUT vs BUILD boundary, feature slice close criteria, validation labels (deterministic / environment-sensitive / live-data-sensitive), and stop-after-two for non-BUILD—live in [OPERATING_RULES.md](OPERATING_RULES.md) under **Execution step discipline**.

**Closeout validation (summary):** [OPERATING_RULES.md](OPERATING_RULES.md) now defines **validation tiers** (universal vs conditional), a **closeout runtime budget** (do not let one unstable validation step dominate; stop after one or two inconclusive long runs and classify), **preflight hygiene** before smoke (clean instance, fresh port, avoid manual+smoke collision), and that **smoke C is not a universal tax**—required for classification/scenario-touched feature slices, otherwise supporting unless the spec says otherwise. Declare conditional runs in the feature slice spec / execution step when relevant.

**Runtime health (optional):** stewards may record expected vs actual **validation runtime** (pytest / smoke inside the repo) with labels **NORMAL** / **SLOW_BUT_ACCEPTABLE** / **WATCH** / **ESCALATE** ([FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md)); that is separate from **Cursor turnaround** (same doc). Operators see §4 in [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md). Signals for drift and slowness trends—not default pass/fail gates.

## Current priority

**SELECTION** — pick the next bounded feature slice from `docs/SOP/CURRENT_FRONTIER.md` (one-screen implied lab phase). **No active slice** after feature slice **009** closure.

## Active feature slice

**None.** Feature slice **009** (Implied lab operator runbook) closed (CLOSEOUT, 2026-04-11, docs-only). Prior: feature slice **008** closed (2026-04-11); feature slice **007** closed (2026-04-10).

## Current status

The repo can run unit tests, the primary UI smoke script, and the actual Streamlit app locally. **Feature slice 009** added the canonical implied lab operator runbook: [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md) (preflight, Tier 1 vs smoke **C**, artifacts, caveats, closeout checklist). **Validation for 009:** documentation review only—no code changes.

**Feature slice 008 (Glance-first orientation polish) remains closed** (2026-04-11): `python -m pytest -q` **PASS** (**36** tests); `python scripts/run_implied_lab_ui_smoke.py` **PASS** — manifest `artifacts/ui_smoke/20260411_131344/ui_smoke_manifest.json`; screenshot `artifacts/ui_smoke/20260411_131344/A_width_target_payoff.png` (`trade_ticket_found` **true**). **Smoke C** not required (presentation-only slice). **BUILD caveats (recorded in `CURRENT_FRONTIER.md`):** false expander-label match fixed before acceptance; one smoke run timed out (likely network/Deribit) before the passing run.

**Feature slice 007** remains closed: flatter **Trade ticket** path after glance; **Decision-ready review** linkage; default smoke **A** `full_page=False` may still omit glance/ticket in the PNG — scroll or ad-hoc capture (`docs/IMPLIED_LAB_SMOKE.md`). **Trust strip** and feature slice **005** smoke **C** caveats unchanged in `CURRENT_FRONTIER.md`. UI smokes remain **live-data-sensitive** / **environment-sensitive** when Deribit/Yahoo fail or processes collide.

## Completed recently

- **closed:** **Feature slice 009 — Implied lab operator runbook** (`docs/SOP/IMPLIED_LAB_OPERATOR_RUNBOOK.md`; HANDOFF + CURRENT_FRONTIER updates; cross-links). **Closeout (2026-04-11):** docs-only consistency review.
- **closed:** **Feature slice 008 — Glance-first orientation polish** (`src/viz/app.py` only; layout/copy/hierarchy). **Closeout (2026-04-11):** pytest **36** passed; smoke A **PASS** (`artifacts/ui_smoke/20260411_131344/`).
- **closed:** **Feature slice 007 — Flatter trade ticket path** (`app.py` `right_ticket_slot`, `_implied_lab_trade_ticket_code_text`, `_render_implied_lab_trade_ticket_panel`; `decision_ready_review.py` linkage copy; `tests/test_implied_lab_trade_ticket.py` + updated `tests/test_decision_ready_review.py`). **Closeout (Execution step 27):** pytest **PASS**; smoke A **PASS** (`artifacts/ui_smoke/20260410_180727/ui_smoke_manifest.json`).
- **closed:** **Feature slice 006 — Trust / provenance strip** (`build_trust_strip_lines`, `app.py` `right_trust_slot`, `tests/test_trust_strip.py`). **Closeout (Execution step 22):** pytest **PASS**; smoke A **PASS** (`artifacts/ui_smoke/20260410_171958/ui_smoke_manifest.json`).
- **closed:** **Feature slice 005 — Decision-ready trade review** (`decision_ready_review.py`, right-column block between Summary and glance, `tests/test_decision_ready_review.py`). **Closeout (Execution step 16):** pytest **PASS**; smoke A **PASS** (`artifacts/ui_smoke/20260410_153957/ui_smoke_manifest.json`); smoke C **FAIL** on that rerun — see `CURRENT_FRONTIER.md`.
- **closed:** **Feature slice 004 — Main disagreement digest & fit-family linkage** (`build_disagreement_scan_payload`, glance UI reorder, audit expander, tests). **Closeout (Execution step 13):** `python -m pytest -q` **PASS** (21 tests). `python scripts/run_implied_lab_ui_smoke.py` **PASS** — manifest `artifacts/ui_smoke/20260410_145441/ui_smoke_manifest.json`. `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>` **PASS** — manifest `artifacts/ui_smoke/20260410_150352/ui_smoke_manifest.json`. (One earlier headless **C** attempt in the same session hung until stale Python processes were cleared; second run **PASS** — classify hang as **environment-sensitive**, not product regression.)
- completed: **Feature slice 003 — Belief uncertainty capture (±% move (1σ) input mode + σ_ln mapping + tests)**
- verified: `python -m pytest -q` is green; prior green evidence exists for UI smoke A and C (may flap when data unavailable).
- cleanup done:

## Remaining

- next task:
- deferred:
- optional:

## Risks / watchouts

- `streamlit` may not be on PATH; prefer `python -m streamlit`.
- Remote browser/fetch tools may not reach localhost in isolated environments.
- Chart/main visualization may need longer wait or scroll before treating it as verified.
- Playwright/Chromium, dependencies, network access, and free ports may still matter.
- **Live-data smoke flakiness:** if spot/quotes are unavailable, the app can show **"Need BTC spot price for implied distribution"** and the implied-lab belief UI may not mount; treat smoke failures in that state as **operational/data availability** until reproduced with data available.

## Most relevant files

- path:
- role:

## Most relevant tests/checks

1. **Unit tests**  
   `python -m unittest discover -s tests -p "test_*.py" -v`  
   Last known result: passed

2. **Primary automated UI smoke**  
   `python scripts/run_implied_lab_ui_smoke.py`  
   Last known result: passed (2026-04-11 — `artifacts/ui_smoke/20260411_131344/`; feature slice **008** closeout)

3. **Local app launch**  
   `python -m streamlit run src/viz/app.py --server.headless true --server.port 8515`  
   Readiness check: confirm HTTP 200 from `http://127.0.0.1:8515/` and/or Streamlit log message showing local URL

4. **Local visual inspection**  
   Open `http://localhost:8515` locally after readiness. Confirm headings, sidebar controls, and changed UI region. Perform one safe non-destructive interaction when practical.

## Needs human attention

- issue:
- why escalation is needed:

## Recommended next step

**SELECTION** — choose exactly one next bounded feature slice from `docs/SOP/CURRENT_FRONTIER.md` under the current one-screen implied lab phase (no slice is pre-selected here).

## Baseline checkpoint (Execution step 18, 2026-04-10, RECOVERY)

Pre–feature slice 006: accepted feature slice 002–005 work, full `tests/`, `scripts/run_implied_lab_ui_smoke.py`, and `docs/SOP/` (including Execution step 17 validation-tier / closeout rules in `OPERATING_RULES.md`) are present on disk but **mostly not committed**; `main` is **ahead of `origin/main` by 1** (local commit: implied-lab smoke harness + doc/requirements). **Modified** tracked files carry large deltas on top of that commit. **`python -m pytest -q`:** 28 passed on this tree (2026-04-10). Smallest honest next step before feature slice 006: one scoped checkpoint (commit + push) after deciding whether `artifacts/` (and similar) should be ignored or archived—not broad cleanup.

## Last updated

2026-04-11 by agent (CLOSEOUT — feature slice 009 closed; operator runbook + discoverability; recommended next step SELECTION). Same day: runtime health indicators (steward protocol + runbook + this handoff). Earlier: feature slice 008 closeout (pytest 36 + smoke A `20260411_131344`); 2026-04-10 — feature slice 007/006/005 closeouts; Execution step 18 RECOVERY baseline; Execution step 17 validation tiers.
