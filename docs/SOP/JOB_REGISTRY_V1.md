# JOB_REGISTRY_V1

Purpose: define the **starter set of named, runnable operational programs** ("jobs") that the future relay will dispatch. A job is a **bounded, repeatable unit of work** with a fixed authority boundary, explicit stop conditions, and a defined output contract. Jobs are the **nouns the relay acts on**; `docs/SOP/CODEX_AUTONOMY_V1.md` §§14–15 define the **verbs the relay speaks** between a job run and the next decision.

Status: **v1 — starter registry, four jobs.** Introduced **after** `CODEX_AUTONOMY_V1.md` was canonicalized and **before** Sprint 003 is chartered. This doc defines **what** each job is; it does **not** define **how** the relay runtime implements dispatch — that is a future bounded pass (e.g. `RELAY_RUNTIME_V0`).

Precedence (on any conflict, canonical docs win in this order):

1. `docs/SOP/CURRENT_FRONTIER.md`
2. `docs/SOP/HANDOFF.md`
3. `docs/SOP/OPERATING_RULES.md`
4. `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
5. `docs/SOP/CODEX_AUTONOMY_V1.md`
6. This doc (`JOB_REGISTRY_V1.md`)

## 1. Non-goals (explicit boundaries for v1)

This doc does **not**:

- Charter Sprint 003 or any slice.
- Define the relay runtime, its dispatch loop, its storage layout, or its CLI.
- Authorize any job to cross the Codex Autonomy v1 §2 authority boundary (SELECTION and CONTROL-CLOSEOUT remain steward-only).
- Replace or widen the §14.1 relay result schema or the §15 decision policy.
- Grow the registry. v1 is deliberately four jobs. Additions require a new bounded control-plane pass (`JOB_REGISTRY_V1_1.md` or successor).

## 2. Registry entry schema

Every job in this doc uses the same fields, in this order:

- **name** — stable, lowercase, snake_case, version-suffixed (`_v1`) when the contract is versioned.
- **purpose** — one-sentence operational intent.
- **inputs** — exact fields required to invoke. Missing/invalid inputs → hard stop before side effects.
- **authority boundary** — what planes and stages the job may touch. Anything outside is a stop condition, not a decision.
- **stop conditions** — enumerated explicit halts. A job **must** halt on any listed condition and surface it, not auto-repair.
- **outputs** — what the job emits on a normal finish. Where relevant, this includes a `CODEX_AUTONOMY_V1` §14.1 payload.
- **side effects** — exact write classes (branches, commits, artifacts, logs). "None" means strictly read-only.
- **human signoff required?** — `yes` / `no` / `conditional` with the condition named. Any `yes` blocks automated continuation.

## 3. Jobs (v1)

### 3.1 `run_selected_slice_v1`

- **name**: `run_selected_slice_v1`
- **purpose**: execute exactly one already-SELECTED slice end-to-end under the `CODEX_AUTONOMY_V1` protocol, stopping before CONTROL-CLOSEOUT.
- **inputs**:
  - `slice_id` — verbatim from the active sprint spec (e.g., `Sprint003-Slice001`); must already exist in `docs/SOP/SPRINT_00X_PHASE_Y.md`.
  - `sprint_spec_path` — path to the sprint spec that names the slice.
  - `declared_plane` — one of `PRODUCT-PLANE` or `EVIDENCE-PLANE`, consistent with the slice spec.
  - `baseline_branch` — accepted baseline named by `CURRENT_FRONTIER.md`.
  - `build_branch` — fresh branch name for this run (must not pre-exist remotely).
  - `retry_budget_max` — integer, default `2` (per `CODEX_AUTONOMY_V1` §7).
- **authority boundary**: `CODEX_AUTONOMY_V1` §2 exactly — the sub-sequence `PREFLIGHT → BUILD → bounded REPAIR → BUILD-CLOSEOUT → PROMOTION`. Must not perform SELECTION, must not perform CONTROL-CLOSEOUT, must not write under `docs/SOP/**` or `docs/CONTROL_PLANE/**` (`CODEX_AUTONOMY_V1` §4), must not modify or touch `orchestrator/`, must not widen scope beyond `OPERATING_RULES.md` "adjacent supporting work".
- **stop conditions**: any `CODEX_AUTONOMY_V1` §8 stop condition fires —
  - `PREFLIGHT_FAIL`, `MAX_RETRIES_EXCEEDED`, `SCOPE_AMBIGUITY`, `UNEXPECTED_CONTRACT_CHANGE`, `MIXED_PLANE_CONTAMINATION`, `UNCLEAR_TEST_RESULTS`, `SELECTION_BOUNDARY_REACHED`, `REPO_STATE_DRIFT`, `CONTROL_PLANE_CLOSEOUT_NEEDED`.
  - Plus schema-internal violations named in `CODEX_AUTONOMY_V1` §14.3 (e.g., `declared_plane` does not match actual edits → force `MIXED_PLANE_CONTAMINATION`).
- **outputs**:
  - Human-readable §10 textual blocks (worker report, closeout summary) on stdout/run log.
  - Machine-readable `CODEX_AUTONOMY_V1` §14.1 payload `relay_result.json`, written to the run-scoped path (default `artifacts/ui_smoke/<run_id>/relay_result.json`).
  - Both are always emitted; the §14 payload never replaces the §10 blocks.
- **side effects**:
  - Creates `build_branch` off `baseline_branch`.
  - May commit on `build_branch` within the declared plane only.
  - May fast-forward or merge `build_branch` into `baseline_branch` **only** if all `CODEX_AUTONOMY_V1` §9 gates are green and `tree_cleanliness` invariants hold (§14.3).
  - Writes artifacts under `artifacts/` (already `.gitignore`-covered).
  - Does **not** push to any remote. Does **not** tag.
- **human signoff required?**: **conditional** —
  - `no` for the autonomy sub-sequence itself while `stop_condition == null` and `ready_for_control_closeout == true`.
  - `yes` before CONTROL-CLOSEOUT (always steward-only) and for any non-null `stop_condition`.

### 3.2 `relay_gate_decision`

- **name**: `relay_gate_decision`
- **purpose**: given one `run_selected_slice_v1` run's `CODEX_AUTONOMY_V1` §14.1 payload, emit exactly one `CODEX_AUTONOMY_V1` §15 decision per the §15.1 precedence order.
- **inputs**:
  - `relay_result_path` — path to a single `relay_result.json` conforming to §14.1.
  - `policy_version` — must equal the `schema_version` of the payload (currently `"1"`). Mismatch is a schema violation.
- **authority boundary**: **read-only** with respect to code, docs, and git. The only thing this job may mutate is its own decision log artifact. It may **name** a follow-up job (e.g., `run_selected_slice_v1` when the §15.1 outcome is `RETRY_ALLOWED`) but **must not** dispatch it; dispatch is the relay runtime's responsibility (see `RELAY_RUNTIME_V0.md`).
- **stop conditions**:
  - Payload is unparseable JSON → `BLOCKED`.
  - Payload violates §14.1 schema (missing required field, unknown enum value, invariant violation per §14.3) → `BLOCKED`.
  - `policy_version != payload.schema_version` → `BLOCKED`.
  - Any non-null `stop_condition` in the payload that is not covered by a §15 rule → `BLOCKED` (conservative fallback; never silently treat as `CONTINUE`).
- **outputs**:
  - A decision record written to `artifacts/relay/<run_id>/decision.json`:
    ```json
    {
      "decision": "CONTINUE | RETRY_ALLOWED | STOP_FOR_REVIEW | BLOCKED",
      "rule_matched": "§15.x",
      "reason": "short factual string",
      "follow_up_job": "run_selected_slice_v1 | null",
      "requires_human_signoff": true
    }
    ```
  - The enum values for `decision` are the §15.1 decision enum; this job **must not invent new values**.
- **side effects**:
  - Writes one JSON file under `artifacts/relay/` (already `.gitignore`-covered).
  - Does **not** modify the input payload. Does **not** touch any repo file outside `artifacts/relay/`.
- **human signoff required?**: **conditional** —
  - `no` for `CONTINUE` and `RETRY_ALLOWED` (decision record is valid; next step is steward handoff for CONTROL-CLOSEOUT on `CONTINUE`, or operator re-invocation per §15.4 on `RETRY_ALLOWED` — neither is auto-dispatch by this job).
  - `yes` for `STOP_FOR_REVIEW` (steward judgment before further autonomous work) and `BLOCKED` (schema/invariant defect or hard §8 mapping — always human-visible).

### 3.3 `codebase_health_report`

- **name**: `codebase_health_report`
- **purpose**: produce a grounded, read-only snapshot of the repository's operational health so any SELECTION or PREFLIGHT pass can rely on repo facts, not assumptions.
- **inputs**:
  - `repo_root` — path to the repo working tree. Defaults to CWD.
  - `baseline_branch` — branch to evaluate. Defaults to the branch named in `CURRENT_FRONTIER.md` "Repo-state gate".
- **authority boundary**: strictly **read-only**. No writes to tracked files, no git mutations (no `add`, `commit`, `checkout`, `merge`, `reset`, `stash`), no network calls, no test execution. May shell out to `git` for read queries (`status`, `log`, `rev-parse`, `diff --stat`, `check-ignore`) only.
- **stop conditions**:
  - `repo_root` is not a git repository.
  - Any canonical doc in the precedence list (§0 of this doc, items 1–5) is missing or unreadable.
  - `baseline_branch` does not exist locally.
  - Working tree read fails (permissions, corruption).
- **outputs**: a structured report with at least these fields, emitted to stdout **and** written to `artifacts/health/<timestamp>/codebase_health_report.json`:
  - `repo_root`, `branch`, `head_sha`, `head_sha_short`
  - `tree_cleanliness`: `{ tracked_modified: int, staged: int, untracked: int, untracked_paths: [str] }`
  - `canonical_docs_present`: map of `{doc_path: true|false}` for items 1–5 of the precedence list
  - `last_accepted_slice_id` and `last_accepted_product_sha` (parsed from `CURRENT_FRONTIER.md`; null if unparseable — **not** auto-repaired)
  - `orchestrator_status`: `{ on_disk: bool, gitignored: bool, tracked_file_count: int }`
  - `known_unresolved_items`: array of steward-visible residues (e.g., untracked non-`.gitignore`'d paths)
  - `generated_at` (ISO-8601 UTC)
- **side effects**: writes exactly one JSON artifact under `artifacts/health/` (already `.gitignore`-covered). Writes nothing else.
- **human signoff required?**: **no**. This job is purely informational. Readers (steward or relay) decide what to do with its output in a separate pass.

### 3.4 `control_plane_consistency_check`

- **name**: `control_plane_consistency_check`
- **purpose**: verify that the canonical control-plane docs are **internally consistent** at structural and cross-reference level — heading numbering, cross-doc references resolve, the `CODEX_AUTONOMY_V1` §14 schema and §15 decision enum are still paired, and `CURRENT_FRONTIER.md` does not reference nonexistent sprint/slice spec files.
- **inputs**:
  - `docs_root` — path to `docs/`. Defaults to `<repo_root>/docs`.
  - `precedence_list` — optional override; defaults to items 1–6 of this doc's precedence list plus this doc itself.
- **authority boundary**: strictly **read-only**. No writes, no git mutations, no network, no test execution. May parse Markdown structurally (headings, links, file path mentions) but must **not** rewrite anything. **Advisory only** — never auto-fixes findings.
- **stop conditions**:
  - Any doc in `precedence_list` is missing.
  - A doc is unreadable or not valid UTF-8.
  - A declared `schema_version` in `CODEX_AUTONOMY_V1` §14.1 does not match the version referenced in §15.
- **outputs**: a structured report emitted to stdout **and** written to `artifacts/health/<timestamp>/control_plane_consistency_report.json`, with at least:
  - `passed`: bool (true iff zero `severity: "error"` findings)
  - `findings`: array of `{ severity: "error" | "warn" | "info", doc, locator, message }`
    - checked classes include (non-exhaustive):
      - heading numbering monotonicity within each doc (no duplicate `## N.` headings, no gaps large enough to indicate an edit accident — e.g., `## 14. Last updated` alongside a new `## 14. Relay result contract`)
      - every Markdown link/path reference inside a precedence-list doc resolves to a file that exists on disk
      - every slice/sprint-spec reference in `CURRENT_FRONTIER.md` resolves
      - `CODEX_AUTONOMY_V1` §14.1 field names referenced by §14.3 invariants and §15 rules all still exist in §14.1
      - `CODEX_AUTONOMY_V1` §8 `stop_condition` enum values match §14.2 and §15 coverage
  - `generated_at` (ISO-8601 UTC)
- **side effects**: writes exactly one JSON artifact under `artifacts/health/` (already `.gitignore`-covered). Writes nothing else.
- **human signoff required?**: **no** for a report with zero findings. **Advisory** for any finding — the steward decides in a separate control-plane pass whether to act. This job never edits control-plane docs.

## 4. Interactions (for future relay runtime reference)

The registry does not define dispatch, but it does name the **legal composition** a v0 relay may rely on:

- `run_selected_slice_v1` → emits §14.1 payload → `relay_gate_decision` consumes it → emits decision.
- Before a steward-authored SELECTION, `codebase_health_report` and `control_plane_consistency_check` may run in any order; both are read-only and independent.
- **What happens next** (canonical §15.1 + `RELAY_RUNTIME_V0`): On `CONTINUE`, the relay/runtime **stops** after recording the decision and surfacing the §10.6 HANDBACK; the next **human** step is **steward CONTROL-CLOSEOUT** (`CODEX_AUTONOMY_V1` §15.3 — no auto-closeout, no auto-SELECTION). On `RETRY_ALLOWED`, **at most one** additional in-slice worker invocation is permitted per §15.4 / §7 (same slice spec, `retry_count += 1`); no scope/plane change, no other job chaining. On `STOP_FOR_REVIEW` or `BLOCKED`, automation halts for **steward disposition**; a non-null `stop_condition` is mapped by §15.2 (often `STOP_FOR_REVIEW` or `BLOCKED`, not `CONTINUE`) and must **never** be silently upgraded to `CONTINUE`. Automated chaining that treats canonical steering truth as closed before steward CONTROL-CLOSEOUT on a `CONTINUE` path is forbidden (`RELAY_RUNTIME_V0` §§9–10).
- `BLOCKED` always halts the chain; no automated follow-up is authorized.

## 5. Versioning and change control

- This doc is `v1`. Any modification to an existing job's **authority boundary**, **inputs**, **outputs**, or **stop conditions** is a **breaking change** and requires either a new versioned doc (`JOB_REGISTRY_V1_1.md` or `JOB_REGISTRY_V2.md`) or a steward-accepted amendment on this file with a footer entry.
- Adding a new job is a **non-breaking change** but still requires a bounded control-plane pass of its own; it must not be bundled with a Sprint BUILD pass.
- Removing or renaming a job is a **breaking change**.

## 6. Last updated

2026-04-21 — Control-plane vocabulary reconcile: `relay_gate_decision` §15.1 decision enum and closeout-chaining notes aligned with `CODEX_AUTONOMY_V1.md` §15.1 and `RELAY_RUNTIME_V0.md` (`CONTINUE` / `RETRY_ALLOWED` / `STOP_FOR_REVIEW` / `BLOCKED`; removed stale `RETRY` / `STOP_CLEAN` / `STOP_HARD` wording). No protocol intent change; no BUILD.

2026-04-20 — Initial definition of Job Registry v1 with four starter jobs: `run_selected_slice_v1`, `relay_gate_decision`, `codebase_health_report`, `control_plane_consistency_check`. Control-plane / process-only pass; no product code, no orchestrator edits, no sprint chartered. Depends on: `docs/SOP/CODEX_AUTONOMY_V1.md` (v1, committed `57de839`).
