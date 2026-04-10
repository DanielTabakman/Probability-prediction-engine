# MANAGER_KICKOFF

Single-use orientation for the agent acting as **manager** in this repo. You are **not** executing sprints yourself unless you choose to; your job is to steer, document, review evidence, and delegate when appropriate.

## Role

You **own**:

- **Direction** — what “done” means for the current phase vs `ORIGINAL_SPEC.md`
- **Frontier updates** — keep `CURRENT_FRONTIER.md` accurate after each meaningful pass
- **Sprint creation/approval** — name the sprint, scope, acceptance, test plan (`SPRINT_TEMPLATE.md`)
- **Evidence review** — read worker closeouts; rerun checks only when evidence is thin or something fails
- **Stop/escalate decisions** — halt or escalate to a human on real risk, not on pace

You **do not** need to personally implement the sprint. Delegating execution to a worker is appropriate when the sprint is clear and acceptance is defined.

## Current operating mode

- **Move fast inside the current frontier** — prefer meaningful, testable chunks over micro-steps for their own sake.
- **Push care downstream** — tests, app launch/inspection, cleanup, and structured evidence are the safety system.
- **Interrupt less** — trust a fuller worker pass when the objective and verification path are clear (`MANAGER_LOOP.md`, `WORKER_LOOP.md`).
- **Git stays conservative** — no commit, push, or branch unless explicitly requested (`OPERATING_RULES.md`).

## Source of truth

Read and use these in **priority order**:

1. `docs/SOP/ORIGINAL_SPEC.md` — stable product intent for this cycle
2. `docs/SOP/CURRENT_FRONTIER.md` — phase, goals, candidates, avoid/stop
3. `docs/SOP/HANDOFF.md` — session context, commands, last-known verification
4. `docs/SOP/OPERATING_RULES.md` — workflow, posture, cleanup, escalation
5. `docs/SOP/WORKER_LOOP.md` — worker boundaries and required closeout
6. `docs/SOP/SPRINT_TEMPLATE.md` — shape of `SPRINT_00X.md`

Use `docs/SPRINT_1_SPEC.md`, `docs/SEMANTIC_CONTRACTS.md`, and `docs/IMPLIED_LAB_SMOKE.md` when the sprint touches the implied lab or copy/semantics.

## Immediate task

1. Read the control docs above (at minimum: `ORIGINAL_SPEC`, `CURRENT_FRONTIER`, `HANDOFF`, `OPERATING_RULES`, `WORKER_LOOP`, `SPRINT_TEMPLATE`).
2. Determine whether a sprint is **already active**: an existing `docs/SOP/SPRINT_*.md` **other than** `SPRINT_TEMPLATE.md`, and/or `HANDOFF.md` filled with a real sprint ID/title (not the placeholder line).
3. If **no** sprint is active, pick the best next sprint from `CURRENT_FRONTIER.md` (see **Current sprint options** below).
4. Create `docs/SOP/SPRINT_001.md` using `SPRINT_TEMPLATE.md` — or the **next free** `SPRINT_00X` ID if `001` already exists.
5. Delegate execution to a worker when appropriate; paste or point to the sprint file and `HANDOFF.md` test commands.
6. On return, **require real evidence** before updating the frontier or starting the next sprint (see **Evidence required**).

## Delegation rule

- Delegate **implementation** when the sprint objective, scope boundaries, and test plan are clear.
- **You** keep **direction** and **acceptance**; do not let the worker redefine roadmap or phase goals.
- Workers may **propose** `CURRENT_FRONTIER.md` updates; **you** decide what lands.
- Workers must **not** chain into the next sprint without your explicit next sprint (`WORKER_LOOP.md`).

## Evidence required from worker

The closeout must include:

- objective  
- files changed  
- what changed  
- **exact commands run**  
- tests run and **results**  
- app launch/inspection notes **when UI/relevant**  
- what was **confirmed** vs what remains **unverified**  
- cleanup performed  
- risks / caveats  
- proposed next sprint options  

(`WORKER_LOOP.md` + `OPERATING_RULES.md` align with this.)

## Stop / escalate rules

Stop and escalate (human or reset plan) if:

- tests fail and **cannot** be repaired cleanly in-scope  
- verification is **weak or contradictory**  
- the work starts needing **structural rewrite** behavior beyond the sprint  
- **repo hygiene** is degrading (duplicate truth, incoherent patterns)  
- convergence to `ORIGINAL_SPEC.md` is **no longer clear**  
- **multiple** next sprints are similarly plausible and **direction is uncertain**

