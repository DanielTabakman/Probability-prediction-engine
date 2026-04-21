# Sprint 003 — Phase 2 — Pilot-driven evidence-plane hardening (relay-assisted)

**What this file is:** the **Sprint 003 spec** (scope + acceptance + slice map) for Phase 2. Deliberately **narrow**: this sprint exists to carry **tiny, pilot-evidence-driven evidence-plane hardening slices** executed via `docs/SOP/RELAY_RUNTIME_V0.md`. It is **not** a Phase 2 **product UX** sprint; it does not advance the Phase 2 product charter's desirability/playability acceptance.

**Execution status (ledger lives elsewhere):** the **current selected slice**, BUILD/CLOSEOUT state, and the **next pending execution step** are authoritative in `docs/SOP/CURRENT_FRONTIER.md` (and summarized in `docs/SOP/HANDOFF.md`).

**Parent charter:** `docs/SOP/PHASE_2_CHARTER.md` (Phase 2 remains active; this sprint does **not** supersede the charter and does **not** reopen Sprint 001 or Sprint 002).
**Prior sprints (wrapped, do not reopen by default):** `docs/SOP/SPRINT_001_PHASE_2.md`, `docs/SOP/SPRINT_002_PHASE_2.md`
**Runtime anchor:** `docs/SOP/RELAY_RUNTIME_V0.md` (local, single-run, staged relay; pilots complete — read-only, staged/manual-resume, forensic-replay)
**Job registry anchor:** `docs/SOP/JOB_REGISTRY_V1.md`
**Autonomy anchor:** `docs/SOP/CODEX_AUTONOMY_V1.md` (authority boundary = **PREFLIGHT → BUILD → bounded REPAIR → BUILD-CLOSEOUT → PROMOTION** for **one** already-SELECTED slice; **SELECTION** and **CONTROL-CLOSEOUT** remain steward-only)

---

## 1. Title

**Pilot-driven evidence-plane hardening (relay-assisted)**

## 2. Purpose

Use the now-ready Relay Runtime V0 for its **first real governed slice**: a **tiny, pilot-evidence-driven hardening** of the `control_plane_consistency_check` job so that known **SOP template placeholders** (`SPRINT_00X.md`, `SPRINT_00X_PHASE_Y.md`) do not generate noise warnings that dilute the tool's ability to surface **real** control-plane drift.

This sprint is the **first real relay-assisted execution** following Relay Runtime V0's three local pilots:
- read-only pilot (passed),
- staged/manual-resume pilot (passed),
- forensic-replay pilot (passed).

The sprint is **deliberately narrow**:
- **evidence-plane only** (the relay tool itself and its tests),
- **pilot-grounded** (every slice must cite a specific relay/health finding),
- **no product exposure** (zero `src/viz/**` touch),
- **no control-plane doc churn** (zero writes under `docs/SOP/**` or `docs/CONTROL_PLANE/**` from BUILD; control-plane updates happen only at steward CONTROL-CLOSEOUT and are recorded here and in `CURRENT_FRONTIER.md`).

## 3. Acceptance criteria (sprint-level)

A Sprint 003 slice is acceptable only if **all** hold:

1. The slice targets an **evidence-plane** artifact (typically `scripts/relay_runtime_v0.py` and/or `tests/test_relay_runtime_v0.py`), `declared_plane == EVIDENCE-PLANE` per `CODEX_AUTONOMY_V1` §14.1, and `§14.3` invariant `declared_plane_matches_actual` holds.
2. The slice is **pilot-grounded**: it cites a specific finding from a previous relay run (read-only pilot, staged pilot, forensic-replay pilot, `codebase_health_report`, or `control_plane_consistency_check`).
3. The slice **does not** edit anything under `docs/SOP/**`, `docs/CONTROL_PLANE/**`, or `orchestrator/`, and **does not** modify `docs/SOP/CODEX_AUTONOMY_V1.md`, `docs/SOP/JOB_REGISTRY_V1.md`, or `docs/SOP/RELAY_RUNTIME_V0.md`.
4. The slice **does not** touch `src/viz/**` or any product-plane code.
5. After BUILD, `python -m pytest -q` on baseline passes with **zero regressions** relative to the pre-BUILD run.
6. Any observed **behavior change** of a relay job is expressible as a **narrow, explicit rule** (not a wide regex sweep, not a catch-all suppression).
7. The slice is **single-run** under `run_selected_slice_v1`; no chaining beyond the automatic `run_selected_slice_v1 → relay_gate_decision` pairing defined in `RELAY_RUNTIME_V0` §7.2.

