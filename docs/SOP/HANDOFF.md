# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v2.1 (DOCS-ONLY control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > CURRENT_FRONTIER > HANDOFF > OPERATING_RULES
- Active phase: Phase 2 — Desirability / Playability / UX (`docs/SOP/PHASE_2_CHARTER.md`)
- Active sprint: Sprint 002 (`docs/SOP/SPRINT_002_PHASE_2.md`)
- Closed slices: Sprint 001 — Slices 005–011 (wrap **outcome B**); **Sprint002-Slice001** (product **`ff40b48`**); **Sprint002-Slice002** (product **`bd12b7c`**); no slice in-flight under **BUILD** until **SELECTION** names one
- Next pending execution step: **SELECTION** — next bounded Sprint 002 slice (`docs/SOP/CURRENT_FRONTIER.md`; map **`docs/SOP/SPRINT_002_PHASE_2.md` §6**)
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: CURRENT_FRONTIER outranks HANDOFF if they drift (until reconciled)
- Naming rule: H1/H1-01/H1-02 is non-canonical unless explicitly reintroduced; use Phase/Sprint/Slice
- Canonical truth rule: steering truth lives in canonical docs; repo-state gate is separate

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify at session start (`git rev-parse --abbrev-ref HEAD`; expected baseline `recovery/frontier-steward-v2_1-baseline` unless steward moved it)
- Ahead/behind vs origin: verify at session start (`git rev-list --left-right --count origin/<branch>...HEAD`)
- Working tree: verify at session start (CLEAN required before BUILD)
- Dirty-state classification: M-only / U-only / M+U / Index-or-merge (record actual)
- Changed files by plane (CONTROL / PRODUCT / EVIDENCE): record actual next pass
- Untracked canonical docs present? YES/NO (canonical = docs/SOP/**): verify; must be NO before accepted baseline
- Mixed-plane dirty state? YES/NO: verify
- BUILD allowed right now? YES/NO: YES only if preflight + clean tree + CONTROL/PRODUCT plane discipline satisfied
- Operationally handoff-safe? YES/NO: verify
- If NO: exact reason (one sentence):

C) AGENT CONTINUITY (required)
- Safe to switch agents? YES/NO: verify after repo-state
- Exact reason:
- If YES: exact handoff payload required: branch + HEAD SHA + read `docs/SOP/CURRENT_FRONTIER.md` + `docs/SOP/SPRINT_002_PHASE_2.md` §6 (map) / §7 (Slice001) / §8 (Slice002 closed)
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

**Execution posture (Sprint 002 — post–Slice002 CLOSEOUT):**
- **Sprint002-Slice001** — **CLOSED / shipped** (product **`ff40b48`**); evidence: `CURRENT_FRONTIER.md` **Steering continuity** + **Completed recently**.
- **Sprint002-Slice002** — **CLOSED / shipped** (product **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`**); evidence: `CURRENT_FRONTIER.md` **Completed recently**; smoke `artifacts/ui_smoke/20260418_163043/`.
- **Next execution step:** **SELECTION** — next bounded Sprint 002 slice (map **§6.B** = candidates only).

**Execution posture (Sprint 001 — WRAP / archive):**
- **Sprint 001 — Slice 005 CLOSED** = **Starter state + one obvious first move (presets)**.
- **Sprint 001 — Slice 006 CLOSED** = **Last-action meaning: plain-English “what changed?” readout** (preset-driven readout on accepted baseline).
- **Sprint 001 — Slice 007 CLOSED** = **Last-action meaning for non-preset interactions** (extend “what changed?” beyond presets; shipped on accepted baseline).
- **Sprint 001 — Slice 008 CLOSED** = **Progressive disclosure & advanced de-emphasis (instrument hierarchy)** — shipped on accepted baseline (`99a54f2` and later); bounded per `docs/SOP/SPRINT_001_PHASE_2.md` §3.
- **Sprint 001 — Slice 009 CLOSED** = repeat-play / follow-on interaction quality within the Phase 2 primary loop — shipped/closed on accepted baseline.
- **Sprint 001 — Slice 010 CLOSED** = extend “What changed” to belief + target-payoff — shipped/closed on accepted baseline.
- **Sprint 001 — Slice 011 CLOSED** = guided **“Try next”** one-click affordances (repeat-play; reuses existing presets/meaning readout) — shipped/closed on accepted baseline (`29df0069cbbd14fdb96a8bfdda9c4b46329d7cea`).
- **Control-plane (2026-04-17):** **Sprint 001 primary loop** (`docs/SOP/SPRINT_001_PHASE_2.md` §2) is **complete** — demo coherence checklist vs `docs/SOP/PHASE_2_CHARTER.md` §9 + sprint §5 **passes** on the shipped loop; **outcome B** (no chartered **Slice 012**). Verified baseline **tip:** run `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline` (must include control-plane wrap for **outcome B**); demo-coherence review anchor: `c51a4b4985f586b64264d63715af61e17f66358d`.

**Repo-state gate (operational; does not erase steering):** selection may be done **conceptually**, but **no BUILD** may start until the repo is **reproducible/handoff-safe** (cleanly separated deltas; no mixed dirty tree). Do **not** start BUILD from a mixed dirty tree.

## Hard rule reminders (state-transition safety)

- **No execution work directly on `main`**: all execution passes must use a short-lived branch or a worktree.
- **Single-plane passes**: each pass declares exactly one plane (CONTROL-PLANE / PRODUCT-PLANE / EVIDENCE-PLANE / RECOVERY).
- **BUILD requires preflight**: if preflight says BUILD allowed: NO, BUILD is blocked even if steering is clear.
- **No untracked canonical docs across accepted baselines**: `docs/SOP/**` must not linger untracked at a baseline that is treated as “accepted”.

## Active feature slice

**None (BUILD-selected).** **Sprint002-Slice001** and **Sprint002-Slice002** are **closed/shipped** (see `docs/SOP/CURRENT_FRONTIER.md`). **Sprint 001** remains **wrapped** (**Slices 005–011** closed; no **Slice 012**).

## Current status

**Post-recovery reality (minimal, operational):**

- **Clean control-plane baseline:** `recovery/frontier-steward-v2_1-baseline` (use branch **tip**; verify with `git rev-parse HEAD`)
- **Parked deferred mixed state (explicitly unaccepted):** `parked/deferred-mixed-stash0` @ `3983870`
- **Sprint 001 — Slices 005–011** are **closed** on the accepted baseline (see `docs/SOP/CURRENT_FRONTIER.md`); **Sprint 001 primary loop** is **wrapped** (**outcome B**, 2026-04-17).
- **Sprint002-Slice001** is **closed/shipped** (product **`ff40b48`**).
- **Sprint002-Slice002** is **closed/shipped** (product **`bd12b7c`**; baseline **tip** verifies with `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline`).
- **BUILD may proceed** from the clean baseline **without using parked branches** (use a fresh BUILD branch/worktree; obey preflight + single-plane rules) **after** **SELECTION** names the next slice. The parked deferred state remains **explicitly unaccepted** and does not gate baseline-based BUILD.

## Completed recently

See `docs/SOP/CURRENT_FRONTIER.md` **Completed recently** for the authoritative list. This handoff intentionally stays minimal and non-duplicative to reduce drift.

## Remaining

- next task: **SELECTION** — next bounded Sprint 002 slice (`docs/SOP/CURRENT_FRONTIER.md`; candidates `docs/SOP/SPRINT_002_PHASE_2.md` **§6.B**).
- deferred: **Sprint002-Slice003** (vocabulary / “What changed?” alignment) and **§6.C** batch candidates — only after explicit **SELECTION** (or steward re-order); map is not auto-charter.
- optional: steward demo script (docs-only) if validation thrash warrants it — not selected by default.

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
   Last known result: **PASS** (2026-04-18 — `artifacts/ui_smoke/20260418_163043/`; **Sprint002-Slice002** closeout on baseline tip **`bd12b7c`**)

3. **Local app launch**  
   `python -m streamlit run src/viz/app.py --server.headless true --server.port 8515`  
   Readiness check: confirm HTTP 200 from `http://127.0.0.1:8515/` and/or Streamlit log message showing local URL

4. **Local visual inspection**  
   Open `http://localhost:8515` locally after readiness. Confirm headings, sidebar controls, and changed UI region. Perform one safe non-destructive interaction when practical.

## Needs human attention

- issue:
- why escalation is needed:

## Recommended next step

**SELECTION** — next bounded slice under **Sprint 002** (`docs/SOP/SPRINT_002_PHASE_2.md` §6). **Sprint002-Slice001–002** are **closed**; **Sprint 001** remains **wrapped** (`docs/SOP/CURRENT_FRONTIER.md`).

## Handoff checklist (must be filled each handoff)

### A) Doc-state safety / alignment (canonical docs only)

- **Active phase**: Phase 2 — Desirability / Playability / UX (`docs/SOP/PHASE_2_CHARTER.md`)
- **Active sprint**: Sprint 002 (`docs/SOP/SPRINT_002_PHASE_2.md`)
- **Closed slices (Sprint 001)**: 005–011 (wrap **outcome B**; no Slice 012). **Sprint002-Slice001** — **closed/shipped** (product **`ff40b48`**). **Sprint002-Slice002** — **closed/shipped** (product **`bd12b7c`**)
- **Next pending execution step**: **SELECTION** — next Sprint 002 slice boundary
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

2026-04-18 by agent (**CONTROL-PLANE CLOSEOUT — Frontier Steward 2.2**): **Sprint002-Slice002** **closed/shipped** (`bd12b7c`); **next** = **SELECTION**. **No product code** in this pass. Prior same day: BUILD + promotion Slice002; Slice001 closeout; Slice002 SELECTION charter.
