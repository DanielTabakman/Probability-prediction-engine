# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v2.1 (DOCS-ONLY control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > CURRENT_FRONTIER > HANDOFF > OPERATING_RULES
- Active phase:
- Active sprint:
- Closed slices:
- Next pending execution step:
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: CURRENT_FRONTIER outranks HANDOFF if they drift (until reconciled)
- Naming rule: H1/H1-01/H1-02 is non-canonical unless explicitly reintroduced; use Phase/Sprint/Slice
- Canonical truth rule: steering truth lives in canonical docs; repo-state gate is separate

B) REPO-STATE SAFETY (reproducibility)
- Branch:
- Ahead/behind vs origin:
- Working tree: CLEAN / DIRTY
- Dirty-state classification: M-only / U-only / M+U / Index-or-merge
- Changed files by plane (CONTROL / PRODUCT / EVIDENCE):
- Untracked canonical docs present? YES/NO (canonical = docs/SOP/**):
- Mixed-plane dirty state? YES/NO:
- BUILD allowed right now? YES/NO:
- Operationally handoff-safe? YES/NO
- If NO: exact reason (one sentence):

C) AGENT CONTINUITY (required)
- Safe to switch agents? YES/NO
- Exact reason:
- If YES: exact handoff payload required:
```

**Steward workflow (role, source-of-truth order, compact vs non-compact closeout, window ledger):** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). Optional **workflow health** there may include roundtrips, raw copy-pastes, and **Cursor turnaround** (packet → usable return)—still not a pass/fail gate.

**Repo navigation (agent map):** [CODEBASE_MAP.md](CODEBASE_MAP.md) (what lives where, hot files, validation paths, helper placement hygiene).

**Workflow Metrics V1 (lightweight, cross-session):** see [WORKFLOW_METRICS_V1.md](WORKFLOW_METRICS_V1.md). Session logging uses chat commands `start session`, `break start`, `break end`, `session stop`. The assistant/steward should generate structured rows/events for the sheet at session and slice milestones. This is a lightweight convention, not a pass/fail gate.

**Implied lab — validate, smoke, artifacts, closeout:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Execution step rules (inherit from SOP)

Declare **exactly one** execution step type per session (**BUILD**, **CLOSEOUT**, **RECOVERY**, **SELECTION**) and stay inside its allowed scope. Full anti-thrash rules—CLOSEOUT vs BUILD boundary, feature slice close criteria, validation labels (deterministic / environment-sensitive / live-data-sensitive), and stop-after-two for non-BUILD—live in [OPERATING_RULES.md](OPERATING_RULES.md) under **Execution step discipline**.

**Coupled slice batching (optional):** tightly coupled slices may be batched into one **BUILD** only under the **Coupled slice batching** protocol in [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). Batched work still requires clear **per-sub-slice** reporting at review/closeout (accepted/deferred/reopened); batching is never the default.

**Closeout validation (summary):** [OPERATING_RULES.md](OPERATING_RULES.md) now defines **validation tiers** (universal vs conditional), a **closeout runtime budget** (do not let one unstable validation step dominate; stop after one or two inconclusive long runs and classify), **preflight hygiene** before smoke (clean instance, fresh port, avoid manual+smoke collision), and that **smoke C is not a universal tax**—required for classification/scenario-touched feature slices, otherwise supporting unless the spec says otherwise. Declare conditional runs in the feature slice spec / execution step when relevant.

**Runtime health (optional):** stewards may record expected vs actual **validation runtime** (pytest / smoke inside the repo) with labels **NORMAL** / **SLOW_BUT_ACCEPTABLE** / **WATCH** / **ESCALATE** ([FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md)); that is separate from **Cursor turnaround** (same doc). Operators see §4 in [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md). Signals for drift and slowness trends—not default pass/fail gates.

## Control-plane safety: doc-state vs repo-state (report separately)

This repo can appear “aligned” in docs while still being **operationally unsafe to hand off** (dirty tree, untracked files, unknown divergence vs origin). Therefore, **handoff must report two independent states**:

- **Doc-state safety (alignment)**: are canonical docs mutually consistent about phase/sprint/closed slices/next step?
- **Repo-state safety (reproducibility)**: can a new steward pull/checkout and reproduce the declared state without ambiguity?

**Canonical truth note:** `docs/SOP/CURRENT_FRONTIER.md` **outranks** this `HANDOFF.md` if they temporarily drift; treat drift as a control-plane bug and reconcile in the next docs-only pass.

## Current priority

**Execution posture (Sprint 001):**
- **Sprint 001 — Slice 005 CLOSED** = **Starter state + one obvious first move (presets)**.
- **Sprint 001 — Slice 006 CLOSED** = **Last-action meaning: plain-English “what changed?” readout** (preset-driven readout on accepted baseline).
- **Sprint 001 — Slice 007 CLOSED** = **Last-action meaning for non-preset interactions** (extend “what changed?” beyond presets; shipped on accepted baseline).
- **Sprint 001 — Slice 008 CLOSED** = **Progressive disclosure & advanced de-emphasis (instrument hierarchy)** — shipped on accepted baseline (`99a54f2` and later); bounded per `docs/SOP/SPRINT_001_PHASE_2.md` §3.

**Repo-state gate (operational; does not erase steering):** selection may be done **conceptually**, but **no BUILD** may start until the repo is **reproducible/handoff-safe** (cleanly separated deltas; no mixed dirty tree). Do **not** start BUILD from a mixed dirty tree.

## Hard rule reminders (state-transition safety)

- **No execution work directly on `main`**: all execution passes must use a short-lived branch or a worktree.
- **Single-plane passes**: each pass declares exactly one plane (CONTROL-PLANE / PRODUCT-PLANE / EVIDENCE-PLANE / RECOVERY).
- **BUILD requires preflight**: if preflight says BUILD allowed: NO, BUILD is blocked even if steering is clear.
- **No untracked canonical docs across accepted baselines**: `docs/SOP/**` must not linger untracked at a baseline that is treated as “accepted”.

## Active feature slice

**None.**

## Current status

**Post-recovery reality (minimal, operational):**

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` (use branch **tip**; verify with `git rev-parse HEAD`)
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **Sprint 001 — Slices 005–008** are **closed** on the accepted baseline (see `docs/SOP/CURRENT_FRONTIER.md`).
- **BUILD may proceed** from the clean baseline **without using parked branches** (use a fresh BUILD branch/worktree; obey preflight + single-plane rules). The parked deferred state remains **explicitly unaccepted** and does not gate baseline-based BUILD.

## Completed recently

See `docs/SOP/CURRENT_FRONTIER.md` **Completed recently** for the authoritative list. This handoff intentionally stays minimal and non-duplicative to reduce drift.

## Remaining

- next task: **SELECTION** — choose the next Sprint 001 Phase 2 BUILD target per charter/sprint spec (no BUILD target recorded in steering docs until after SELECTION; fresh branch/worktree from clean baseline when BUILD resumes; do not use parked branches).
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

**SELECTION** — pick the next Sprint 001 Phase 2 slice to execute (per `docs/SOP/PHASE_2_CHARTER.md` and `docs/SOP/SPRINT_001_PHASE_2.md`). **BUILD** resumes only after a target is selected and preflight allows it.

## Handoff checklist (must be filled each handoff)

### A) Doc-state safety / alignment (canonical docs only)

- **Active phase**:
- **Active sprint**:
- **Closed slices (Sprint 001)**:
- **Next pending execution step**:
- **Reporting posture**: **SLIM MODE** and (if applicable) **REPO-SENSOR execution-only** (no extra analysis)
- **Canonical truth rule**: confirm `CURRENT_FRONTIER` outranks `HANDOFF` if drift is detected (until reconciled)
- **Non-canonical naming note**: confirm any **H1 / H1-01 / H1-02** shorthand is treated as **non-canonical legacy** unless explicitly reintroduced by accepted docs (prefer Phase/Sprint/Slice identifiers)

### B) Repo-state safety / reproducibility (operational)

- **Branch**:
- **Ahead/behind vs `origin/<branch>`**:
- **Working tree**: **CLEAN** / **DIRTY**
- **Dirty-state classification** (choose one):
  - **M-only** (modified tracked files only)
  - **U-only** (untracked files only)
  - **M+U** (both modified + untracked)
  - **Index/merge** (staged changes, conflicts, or in-progress operations)
- **Operationally handoff-safe?** **YES/NO**
  - **YES** requires: pushed/known branch, divergence known, and a clean or intentionally-classified state that a new steward can reproduce without guessing
  - **NO** requires: state is dirty/unknown enough that a new steward could misread “what is real” vs “local leftovers”
- **If NO**: one-sentence reason (e.g., “docs aligned but `main` dirty with untracked artifacts; not reproducible from origin”)

### C) Agent continuity (required)

- **Safe to switch agents?** **YES/NO**
  - **NO** whenever live repo state still exists: stash entries; staged/uncommitted changes; partial recovery; branch/worktree divergence not explicitly parked/handed off; any incomplete execution state.
- **Exact reason:**
- **If YES: exact handoff payload required:** (minimum: branch/worktree + commit SHA, plus any named parked state and how to reproduce it)

## Baseline checkpoint (Execution step 18, 2026-04-10, RECOVERY)

Pre–feature slice 006: accepted feature slice 002–005 work, full `tests/`, `scripts/run_implied_lab_ui_smoke.py`, and `docs/SOP/` (including Execution step 17 validation-tier / closeout rules in `OPERATING_RULES.md`) are present on disk but **mostly not committed**; `main` is **ahead of `origin/main` by 1** (local commit: implied-lab smoke harness + doc/requirements). **Modified** tracked files carry large deltas on top of that commit. **`python -m pytest -q`:** 28 passed on this tree (2026-04-10). Smallest honest next step before feature slice 006: one scoped checkpoint (commit + push) after deciding whether `artifacts/` (and similar) should be ignored or archived—not broad cleanup.

## Last updated

2026-04-16 by agent (**DOCS-ONLY** — steering aligned: **Sprint 001 — Slice 008** **closed/shipped** on accepted baseline; recommended next step **SELECTION**). Prior same day: SELECTION recorded Slice 008 as next BUILD target (superseded by shipped baseline). Prior: 2026-04-11 by agent (CLOSEOUT — feature slice 009 closed; operator runbook + discoverability; recommended next step SELECTION). Same day: runtime health indicators (steward protocol + runbook + this handoff). Earlier: legacy Phase 1 feature slice 008 closeout (pytest 36 + smoke A `20260411_131344`); 2026-04-10 — feature slice 007/006/005 closeouts; Execution step 18 RECOVERY baseline; Execution step 17 validation tiers.