## 4. Non-goals

- **No** Phase 2 product UX work (that remains the domain of a separately chartered product sprint).
- **No** semantic contract edits (`docs/SEMANTIC_CONTRACTS.md` is untouched by this sprint).
- **No** relay protocol amendments (`CODEX_AUTONOMY_V1.md` §§14–15), **no** registry amendments (`JOB_REGISTRY_V1.md`), **no** runtime-spec amendments (`RELAY_RUNTIME_V0.md`).
- **No** new job types, **no** new relay subcommands, **no** new artifact paths outside what Job Registry v1 already defines.
- **No** `orchestrator/` revival or edits.
- **No** auto-fixing of control-plane docs (the consistency check remains **advisory only** per `JOB_REGISTRY_V1.md` §3.4).
- **No** widening from the single selected slice. Additional hardening candidates require explicit SELECTION under this sprint (one at a time).
- **No** promotion of the pre-v1 `orchestrator/` prototype.

## 5. Validation posture

- **Universal tier:** `python -m pytest -q` on baseline before and after BUILD; must be green both sides with no new failures.
- **Functional witness (pilot replay):** re-invoke the targeted relay job (e.g. `control_plane_consistency_check`) on a clean baseline **after** the slice lands and confirm the cited pilot finding is either suppressed (for known benign cases) or continues to fire (for genuine drift). Artifact under `artifacts/health/<timestamp>/` is the evidence.
- **Negative witness (in-test):** each slice must include at least one unit-test assertion that a **genuinely missing** or **genuinely drifted** case **still** produces the original finding — i.e. the narrow rule does not silence real problems.
- **No UI smoke required** (evidence-plane only; no `src/viz/**` touch).
- **Stop / escalate:** if the narrow rule cannot be expressed without widening scope (e.g. would need to pattern-match arbitrary sprint names, or would require editing a canonical doc), **stop** the BUILD and return to SELECTION; do not widen.

---

## 6. Sprint 003 map (lightweight)

### A. Selected now

- **Sprint003-Slice001** — `control_plane_consistency_check` placeholder-literal suppression. **Evidence-plane only.** **First real relay-assisted slice.**

### B. Deferred candidates (do not promote without explicit SELECTION)

- **Sprint003-Slice002 (candidate):** `codebase_health_report` — extend `known_unresolved_items` to surface a canonical count of ignored-artifact directories (informational). **Not** selected; listed here only as a candidate shape for the **next** hardening slice if pilot evidence supports it.
- **Sprint003-Slice003 (candidate):** `control_plane_consistency_check` — add **heading-gap monotonicity** finding class (currently only duplicate-heading-number is checked per `scripts/relay_runtime_v0.py` §3.4 step 2). **Not** selected.
- Any other pilot-driven finding from future relay runs is a candidate **only after** it appears in a real artifact.

### C. Not now / anti-goals

- Product UX work (Phase 2 product scope).
- Protocol / registry / runtime-spec amendments.
- `orchestrator/` revival.
- Multi-job chaining beyond `run_selected_slice_v1 → relay_gate_decision`.
- Silent widening of any relay-job rule (e.g. generic regex suppression).

---

## 7. Sprint003-Slice001 — `control_plane_consistency_check` placeholder-literal suppression (**SELECTED**)

**Identifier:** `Sprint003-Slice001`
**Title:** `control_plane_consistency_check` placeholder-literal suppression
**Declared plane:** `EVIDENCE-PLANE`
**Execution mode:** `CODEX_AUTONOMY_V1` §2 authority, **relay-assisted** via `run_selected_slice_v1` (Job Registry v1 §3.1). Retry budget max: **2** (`CODEX_AUTONOMY_V1` §7 default).

### 7.1 User / problem statement

The first **read-only** relay pilot (and the staged/forensic-replay pilots that followed) surfaced three benign warnings from `control_plane_consistency_check`:

