# HANDOFF

Purpose: minimum context needed for the next work session.

## Transaction rules (inherit from SOP)

Declare **exactly one** transaction type per session (**BUILD**, **CLOSEOUT**, **RECOVERY**, **SELECTION**) and stay inside its allowed scope. Full anti-thrash rules—CLOSEOUT vs BUILD boundary, sprint close criteria, validation labels (deterministic / environment-sensitive / live-data-sensitive), and stop-after-two for non-BUILD—live in [OPERATING_RULES.md](OPERATING_RULES.md) under **Transaction discipline**.

**Closeout validation (summary):** [OPERATING_RULES.md](OPERATING_RULES.md) now defines **validation tiers** (universal vs conditional), a **closeout runtime budget** (do not let one unstable validation step dominate; stop after one or two inconclusive long runs and classify), **preflight hygiene** before smoke (clean instance, fresh port, avoid manual+smoke collision), and that **smoke C is not a universal tax**—required for classification/scenario-touched sprints, otherwise supporting unless the spec says otherwise. Declare conditional runs in the sprint/transaction when relevant.

## Current priority

Select the next bounded Sprint 1 frontier from `docs/SOP/CURRENT_FRONTIER.md` after Sprint 006 closure.

## Active sprint

**None.** Sprint 006 closed (Transaction 22, 2026-04-10).

## Current status

The repo can run unit tests, the primary UI smoke script, and the actual Streamlit app locally. **Sprint 006 is formally closed** (Transaction 22, 2026-04-10): `python -m pytest -q` **PASS** (**35** tests); `python scripts/run_implied_lab_ui_smoke.py` **PASS** — manifest `artifacts/ui_smoke/20260410_171958/ui_smoke_manifest.json`. **Smoke C** not rerun for Sprint 006 (presentation-only; per OPERATING_RULES validation tiers). **Trust strip visibility:** compact **Trust / provenance** sits under **Summary** above **Decision-ready review**; primary smoke **A** still scrolls into expanded **Verification** before screenshot — use a local scroll or ad-hoc capture to pixel-check the strip (see `docs/IMPLIED_LAB_SMOKE.md` note). Prior **Sprint 005** closeout notes (smoke C fail on that window) remain historical in `CURRENT_FRONTIER.md`. UI smokes remain **live-data-sensitive** / **environment-sensitive** if Deribit/Yahoo are down or local processes collide.

## Completed recently

- **closed:** **Sprint 006 — Trust / provenance strip** (`build_trust_strip_lines`, `app.py` `right_trust_slot`, `tests/test_trust_strip.py`). **Closeout (Transaction 22):** pytest **PASS**; smoke A **PASS** (manifest above).
- **closed:** **Sprint 005 — Decision-ready trade review** (`decision_ready_review.py`, right-column block between Summary and glance, `tests/test_decision_ready_review.py`). **Closeout (Transaction 16):** pytest **PASS**; smoke A **PASS** (`artifacts/ui_smoke/20260410_153957/ui_smoke_manifest.json`); smoke C **FAIL** on that rerun — see `CURRENT_FRONTIER.md`.
- **closed:** **Sprint 004 — Main disagreement digest & fit-family linkage** (`build_disagreement_scan_payload`, glance UI reorder, audit expander, tests). **Closeout (Transaction 13):** `python -m pytest -q` **PASS** (21 tests). `python scripts/run_implied_lab_ui_smoke.py` **PASS** — manifest `artifacts/ui_smoke/20260410_145441/ui_smoke_manifest.json`. `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>` **PASS** — manifest `artifacts/ui_smoke/20260410_150352/ui_smoke_manifest.json`. (One earlier headless **C** attempt in the same session hung until stale Python processes were cleared; second run **PASS** — classify hang as **environment-sensitive**, not product regression.)
- completed: **Sprint 003 — Belief uncertainty capture (±% move (1σ) input mode + σ_ln mapping + tests)**
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
   Last known result: passed (2026-04-10 — `artifacts/ui_smoke/20260410_171958/`)

3. **Local app launch**  
   `python -m streamlit run src/viz/app.py --server.headless true --server.port 8515`  
   Readiness check: confirm HTTP 200 from `http://127.0.0.1:8515/` and/or Streamlit log message showing local URL

4. **Local visual inspection**  
   Open `http://localhost:8515` locally after readiness. Confirm headings, sidebar controls, and changed UI region. Perform one safe non-destructive interaction when practical.

## Needs human attention

- issue:
- why escalation is needed:

## Recommended next step

Create Sprint 001 and include both automated validation and launch-and-inspect validation for any user-visible change.

## Baseline checkpoint (Transaction 18, 2026-04-10, RECOVERY)

Pre–Sprint 006: accepted Sprint 002–005 work, full `tests/`, `scripts/run_implied_lab_ui_smoke.py`, and `docs/SOP/` (including Transaction 17 validation-tier / closeout rules in `OPERATING_RULES.md`) are present on disk but **mostly not committed**; `main` is **ahead of `origin/main` by 1** (local commit: implied-lab smoke harness + doc/requirements). **Modified** tracked files carry large deltas on top of that commit. **`python -m pytest -q`:** 28 passed on this tree (2026-04-10). Smallest honest next step before Sprint 006: one scoped checkpoint (commit + push) after deciding whether `artifacts/` (and similar) should be ignored or archived—not broad cleanup.

## Last updated

2026-04-10 by agent (Transaction 22 — Sprint 006 closed; pytest 35 passed + smoke A green; Transaction 18 — RECOVERY baseline; Transaction 17 — validation tiers; Transaction 16 — Sprint 005 closed)
