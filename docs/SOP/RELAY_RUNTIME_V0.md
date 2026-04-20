# RELAY_RUNTIME_V0

Purpose: define the **minimum viable runtime layer** that dispatches `docs/SOP/JOB_REGISTRY_V1.md` jobs and consumes `docs/SOP/CODEX_AUTONOMY_V1.md` §§14–15 relay results. This doc is the **boundary-before-implementation** spec for a local, single-operator, staged relay. It names **what the runtime does, what it does not do, and what stays steward-only**, so any future implementation pass has a fixed contract to build against.

Status: **v0 — pre-implementation spec, local-only.** Introduced after Job Registry v1 was canonicalized and before any Sprint 003 BUILD. Applies to the local relay process; no server, no daemon, no remote dispatch. Supersedes nothing.

Precedence (on any conflict, canonical docs win in this order):

1. `docs/SOP/CURRENT_FRONTIER.md`
2. `docs/SOP/HANDOFF.md`
3. `docs/SOP/OPERATING_RULES.md`
4. `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
5. `docs/SOP/CODEX_AUTONOMY_V1.md`
6. `docs/SOP/JOB_REGISTRY_V1.md`
7. This doc (`RELAY_RUNTIME_V0.md`)

## 1. Purpose

The runtime exists to do exactly three things:

1. **Dispatch** one named job from Job Registry v1 per invocation, with declared inputs.
2. **Validate** every emitted `CODEX_AUTONOMY_V1` §14.1 `relay_result.json` payload against the §14 schema and §14.3 invariants **before** any downstream step.
3. **Apply** the §15 decision policy to a validated payload and persist the resulting decision as a durable local artifact.

It is not a planner, not a selector, not a strategist, and not an LLM caller. It is a **file-and-state shuttle** between an operator/worker, the job registry contracts, and the §§14–15 grammar already canonicalized in the control-plane.

## 2. Scope

- **Local-only.** Single machine, single operator, CLI-driven. No network except read-only `git` introspection commands and any `git fetch` the operator explicitly invokes.
- **Single in-flight run at a time.** No queue, no parallelism, no multi-slice orchestration.
- **Staged dispatch.** When a job needs a human or a Codex worker to do real work (notably `run_selected_slice_v1`), the runtime **pauses** after staging the task, and **resumes** only when the worker writes the result artifact back.
- **No LLM inside the runtime.** Workers may use LLMs; the runtime itself contains **no `openai`, `anthropic`, or equivalent API calls**. This is a deliberate contrast with the pre-v1 `orchestrator/` prototype.
- **Control-plane-read-only.** The runtime may read any canonical doc; it must write **nothing** to `docs/SOP/**` or `docs/CONTROL_PLANE/**`.

## 3. Supported jobs at v0

Exactly four, pinned to Job Registry v1:

1. `run_selected_slice_v1` (§3.1 of `JOB_REGISTRY_V1.md`)
2. `relay_gate_decision` (§3.2 of `JOB_REGISTRY_V1.md`)
3. `codebase_health_report` (§3.3 of `JOB_REGISTRY_V1.md`)
4. `control_plane_consistency_check` (§3.4 of `JOB_REGISTRY_V1.md`)

The runtime **must not dispatch any job name not in this list**. Unknown job name → immediate refusal, non-zero exit, no side effects.

## 4. Runtime inputs

Inputs at invocation time:

- **Subcommand**: the job name (from §3) plus optional subcommand verbs `stage`, `resume`, `status`, `abort`. Exact CLI shape is deferred to implementation but the logical verbs are fixed here.
- **Job inputs**: exactly the `inputs` fields defined for the named job in `JOB_REGISTRY_V1.md` §3.x. Missing or invalid → refusal, no side effects.
- **Runtime config** (required, small):
  - `baseline_branch` — must match `CURRENT_FRONTIER.md` repo-state gate at invocation time.
  - `repo_root` — absolute path to the working tree; must be a clean git repo at invocation (see §8).
  - `artifacts_root` — defaults to `<repo_root>/artifacts/relay`. Must be gitignored.
  - `job_registry_path` — defaults to `docs/SOP/JOB_REGISTRY_V1.md`.
  - `autonomy_doc_path` — defaults to `docs/SOP/CODEX_AUTONOMY_V1.md`.
- **Environment**: the runtime **must not** require any API key. Setting `OPENAI_API_KEY` or similar is not an input; the runtime ignores them.

All inputs are passed at invocation; the runtime does not read hidden config files outside the repo.

## 5. Runtime outputs

Per invocation:

- **Stdout**: a terse human-readable log of what was staged, validated, decided, and exited with. Never a substitute for artifact files.
- **Exit code**: deterministic mapping to the canonical `CODEX_AUTONOMY_V1` §15.1 decision enum (`CONTINUE` / `RETRY_ALLOWED` / `STOP_FOR_REVIEW` / `BLOCKED`) plus invocation-level outcomes:
  - `0` — `CONTINUE` (§15.1 rule 7; handoff to steward CONTROL-CLOSEOUT)
  - `10` — `RETRY_ALLOWED` (§15.1 rule 5; runtime signals the operator to re-invoke for the same slice within the §7 retry budget)
  - `20` — `STOP_FOR_REVIEW` (§15.1 rules 3, 4, 6, 8; run is paused for steward judgment; not a hard block, but the relay must not auto-advance)
  - `40` — `BLOCKED` (§15.1 rules 1–2; schema/invariant violation or hard §8 stop condition; always human-visible)
  - `2` — invocation-level refusal (bad inputs, unknown job, preflight drift before any job ran)
  - `1` — unexpected internal error (bug in runtime; never a normal state)
- **Durable artifacts** (all under `artifacts_root`, all gitignored):
  - `state/run_state.json` — current state machine snapshot
  - `state/current_job.json` — currently staged/in-flight job request
  - `state/last_decision.json` — most recent §15 decision record
  - `runs/<run_id>/` — per-run directory
  - `runs/<run_id>/task_envelope.json` — what was handed to the worker
  - `runs/<run_id>/relay_result.json` — §14.1 payload returned by the worker
  - `runs/<run_id>/decision.json` — §15 decision emitted by `relay_gate_decision`
  - `runs/<run_id>/events.log` — append-only run log (timestamps + transitions)

No output is ever written outside `artifacts_root` by the runtime itself. Writes on the worktree (e.g., build-branch commits from `run_selected_slice_v1`) are performed by the worker inside that job's own authority boundary, not by the runtime directly.

## 6. State files / queue model

The runtime is **state-machine-driven, not queue-driven** at v0.

Run states (values of `run_state.json.status`):

- `idle` — no job in flight; ready to accept a new invocation.
- `staged_for_worker` — runtime has written `task_envelope.json` for `run_selected_slice_v1` and is waiting for the worker to produce `relay_result.json`.
- `validating` — runtime is checking the returned payload against §14.1 and §14.3.
- `deciding` — runtime is applying §15.1 precedence to the validated payload.
- `decided_continue` / `decided_retry_allowed` / `decided_stop_for_review` / `decided_blocked` — terminal states for this run, one per canonical §15.1 decision; runtime exits with the matching exit code (§5) and clears `current_job.json`.
- `aborted` — operator-invoked `abort`; terminal; no further automation.

Rules:

- Only one run may be non-terminal at any time. Attempting to stage a second concurrent run while one is non-terminal → refusal.
- Terminal states are **sticky**: the runtime will not overwrite a terminal `run_state.json` without an explicit operator reset (invocation: `relay reset`, which is itself a no-op if `run_state.status == "idle"`).
- Read-only jobs (`codebase_health_report`, `control_plane_consistency_check`) do **not** occupy the state machine. They run inline, write their artifact, and return. They may be invoked freely regardless of the slice-run state.
- No multi-job chaining beyond the canonical pairing `run_selected_slice_v1` → `relay_gate_decision`. That pairing is **automatic and synchronous** once the payload is produced; no other chaining is permitted at v0.

## 7. Dispatch model

Two dispatch shapes, and only two:

### 7.1 Inline (read-only jobs)

For `codebase_health_report` and `control_plane_consistency_check`:

1. Operator invokes the job with its declared inputs.
2. Runtime executes the job's logic inline, writes the artifact under `artifacts/health/<timestamp>/`, emits the structured report to stdout, and exits `0` (report produced, regardless of findings — findings are advisory per Job Registry v1 §3.3 and §3.4).
3. No state-file writes beyond the per-invocation artifact. Does not touch `state/run_state.json`.

### 7.2 Staged / manual-resume (slice job)

For `run_selected_slice_v1`:

1. Operator invokes the job with its declared inputs (`slice_id`, `sprint_spec_path`, `declared_plane`, `baseline_branch`, `build_branch`, `retry_budget_max`).
2. Runtime performs preflight (see §8), writes `runs/<run_id>/task_envelope.json`, sets `run_state.status = "staged_for_worker"`, stages `current_job.json`, and exits `0` with a staging message.
3. The worker (Codex agent or human) does the slice work under `CODEX_AUTONOMY_V1` §2 authority, ending by writing `runs/<run_id>/relay_result.json`.
4. Operator re-invokes the runtime (`relay resume <run_id>`). Runtime transitions `validating` → `deciding`, applies §15, writes `decision.json` and `state/last_decision.json`, transitions to the corresponding terminal state, and exits with the matching exit code.

The staged model is identical in shape to the pre-v1 `orchestrator/` prototype; what is **new** at v0 is: strict §14.1 validation, strict §15.1 decision, no LLM inside the runtime, and artifact layout disciplined under `artifacts/relay/`.

`relay_gate_decision` is **not** typically dispatched directly by the operator at v0; it is invoked automatically by the runtime at step 4 above. Direct operator invocation is permitted only for forensic replay against an existing `relay_result.json` and must never mutate `state/run_state.json`.

## 8. Stop conditions / halt behavior

The runtime halts (non-zero exit, no further automation, terminal `run_state.status`) on any of:

- **Input refusal** (§4): unknown job name, missing required input, `baseline_branch` mismatch with `CURRENT_FRONTIER.md`, `repo_root` not a git repo. Exit `2`.
- **Preflight drift** before staging `run_selected_slice_v1`:
  - tracked tree not clean → record `stop_condition = REPO_STATE_DRIFT`, map to `STOP_FOR_REVIEW`, exit `20`.
  - untracked canonical docs (any file under `docs/SOP/**` or `docs/CONTROL_PLANE/**` untracked) → same.
  - `build_branch` already exists locally or on remote → refusal, exit `2`.
- **Registry integrity failure**: `JOB_REGISTRY_V1.md` is missing, or the registry as read on disk is older than the runtime's pinned reference SHA for it (implementation detail deferred; the **requirement** is that an unexpected registry edit halts the runtime). Exit `40`.
- **Schema violation** in the returned `relay_result.json` — missing required field, unknown enum value, broken §14.3 invariant → `BLOCKED`, exit `40`.
- **Any non-null `stop_condition`** in the payload — runtime does **not** override it, does **not** auto-retry past the §7 retry budget already enforced inside `run_selected_slice_v1`. Exits per §15 mapping.
- **Operator abort** (`relay abort`): flushes a terminal `run_state.status = "aborted"` and exits `2`.
- **Internal error** (bug): exit `1` with a dump to `events.log`; never silently continues.

Halt behavior is **idempotent**: re-invoking the runtime on a terminal state is a no-op that re-prints the terminal decision and exits with the same code.

## 9. Forbidden behaviors

The runtime **must not**:

- Perform SELECTION, invent a slice, or reinterpret a slice spec.
- Perform CONTROL-CLOSEOUT or write to `docs/SOP/**` or `docs/CONTROL_PLANE/**`.
- Modify, read-for-write, or delete anything under `orchestrator/` (the ignored pre-v1 prototype tree).
- Edit `docs/SOP/JOB_REGISTRY_V1.md`, `docs/SOP/CODEX_AUTONOMY_V1.md`, or this doc.
- Make LLM API calls, HTTP calls, or any non-`git` network call.
- Push, tag, force-push, `git reset --hard`, or `git clean -fdx`.
- Auto-retry beyond the `retry_budget_max` already enforced inside `run_selected_slice_v1` (default `2` per `CODEX_AUTONOMY_V1` §7).
- Run more than one `run_selected_slice_v1` per invocation.
- Switch branches outside of (a) creating `build_branch` off `baseline_branch` for a slice run, and (b) returning to `baseline_branch` on clean exit or abort.
- Invent new §15 decision values or new §8 stop-condition values.
- Silently coerce a malformed payload into a well-formed one.
- Continue past a `BLOCKED` or any non-null `stop_condition`.
- Log secrets or payloads containing secrets.

## 10. What remains steward-only

The runtime does not touch, and never automates, any of:

- SELECTION (chartering a sprint, naming a slice, deferring / un-deferring work).
- CONTROL-CLOSEOUT (updating `CURRENT_FRONTIER.md`, `HANDOFF.md`, sprint specs).
- Amendment of `CODEX_AUTONOMY_V1.md` §§1–15 (protocol itself).
- Amendment of `JOB_REGISTRY_V1.md` (adding / removing / renaming jobs; changing any job's authority boundary, inputs, outputs, or stop conditions).
- Amendment of this doc.
- Disposition of any `STOP_FOR_REVIEW` or `BLOCKED` run — the runtime produces the terminal artifact and exits; the steward diagnoses and decides. `CONTINUE` is likewise handed back to the steward for CONTROL-CLOSEOUT (§11), never auto-closed by the runtime.
- Any change to `.gitignore` or the `orchestrator/` disposition.
- Phase transitions, charter decisions, or product-facing policy.

## 11. Interaction with Job Registry v1 and CODEX_AUTONOMY_V1 §§14–15

- **Registry is the source of truth for every job's contract.** The runtime does not embed job semantics; it reads the registry and enforces the fields declared there (`inputs`, `authority boundary`, `stop conditions`, `outputs`, `side effects`, `human signoff`).
- **§14.1 is the wire format between worker and runtime.** Every `relay_result.json` is validated field-by-field against §14.1 before any §15 step. Unknown fields may be logged but are **not** a blocker at v0; missing required fields or unknown enum values **are** a blocker (`BLOCKED`).
- **§14.3 invariants are enforced.** If the payload reports `promotion.performed == true` but any invariant of §14.3 is violated, the runtime coerces the outcome to `BLOCKED` and does not execute the §15 decision the payload claims.
- **§15.1 precedence is respected exactly.** The runtime applies the precedence order verbatim; first matching rule wins; later rules are not evaluated. The runtime must not invent a merged decision or skip an earlier rule.
- **Human-signoff postures from the registry are honored.** If a job's output is marked `conditional` or `yes` on human signoff, the runtime halts at the terminal state and **does not** auto-invoke any downstream job — even if a follow-up is named in the decision record.
- **The §10 textual blocks are never regenerated.** The runtime may quote them in `events.log` but never rewrites them; the §14.1 payload is additive, never a replacement.

## 12. Explicitly deferred to later runtime versions

Not in v0. Do **not** rely on any of these; revisiting them requires a new bounded control-plane pass (`RELAY_RUNTIME_V1.md` or successor):

- Multi-run queue, backlog, or scheduler.
- Parallel job execution.
- Remote / headless dispatch (SSH, CI, webhook, cloud agent).
- LLM-driven planning inside the runtime.
- Automatic SELECTION or sprint chartering.
- Persistent database, message bus, or external store. (v0 is file-backed under `artifacts/relay/` only.)
- Web UI, IDE UI, or dashboard.
- Cross-repo dispatch or multi-worktree coordination beyond the single `build_branch` off `baseline_branch`.
- Automatic retry policy beyond `CODEX_AUTONOMY_V1` §7.
- Migration / compatibility tooling for `CODEX_AUTONOMY_V1` §14 `schema_version` bumps. (v0 pins `schema_version == "1"`; any other value is `BLOCKED`.)
- New job types beyond the four in §3.
- Secrets management, credential injection, or vaulted configuration.
- Observability beyond `events.log` + artifact files (no metrics export, no tracing).
- Recovery logic beyond operator-driven `relay reset` on a terminal state.

## 13. Versioning and change control

- This doc is `v0`. It deliberately refuses ambition.
- **Breaking change** (any change to §§3, 4.1–4.5 input contract, 5 exit-code mapping, 6 state enum, 7 dispatch shapes, 8 stop conditions, 9 forbidden behaviors, 10 steward-only list, or 11 interaction claims): requires a new versioned doc (`RELAY_RUNTIME_V0_1.md` or `RELAY_RUNTIME_V1.md`) and explicit steward acceptance.
- **Non-breaking change**: clarifications, typo fixes, tightening of forbidden-behavior wording. Still requires a bounded single-file control-plane pass; never bundled with a BUILD pass.
- Implementation of the runtime is **not** a change to this doc. Implementation lives in product/evidence-plane commits under `scripts/` or `src/relay/` (path to be decided at implementation time) and must cite this doc's version in its commit message.

## 14. Last updated

2026-04-20 — Initial definition of Relay Runtime v0 as a minimum local file-backed staged runtime consuming Job Registry v1 (commit `67f38ad`) and `CODEX_AUTONOMY_V1` §§14–15 (commit `57de839`). Control-plane / process-only pass; pre-implementation spec; no code, no orchestrator edits, no sprint chartered. Deliberately local, single-run, non-LLM, non-selector.

2026-04-20 — Reconciliation pass (post-implementation `bc1b9ac`). Aligned §§5–6 decision enum, terminal-state names, and exit-code mapping with the canonical 4-decision enum from `CODEX_AUTONOMY_V1.md` §15.1 (`CONTINUE` / `RETRY_ALLOWED` / `STOP_FOR_REVIEW` / `BLOCKED`). Removed the non-canonical `STOP_CLEAN` / `STOP_HARD` split and the unused exit `30`. Updated §8 preflight-drift mapping to `STOP_FOR_REVIEW` (exit `20`) to match the implementation, and §10 steward-only list accordingly. No new constraints, no scope widening; control-plane / semantic-consistency only.
