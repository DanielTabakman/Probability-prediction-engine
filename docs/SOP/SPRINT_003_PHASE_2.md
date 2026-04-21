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

- **No Sprint 003 (evidence-plane) slice selected.** **Sprint003-Slice001** **CLOSED / shipped** (2026-04-21 CONTROL-CLOSEOUT; Slice001 product-of-record **`e044f0fe16097da32ef7e472084e266fc5405740`**; see §9 slice ledger). §6.B evidence-plane candidates remain **deferred** pending fresh pilot evidence per §3 rule 2.
- **Interleaved CONTROL-PLANE slice — `Workflow-Hardening-Slice-001` — CLOSED / shipped (2026-04-21 CONTROL-CLOSEOUT; advisory, non-gating).** This slice lived **outside** the evidence-plane scope of Sprint 003 (per §3 rule 3 this sprint's BUILD does not write to `docs/SOP/**`); it was a short steward-driven CONTROL-PLANE interlude that cashed in the Sprint003-Slice001 timing/context audit before any further Sprint 003 evidence-plane SELECTION. **Spec anchor:** `docs/SOP/CURRENT_FRONTIER.md` "Current feature slice" (inline). **Not** routed through `RELAY_RUNTIME_V0` / `run_selected_slice_v1` (CONTROL-PLANE only). Accepted baseline tip after promotion: **`e876bfe455ba5d51057a177088e362e9aa8ce384`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/workflow-hardening-slice-001`; pre-promotion tip `e044f0fe16097da32ef7e472084e266fc5405740`). Ledger entry: §9. Any further Sprint 003 §6.B evidence-plane SELECTION remains **deferred**, gated on fresh pilot evidence per §3 rule 2. The next pending execution step (canonical in `docs/SOP/CURRENT_FRONTIER.md` / `docs/SOP/HANDOFF.md`) is a **steward-only SELECTION / timing-audit decision gate** — BUILD does **not** start in the next pass.

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

## 7. Sprint003-Slice001 — `control_plane_consistency_check` placeholder-literal suppression (**CLOSED / shipped, 2026-04-21**)

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

- **Sprint003-Slice001** — **CLOSED / shipped** (2026-04-21 CONTROL-CLOSEOUT; **first real relay-assisted slice**).
  - **Selected:** 2026-04-20.
  - **BUILD executed:** 2026-04-21 via `run_selected_slice_v1` (Job Registry v1 §3.1) on `build_branch = build/sprint003-slice001-placeholder-suppression`, `baseline_branch = recovery/frontier-steward-v2_1-baseline`, `declared_plane = EVIDENCE-PLANE`, `retry_budget_max = 2` (retry count used: 0). Dispatch: staged / manual-resume per `RELAY_RUNTIME_V0` §7.2.
  - **Baseline tip before promotion:** `63fee9510670873d4c2a5b6d82025de617b55a73`.
  - **Accepted baseline tip after promotion (product-of-record):** **`e044f0fe16097da32ef7e472084e266fc5405740`** (fast-forward; `ancestor_check_pass: true`). Verify with `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline` and `git merge-base --is-ancestor e044f0fe16097da32ef7e472084e266fc5405740 HEAD`.
  - **Diff scope (evidence-plane only):** `scripts/relay_runtime_v0.py` (`dispatch_control_plane_consistency_check` step 3 — explicit `_SOP_SPRINT_TEMPLATE_PLACEHOLDERS` literal allow-list), `tests/test_relay_runtime_v0.py` (positive-suppression + negative-still-flagged unit tests). Zero writes under `docs/SOP/**`, `docs/CONTROL_PLANE/**`, `src/**`, or `orchestrator/` — satisfies §3 acceptance rules 1, 3, 4 and §7.4 bullets.
  - **Evidence pointers (relay-assisted BUILD):**
    - **Pytest (universal tier):** `python -m pytest -q` → **117** passed; no regressions vs pre-BUILD (`tests.pytest_status == "PASS"`, `validation_classification == "deterministic"`). Satisfies §7.4 "zero regressions".
    - **Post-build functional witness (§7.5 functional witness):** `artifacts/health/20260421_164325/control_plane_consistency_report.json` — `passed: true`, `findings: []`; the three cited `SPRINT_00X` / `SPRINT_00X_PHASE_Y` template placeholder warnings are absent. Satisfies §7.4 bullets 1, 2.
    - **Relay result payload (`CODEX_AUTONOMY_V1` §14.1):** `artifacts/relay/runs/20260421_163438/relay_result.json` — `declared_plane == "EVIDENCE-PLANE"` (satisfies §3 rule 1 / §14.3 `declared_plane_matches_actual`), `preflight.build_allowed == true`, `tree_cleanliness.build_branch_clean == true`, `tree_cleanliness.mixed_plane_residue == false`, `stop_condition == null`, `ready_for_control_closeout == true`, `safe_to_continue == true`, `promotion.performed == true`, `promotion.method == "fast-forward"`, `product_commit_sha == "e044f0fe16097da32ef7e472084e266fc5405740"`. Negative witness coverage (§5 / §7.4 bullets 3, 4) lives in `tests/test_relay_runtime_v0.py` and is counted in the 117-test run.
    - **§15 relay-gate decision:** `artifacts/relay/runs/20260421_163438/decision.json` → **`CONTINUE`** (`rule_matched == "15.2 rule 7"` — *clean closure; hand back to steward for CONTROL-CLOSEOUT*), `schema_violations == []`, `invariant_violations == []`.
    - **Task envelope / run log:** `artifacts/relay/runs/20260421_163438/task_envelope.json`, `artifacts/relay/runs/20260421_163438/events.log`.
  - **Acceptance (§7.4 checklist status):** all bullets satisfied — narrow/explicit suppression (literal allow-list, not a regex sweep), genuinely-missing-doc case still flagged (negative unit test), `declared_plane == EVIDENCE-PLANE`, §14.3 invariant holds, `stop_condition == null`, `ready_for_control_closeout == true`, §15 decision `CONTINUE`.
  - **Sprint-level acceptance (§3):** all seven rules satisfied (evidence-plane target; pilot-grounded in the first read-only relay pilot's `control_plane_consistency_report.json`; no `docs/SOP/**`, `docs/CONTROL_PLANE/**`, `orchestrator/`, or `src/viz/**` writes; zero pytest regressions; narrow explicit rule; single-run under `run_selected_slice_v1` → `relay_gate_decision`).
  - **Status:** CLOSED / shipped. No reopen. Further Sprint 003 slices must re-enter via explicit SELECTION grounded in a real relay/health artifact per §3 rule 2 and §6.B.

- **`Workflow-Hardening-Slice-001`** — **CLOSED / shipped (2026-04-21 CONTROL-CLOSEOUT; advisory, non-gating).** Declared plane: **CONTROL-PLANE**. **Interleaved outside Sprint 003's evidence-plane scope** — ledgered here only as a cross-reference so the sprint state remains legible; the slice itself is **not** governed by Sprint 003 §§3, 7, or 8 (those apply to evidence-plane slices routed through `RELAY_RUNTIME_V0`).
  - **Canonical spec:** `docs/SOP/CURRENT_FRONTIER.md` "Current feature slice" (inline).
  - **Grounding:** cashed in the Sprint003-Slice001 post-BUILD workflow audit (governance/context overhead near ceiling).
  - **Selected:** 2026-04-21. **BUILD executed:** 2026-04-21 on short-lived branch `build/workflow-hardening-slice-001` off `recovery/frontier-steward-v2_1-baseline @ e044f0fe16097da32ef7e472084e266fc5405740`; steward-driven CONTROL-PLANE BUILD (**not routed** through `run_selected_slice_v1`).
  - **Baseline tip before promotion:** `e044f0fe16097da32ef7e472084e266fc5405740`.
  - **Accepted baseline tip after promotion (control-plane-of-record):** **`e876bfe455ba5d51057a177088e362e9aa8ce384`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/workflow-hardening-slice-001`). Verify with `git rev-parse HEAD` on `recovery/frontier-steward-v2_1-baseline` and `git merge-base --is-ancestor e876bfe455ba5d51057a177088e362e9aa8ce384 HEAD`.
  - **BUILD scope (three outputs, CONTROL-PLANE only — all delivered):** new `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` (canonical timing/context audit + NORMAL / WATCH / ESCALATE threshold bands with lightweight heuristics + per-band advisory actions + explicit advisory-not-gating clause); new `.cursor/rules/context-budget.mdc` (advisory Cursor rule, on-demand load; not a gate); **+15-line** LOAD-ALWAYS / LOAD-ON-DEMAND subsection in `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` (inside the ≤~20-line budget — the "skip if it would enlarge the diff" escape hatch from SELECTION was not needed).
  - **Hard out-of-scope (honored):** `CODEX_AUTONOMY_V1.md`, `JOB_REGISTRY_V1.md`, `RELAY_RUNTIME_V0.md`, this Sprint 003 spec (beyond this cross-reference entry), `src/**`, `scripts/**`, `tests/**`, `orchestrator/`, new gates, new enums, Sprint003-Slice002 / Sprint003-Slice003 selection. BUILD diff confirmed CONTROL-PLANE only.
  - **Evidence pointers (closeout):**
    - **Pytest (universal tier):** `python -m pytest -q` → **117** passed; no regressions vs pre-BUILD (slice touches no runtime code). Matches the pre-BUILD 117-count baseline inherited from Sprint003-Slice001 closeout.
    - **Post-build functional witness (optional; non-gating):** `python scripts/relay_runtime_v0.py stage control_plane_consistency_check` → `artifacts/health/20260421_175320/control_plane_consistency_report.json` — `passed: true`, `findings: []`. The two transient forward-reference warnings flagged at SELECTION (in `CURRENT_FRONTIER.md` and `HANDOFF.md`, both pointing at `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` before BUILD) are cleared by the new canonical audit doc.
  - **Acceptance status (slice-level, per canonical spec in `CURRENT_FRONTIER.md` "Current feature slice"):** all bullets satisfied — canonical audit doc exists with required structure; advisory Cursor rule exists and references the bands; advisory-not-gating posture explicit in both files; LOAD-ALWAYS / LOAD-ON-DEMAND subsection inside ≤~20-line budget and lives in `FRONTIER_STEWARD_PROTOCOL.md` (not a new doc); BUILD diff CONTROL-PLANE only; pytest unchanged at 117; optional consistency witness `passed: true, findings: []`.
  - **Status:** CLOSED / shipped. No reopen. Further SELECTION is steward-only.

(Further slices, when chartered, append to this section on CONTROL-CLOSEOUT.)

## 10. Last updated

2026-04-21 — **`Workflow-Hardening-Slice-001` CONTROL-CLOSEOUT** (steward-only, control-plane only). Slice **CLOSED / shipped** (CONTROL-PLANE; advisory, non-gating; interleaved outside Sprint 003's evidence-plane scope; **not** routed through `RELAY_RUNTIME_V0` / `run_selected_slice_v1`). Accepted baseline tip after promotion: **`e876bfe455ba5d51057a177088e362e9aa8ce384`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/workflow-hardening-slice-001`; pre-promotion tip `e044f0fe16097da32ef7e472084e266fc5405740`). Three CONTROL-PLANE outputs shipped (all within scope): new canonical audit `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` (NORMAL / WATCH / ESCALATE bands + lightweight heuristics + per-band advisory actions + explicit advisory-not-gating clause); new advisory Cursor rule `.cursor/rules/context-budget.mdc` (on-demand load; not a gate); **+15-line** LOAD-ALWAYS / LOAD-ON-DEMAND subsection in `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` (inside the ≤~20-line budget from the slice spec). Evidence recorded in §9: pytest **117** passed (no regressions; slice touches no runtime code); post-build functional witness `artifacts/health/20260421_175320/control_plane_consistency_report.json` (`passed: true`, `findings: []`; the two transient forward-reference warnings for the canonical audit doc are cleared). No product code in this closeout pass; zero writes under `src/**`, `scripts/**`, `tests/**`, `orchestrator/`; no protocol / registry / runtime-spec amendments. §6.B Sprint 003 evidence-plane candidates remain **deferred**, gated on fresh pilot evidence per §3 rule 2. **Next pending execution step (canonical in `docs/SOP/CURRENT_FRONTIER.md` / `docs/SOP/HANDOFF.md`):** **SELECTION / timing-audit decision gate** — steward-only; next pass chooses among a next Sprint 003 §6.B hardening slice (only with fresh pilot evidence), a Phase 2 product UX re-charter, or continued deferral. **BUILD does not start in the next pass.** No next slice selected here.

2026-04-21 — **`Workflow-Hardening-Slice-001` SELECTED** (CONTROL-PLANE; advisory, non-gating; steward-driven; **not** routed through `RELAY_RUNTIME_V0` / `run_selected_slice_v1`). Interleaved outside Sprint 003's evidence-plane scope to cash in the Sprint003-Slice001 timing/context audit **before** any further Sprint 003 evidence-plane SELECTION. Canonical spec inline in `docs/SOP/CURRENT_FRONTIER.md` "Current feature slice"; cross-reference entry added to §6.A and §9 here (this file only — Sprint 003 §§3, 7, 8 do **not** govern this interlude). BUILD outputs in scope: `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` (canonical audit + NORMAL / WATCH / ESCALATE bands + advisory actions), `.cursor/rules/context-budget.mdc` (advisory), optional short LOAD-ALWAYS / LOAD-ON-DEMAND subsection in `FRONTIER_STEWARD_PROTOCOL.md`. Hard out-of-scope: `CODEX_AUTONOMY_V1.md`, `JOB_REGISTRY_V1.md`, `RELAY_RUNTIME_V0.md`, `src/**`, `scripts/**`, `tests/**`, `orchestrator/`, new gates, new enums, Sprint003-Slice002 / Sprint003-Slice003 selection. §6.B Sprint 003 evidence-plane candidates **deferred** behind this interlude. **Next pending execution step:** **BUILD — `Workflow-Hardening-Slice-001` (CONTROL-PLANE)**.

2026-04-21 — **Sprint003-Slice001 CONTROL-CLOSEOUT** (steward-only, control-plane only). Slice CLOSED / shipped as the **first real relay-assisted slice** executed end-to-end under `run_selected_slice_v1` + §15 `relay_gate_decision`. Accepted baseline tip after promotion: **`e044f0fe16097da32ef7e472084e266fc5405740`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/sprint003-slice001-placeholder-suppression`; pre-promotion tip `63fee9510670873d4c2a5b6d82025de617b55a73`). Evidence recorded in §9: pytest **117** passed; post-build functional witness `artifacts/health/20260421_164325/control_plane_consistency_report.json` (`passed: true`, `findings: []`); relay result `artifacts/relay/runs/20260421_163438/relay_result.json` (`stop_condition == null`, `ready_for_control_closeout == true`); §15 decision `artifacts/relay/runs/20260421_163438/decision.json` → **`CONTINUE`** (`rule_matched == "15.2 rule 7"`). BUILD diff was evidence-plane only (`scripts/relay_runtime_v0.py`, `tests/test_relay_runtime_v0.py`). No protocol / registry / runtime-spec amendments. **Next pending execution step (canonical in `docs/SOP/CURRENT_FRONTIER.md` / `docs/SOP/HANDOFF.md`):** **SELECTION / timing-audit decision gate** — steward decides between (a) a next Sprint 003 §6.B hardening slice only if fresh pilot evidence supports it, or (b) a phase / new-sprint re-charter. **BUILD does not start in this pass.**

2026-04-20 — Sprint 003 chartered as **pilot-driven evidence-plane hardening (relay-assisted)**. **Sprint003-Slice001 SELECTED** as the **first real relay-assisted slice** following successful Relay Runtime V0 local pilots (read-only, staged/manual-resume, forensic-replay). Control-plane / SELECTION-only pass; no product code, no orchestrator edits, no protocol or registry amendments. Next pending execution step: **BUILD via relay-assisted execution** (`run_selected_slice_v1`, `Sprint003-Slice001`).