- `docs/SOP/OPERATING_RULES.md` — reference `'docs/SOP/SPRINT_00X.md'` does not resolve on disk.
- `docs/SOP/CODEX_AUTONOMY_V1.md` — reference `'docs/SOP/SPRINT_00X_PHASE_Y.md'` does not resolve on disk.
- `docs/SOP/JOB_REGISTRY_V1.md` — reference `'docs/SOP/SPRINT_00X_PHASE_Y.md'` does not resolve on disk.

These are **intentional template placeholders** (variable tokens `00X` and `_Y`) used by `docs/SOP/SPRINT_TEMPLATE.md` and the SOP authoring standards to describe the general shape of a sprint-spec path. They are **not** real references to missing docs.

Treating them as unresolved references creates **signal-diluting noise** in a tool whose purpose is to help the steward distinguish **real** control-plane drift (e.g. a `CURRENT_FRONTIER.md` pointer to a sprint spec that genuinely does not exist) from **known** placeholder strings.

### 7.2 Exact target

- **Primary code:** `scripts/relay_runtime_v0.py` — function `dispatch_control_plane_consistency_check`, **step 3** (backtick-quoted reference resolution; the `_LINK_PATH_RE` matching block).
- **Primary tests:** `tests/test_relay_runtime_v0.py` — add at least two new unit-test cases (positive suppression + negative / still-flagged) covering the new rule.
- **Out of scope of the diff:**
  - Any file under `docs/SOP/**` or `docs/CONTROL_PLANE/**`.
  - `docs/SOP/CODEX_AUTONOMY_V1.md`, `docs/SOP/JOB_REGISTRY_V1.md`, `docs/SOP/RELAY_RUNTIME_V0.md` (these placeholders live **in** those docs and stay **as-is** — the fix goes in the checker, not the docs).
  - Any file under `src/viz/**` or other product-plane paths.
  - Any file under `orchestrator/`.

### 7.3 Non-goals (slice-level)

- **Do not** edit `docs/SOP/OPERATING_RULES.md`, `docs/SOP/CODEX_AUTONOMY_V1.md`, or `docs/SOP/JOB_REGISTRY_V1.md` to remove the placeholders (those placeholders are **intentional template documentation**).
- **Do not** add a wide / catch-all suppression (e.g. "ignore any unresolved `docs/SOP/SPRINT_*.md`"). The rule must be **explicit** — scoped to the known placeholder tokens (`00X`, `_Y.md`, or an explicit allow-list of literal placeholder paths).
- **Do not** introduce a new finding class, new config knob, or new CLI flag.
- **Do not** change the `control_plane_consistency_check` report schema (shape of `findings[]` entries, `passed`, `generated_at`, etc.).
- **Do not** change the job's `authority boundary`, `stop conditions`, `outputs`, or `side effects` as declared in `JOB_REGISTRY_V1.md` §3.4.
- **Do not** touch any other step of `dispatch_control_plane_consistency_check` (steps 1, 2, 4 remain as-is).

### 7.4 Acceptance bullets (slice-level; all must hold)

- [ ] Running `control_plane_consistency_check` via the relay on a **clean** baseline produces a report in which the three `SPRINT_00X`-family placeholder warnings cited in §7.1 **do not appear**.
- [ ] The suppression is **narrow and explicit**: the code change targets a specific, documented placeholder shape (e.g. tokens containing `00X` and/or `_Y.md` used as SOP template variables), not a generic regex over all `docs/SOP/SPRINT_*.md`.
- [ ] A **genuinely missing** canonical-doc reference (e.g. a link to `docs/SOP/DEFINITELY_NOT_A_REAL_DOC.md`) still produces a `warn` finding from step 3.
- [ ] `tests/test_relay_runtime_v0.py` adds **at least one** unit test asserting the placeholder is suppressed **and** **at least one** unit test asserting a genuinely missing doc is still flagged.
- [ ] `python -m pytest -q` on baseline passes with **zero regressions** relative to the pre-BUILD run.
- [ ] The BUILD diff contains **no writes** under `docs/SOP/**`, `docs/CONTROL_PLANE/**`, `src/viz/**`, or `orchestrator/`.
- [ ] The §14.1 `relay_result.json` payload reports `declared_plane == "EVIDENCE-PLANE"` and satisfies `§14.3` invariant `declared_plane_matches_actual`.
- [ ] `stop_condition` is `null` on a clean BUILD; `ready_for_control_closeout` is `true`; §15 decision is `CONTINUE`.

