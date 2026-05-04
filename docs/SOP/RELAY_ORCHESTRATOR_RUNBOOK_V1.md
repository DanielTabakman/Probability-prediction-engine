## RELAY_ORCHESTRATOR_RUNBOOK_V1

Purpose: a short “how we run work now” doc so the process lives in-repo, not in your head.

### Roles

- **Steward / human**: SELECTION and CONTROL-CLOSEOUT authority (see `docs/SOP/MVP1_FRONTIER.md`).
- **Relay** (`scripts/relay_runtime_v0.py`): hard gate — stages jobs, validates §14 payload, emits §15 decision.
- **Orchestrator** (`ppe-orchestrator-acp`, sibling repo): driver — creates worktrees, runs ACP workers, watches time, retries when relay allows.
- **Worker** (`agent acp` session): does the slice work and writes `relay_result.json`.

### One-slice default workflow (day-to-day)

From repo root:

1. Ensure the work is referenced in the live frontier `docs/SOP/MVP1_FRONTIER.md` (MVP1 language).
2. Run:
   - `run_slice.cmd <sliceId>`
3. Orchestrator will:
   - create a per-slice worktree
   - call relay `stage run_selected_slice_v1`
   - run ACP worker in that worktree
   - wait for `artifacts/relay/runs/<run_id>/relay_result.json`
   - call relay `resume`

### Phase workflow (sequential)

1. Ensure a canonical plan exists under `docs/SOP/PHASE_PLANS/`.
2. Run:
   - `run_phase.cmd docs/SOP/PHASE_PLANS/phase2_next.json`
3. Phase runner stops on first non-CONTINUE.

### Artifacts (where to look)

- **Relay run artifacts**:
  - `artifacts/relay/state/current_job.json`
  - `artifacts/relay/runs/<run_id>/task_envelope.json`
  - `artifacts/relay/runs/<run_id>/relay_result.json`
  - `artifacts/relay/runs/<run_id>/decision.json`
- **Orchestrator state**:
  - `artifacts/orchestrator/acp_state.json` (progress + results; written early so crashes still leave breadcrumbs)
- **Last run report (wrapper completion)**:
  - `artifacts/orchestrator/LAST_RUN_REPORT.json` + `artifacts/orchestrator/LAST_RUN_REPORT.md` (written by `run_slice.cmd` / `run_phase.cmd` / `run_phase_raw.cmd` on exit)
  - `artifacts/orchestrator/ACTIVE_RUN.json` (present only while a wrapper-launched slice/phase is in-flight)
  - Optional: set `PPE_NOTIFY=0` to disable Windows toast/beeps from `scripts/notify_run_finished.ps1`
- **UI smoke** (when applicable):
  - `artifacts/ui_smoke/<timestamp>/...`

### Feedback loop (what gets updated after a run)

- If relay returns **CONTINUE**: steward performs CONTROL-CLOSEOUT and updates canonical steering docs (typically `docs/SOP/MVP1_FRONTIER.md`).
- If relay returns **RETRY_ALLOWED**: orchestrator re-runs the worker (max 2 attempts total).
- If relay returns **STOP_FOR_REVIEW** or **BLOCKED**: stop; steward decides whether to open RECOVERY, adjust slice scope, or defer.

### Promotion caveat (common STOP_FOR_REVIEW procedural case)

Relay may return **STOP_FOR_REVIEW** (even when BUILD + tests + artifacts are green) when **promotion cannot be performed** from the worker worktree. This happens when the baseline branch is checked out elsewhere (git refuses fast-forward/branch moves across worktrees).\n+\n+Steward action:\n+- perform promotion from the checkout that currently owns the baseline branch, and\n+- record the closeout in `docs/SOP/MVP1_FRONTIER.md` with pointers to the relay run artifacts.

### Audits (lightweight, repeatable)

Use these as quick “are we drifting?” checks:

- **Context-budget bands**: see `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md` (NORMAL/WATCH/ESCALATE).
- **Plane discipline**: single-plane per execution step (`docs/SOP/OPERATING_RULES.md`).
- **Worktree isolation**: one slice = one worktree; never run two workers in the same worktree concurrently.

### Upgrade posture (relay / orchestrator)

- Treat relay/orchestrator changes as **bounded slices** (usually EVIDENCE-PLANE or CONTROL-PLANE) with explicit acceptance evidence.
- Avoid “silent upgrades” bundled into product work; they confuse plane discipline and make postmortems harder.

### Cleanup (prevent mess accumulation)

- Worktree pruning (safe default): `powershell -File scripts/cleanup_orchestrator_worktrees.ps1 -Keep 3` (dry run) or add `-Force` to delete.
- Relay/artifact folders are intentionally persistent for audit/replay; prune only when you have a clear retention policy.