Do **not** stop solely because the diff was large if evidence shows acceptance was met and the repo stayed coherent (`MANAGER_LOOP.md`).

## Current project state

- **Aggressive / fast mode** is documented in SOP: bigger testable passes inside the frontier, fewer artificial micro-gates.  
- **Manager/worker split** is defined in `MANAGER_LOOP.md` and `WORKER_LOOP.md`.  
- **`ORIGINAL_SPEC.md`** and **`CURRENT_FRONTIER.md`** are filled in (not placeholders).  
- **No sprint file** exists under `docs/SOP/` yet except `SPRINT_TEMPLATE.md`. **`HANDOFF.md`** still has a placeholder under **Active sprint**; **`CURRENT_FRONTIER.md`** states **no sprint active** — treat as **no formal sprint** until you create `SPRINT_001.md` (or next ID) and align handoff.  
- **Validation paths** are already documented in `HANDOFF.md`: unit tests, `python scripts/run_implied_lab_ui_smoke.py`, headless Streamlit readiness, local visual inspection; details in `docs/IMPLIED_LAB_SMOKE.md`.

## Current sprint options

Derived from `CURRENT_FRONTIER.md` **Next best sprint candidates** (reframed as risk levels).

### Bold option

| Field | Content |
|--------|---------|
| **Title** | Sprint 1 closure: layout + centralized lab state |
| **Objective** | Deliver frontier candidates **1 + 2** in one sprint: Sprint 1 layout & summary closure **and** a single session/state layer driving chart, summary, and controls (`docs/SPRINT_1_SPEC.md` layout + technical principle). |
| **Why it matters** | Maximum progress toward phase success in one verification cycle; reduces repeated UI passes. |
| **Likely files** | `src/viz/app.py`, `src/viz/implied_lab_*.py`, related viz modules touched by wiring; `tests/test_*.py` as needed. |
| **Required validation** | `python -m unittest discover -s tests -p "test_*.py" -v`; `python scripts/run_implied_lab_ui_smoke.py`; Streamlit launch + `docs/IMPLIED_LAB_SMOKE.md` checklist for changed UI. |
| **Main risk** | Streamlit session state and widget coupling — regressions if state ownership is unclear; larger blast radius. |

### Medium-risk option

| Field | Content |
|--------|---------|
| **Title** | Belief / disagreement UX + test hardening |
| **Objective** | Frontier candidate **3**: align hints, thresholds, and related UI copy with `docs/SEMANTIC_CONTRACTS.md`; extend focused unit tests; run gated smoke `C_directional_peak_disagreement` when that path is touched. |
| **Why it matters** | Reduces semantic drift and user-visible “wrong story” bugs without a full layout rewrite. |
| **Likely files** | `src/viz/belief_disagreement_hints.py`, `src/viz/disagreement_thresholds.py`, targeted `src/viz/app.py` sections, `tests/test_belief_disagreement_hints.py`. |
| **Required validation** | Unit tests above; primary smoke **A** always; scenario **C** when applicable per `docs/IMPLIED_LAB_SMOKE.md`; spot-check copy in running app. |
| **Main risk** | Copy and multi-module behavior — mistakes show up as misleading UX; external/network deps for full smoke. |

### Safe option

| Field | Content |
|--------|---------|
| **Title** | Sprint 1 layout & summary closure (no state centralization sprint) |
| **Objective** | Frontier candidate **1 only**: chart near top, two-column layout, summary fields, expanders for advanced math — **without** taking on the full “one state layer” refactor in the same sprint. |
| **Why it matters** | Highly visible progress toward Sprint 1 spec with smaller session-state risk than the bold combo. |
| **Likely files** | `src/viz/app.py`, tightly related viz helpers only as needed for layout/summary. |
| **Required validation** | Same as bold for tests/smoke/manual checklist relevant to layout/summary. |
| **Main risk** | May leave duplicate/widget-driven logic in place — acceptable if explicitly **scope-out** centralization for this sprint; follow-up sprint may still be needed for candidate 2. |

## Manager instruction block

1. Read the control docs (source-of-truth list).  
2. Confirm sprint status; if none, **pick** bold, medium, or safe (or a clearly scoped subset) and **create** `docs/SOP/SPRINT_001.md` from `SPRINT_TEMPLATE.md`.  
3. **Delegate** implementation when appropriate; require the **evidence** list on return.  
4. **Review** evidence — rerun checks only if needed.  
5. **Update** `CURRENT_FRONTIER.md` and `HANDOFF.md` to match reality.  
6. **Continue** with the next sprint, **request fixes**, or **stop/escalate** per the rules above.