### 7.5 Validation posture (slice-level)

- **Universal:** `python -m pytest -q` before BUILD (record baseline test count) and after BUILD (must be green; new tests counted explicitly).
- **Functional witness:** after BUILD, re-invoke `control_plane_consistency_check` on the baseline; attach the resulting `artifacts/health/<timestamp>/control_plane_consistency_report.json` to closeout and confirm the three cited placeholder warnings are absent.
- **Negative witness:** covered in-test (a genuinely missing-doc fixture asserts the warn path still fires).
- **No UI smoke required** (no product code touched).
- **Stop / escalate:** if the narrow rule cannot be expressed without matching arbitrary sprint names, or would require editing a canonical doc, **stop BUILD** and hand back to the steward for re-SELECTION — do not widen.

### 7.6 Why this is the right first real relay-assisted slice

- **Directly grounded in pilot evidence** — the exact finding comes from the read-only pilot's `control_plane_consistency_report.json` and is reproduced in staged and forensic-replay pilots.
- **Evidence-plane only** — no product UX risk, no control-plane doc churn, no contract impact.
- **Small and low-risk** — a single function, a single rule, a single pair of unit tests.
- **Tests the full relay loop under governance for the first time in anger** — `run_selected_slice_v1` → §14.1 payload → `relay_gate_decision` → §15 decision, with a real (not pilot) slice and real product-of-record acceptance.
- **Correctly narrow** — explicitly refuses the tempting wider alternatives (editing canonical docs to remove placeholders; catch-all regex suppression).
- **Clean failure mode** — if the rule cannot be expressed narrowly, the slice stops at BUILD and returns to steward SELECTION without any control-plane or product damage.

---

## 8. Execution posture

- **Relay invocation:** operator runs `run_selected_slice_v1` with:
  - `slice_id = "Sprint003-Slice001"`
  - `sprint_spec_path = "docs/SOP/SPRINT_003_PHASE_2.md"`
  - `declared_plane = "EVIDENCE-PLANE"`
  - `baseline_branch` = branch tip of `recovery/frontier-steward-v2_1-baseline` (verify `git rev-parse HEAD`)
  - `build_branch` = fresh (must not pre-exist locally or on remote)
  - `retry_budget_max = 2`
- **Preflight** (`CODEX_AUTONOMY_V1` §5 + `RELAY_RUNTIME_V0` §8): tree must be CLEAN; no untracked canonical docs under `docs/SOP/**` or `docs/CONTROL_PLANE/**`; `baseline_branch` matches `CURRENT_FRONTIER.md` repo-state gate; `build_branch` does not pre-exist.
- **BUILD authority:** the Codex worker may only commit to `build_branch` within the declared plane (`EVIDENCE-PLANE`). Any diff outside evidence-plane files forces `MIXED_PLANE_CONTAMINATION` and a `BLOCKED` §15 decision.
- **Promotion:** the worker may fast-forward / merge `build_branch` into `baseline_branch` **only** if all §9 gates (`CODEX_AUTONOMY_V1`) are green, `tree_cleanliness` invariants hold, and `§15 == CONTINUE`. No push. No tag.
- **CONTROL-CLOSEOUT:** steward-only. On `CONTINUE`, the steward updates `CURRENT_FRONTIER.md`, `HANDOFF.md`, and this spec's §9 ledger.

## 9. Slice ledger (Sprint 003)

- **Sprint003-Slice001** — **SELECTED** (2026-04-20). Status: pre-BUILD. No product SHA yet.

(Further slices, when chartered, append to this section on CONTROL-CLOSEOUT.)

## 10. Last updated

2026-04-20 — Sprint 003 chartered as **pilot-driven evidence-plane hardening (relay-assisted)**. **Sprint003-Slice001 SELECTED** as the **first real relay-assisted slice** following successful Relay Runtime V0 local pilots (read-only, staged/manual-resume, forensic-replay). Control-plane / SELECTION-only pass; no product code, no orchestrator edits, no protocol or registry amendments. Next pending execution step: **BUILD via relay-assisted execution** (`run_selected_slice_v1`, `Sprint003-Slice001`).
