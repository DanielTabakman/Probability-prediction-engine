## RELAY_ORCHESTRATOR_RUNBOOK_V1

Purpose: a short “how we run work now” doc so the process lives in-repo, not in your head.

### Roles

- **Steward / human**: SELECTION authority and disposition of `STOP_FOR_REVIEW` / `BLOCKED`. **CONTROL-CLOSEOUT** is automated via relay job `apply_control_closeout_v1` (`RELAY_RUNTIME_V1.md`). For **routine ship to production**, the steward is **not** in the GitHub merge path when checks are green: see [GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md).
- **Relay** (`scripts/relay_runtime_v0.py`): hard gate — stages jobs, validates §14 payload, emits §15 decision.
- **Orchestrator** (`ppe-orchestrator-acp`, sibling repo): driver — creates worktrees, runs ACP workers, watches time, retries when relay allows.
- **Worker** (`agent acp` session): does the slice work and writes `relay_result.json`.

### Unified run (recommended — full phase)

1. **SELECTION:** steward charters chapter → phase plan under `docs/SOP/PHASE_PLANS/`.
2. Set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) (`phasePlanPath`, `sprintSpecPath`, `status: READY`) — see [`ACTIVE_PHASE_MANIFEST.md`](ACTIVE_PHASE_MANIFEST.md).
3. Preflight (optional): `run_ppe.cmd --dry-run`
4. From repo root: **`run_ppe.cmd`** (runs full phase via `run_phase.cmd` + preflight + manifest `RUNNING`).
5. **After exit:** read `artifacts/orchestrator/LAST_RUN_REPORT.md` (includes **Cursor context ritual**); open a **new** Cursor thread with `AGENT_CONTINUITY_BRIEF.md` only — do not paste orchestrator logs into chat. See [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).

Escape hatches: `run_ppe.cmd --plan <path>`, `run_ppe.cmd --slice <sliceId>`, `run_ppe.cmd --status`.

### Chapter queue cycle (mechanical SELECTION)

For unattended chapter runs, maintain [`SLICE_QUEUE_V1.json`](SLICE_QUEUE_V1.json) (chapter-level items with full `slices[]` including closeout).

From repo root:

```bash
run_queue_cycle.cmd --dry-run
run_queue_cycle.cmd --max-chapters 1
run_queue_cycle.cmd --max-chapters 3 --continuous
```

The runner:

1. Pops the first `PENDING` chapter.
2. Writes `docs/SOP/PHASE_PLANS/auto_queue_<queueId>_<ts>.json` and sets [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) to `READY`.
3. Runs `run_ppe.cmd --plan <generated-plan>`.
4. Marks the queue item `DONE` or `BLOCKED` from `LAST_RUN_REPORT.json` + manifest status.

**Hard stops:** `STOP_FOR_REVIEW`, `BLOCKED`, non-zero wrapper exit, or `ACTIVE_RUN.json` already present — the cycle exits; steward fixes the queue item or frontier, then re-runs.

Queue-driven selection is **mechanical**, not judgment-free: it does not replace steward chartering of what enters the queue.

**Cursor discipline during phase:** steward SELECTION thread ≠ relay BUILD workers (fresh ACP per slice). Do not run a full phase + PR + planning in one IDE chat ([`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) §3.4).

### One-slice workflow

From repo root:

1. Ensure the work is referenced in the live frontier `docs/SOP/MVP1_FRONTIER.md` (MVP1 language).
2. Run:
   - `run_slice.cmd <sliceId>` or `run_ppe.cmd --slice <sliceId>` (requires manifest / `--plan`)
3. When `PHASE_PLAN` is set, `run_slice.cmd` writes **`artifacts/control_plane/active_slice_touch_set.json`** via `scripts/relay/write_slice_touch_set.py` (PRODUCT slices must have `touchSet` in the plan JSON).
4. Orchestrator will:
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
4. Wrapper runs `scripts/post_relay_continue.py` after each slice exit `0`; on `CONTINUE` it runs **`verify_slice_touch_set`** before CONTROL closeout, then steering docs update when the slice has a `closeout` block, then **GOOGLE_DOCS_REFRESH** (`cycle-end`: Live Mirror + report; best-effort).

Optional: `run_slice.cmd <sliceId> [sprintSpec] [plane] [phasePlanPath]` or set `PPE_PHASE_PLAN` for the same post-closeout hook.

### Artifacts (where to look)

- **Relay run artifacts**:
  - `artifacts/relay/state/current_job.json`
  - `artifacts/relay/runs/<run_id>/task_envelope.json`
  - `artifacts/relay/runs/<run_id>/relay_result.json`
  - `artifacts/relay/runs/<run_id>/decision.json`
- **Orchestrator state**:
  - `artifacts/orchestrator/acp_state.json` (progress + results; written early so crashes still leave breadcrumbs)
- **Last run report (wrapper completion)**:
  - `artifacts/orchestrator/LAST_RUN_REPORT.json` + `artifacts/orchestrator/LAST_RUN_REPORT.md` (written by `run_slice.cmd` / `run_phase.cmd` / `run_ppe.cmd` on exit; includes context ritual when manifest present)
  - `artifacts/orchestrator/ACTIVE_RUN.json` (present only while a wrapper-launched slice/phase is in-flight)
  - Optional: set `PPE_NOTIFY=0` to disable Windows toast/beeps from `scripts/notify_run_finished.ps1` and `scripts/notify_run_error.ps1`
  - **Agent health gate:** `scripts/ppe_agent_healthcheck.py` (automatic in `run_ppe.cmd`; bypass `PPE_SKIP_AGENT_CHECK=1`) — see [PPE_AGENT_AND_NETWORK_TROUBLESHOOTING.md](PPE_AGENT_AND_NETWORK_TROUBLESHOOTING.md)
  - **Early failure:** orchestrator writes `artifacts/orchestrator/run_alert.json` + toast via `notify_run_error.ps1` (watchdog polls as backup)
  - **Stall watchdog** (default on): `scripts/watch_active_run.py` spawned by `run_phase.cmd` / `run_slice.cmd`
    - **~15m (SUS):** Windows toast via `scripts/notify_run_stalled.ps1` (once per slice)
    - **~30m + 90s (hard):** toast + kill stuck wrapper + manifest `READY` + `artifacts/orchestrator/STALL_REPORT.json`
    - Disable: `set PPE_WATCH=0` before `run_ppe.cmd`
    - Override limits: `PPE_SUS_MINUTES` / `PPE_HARD_MINUTES`
- **UI smoke** (when applicable):
  - `artifacts/ui_smoke/<timestamp>/...`
- **Agent continuity** (after closeout job):
  - `docs/SOP/AGENT_CONTINUITY_BRIEF.md`
  - `artifacts/control_plane/continuity_brief.json`
- **PPE / MSOS live mirror** (after closeout, best-effort):
  - `artifacts/msos_repo_truth_snapshot.md`
  - `artifacts/control_plane/msos_sync_report.json`
  - Google Doc **PPE / MSOS Repo Truth — Live Mirror** (marker block only) — see [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md)

### Feedback loop (what gets updated after a run)

- If relay returns **CONTINUE** and the slice has phase-plan `closeout`: `post_relay_continue.py` runs `apply_control_closeout_v1` (updates `MVP1_FRONTIER.md`, `HANDOFF.md`, `PPE_INTEGRATED_STATUS.md`, `AGENT_CONTINUITY_BRIEF.md`), then `google_docs_refresh_v1` (`cycle-end`: includes Live Mirror sync + `google_docs_refresh_report.md`).
- Before a phase run: `run_ppe.cmd` → `ppe_run.py` runs `google_docs_refresh_v1` (`cycle-start`, WARN-only on failure).
- If relay returns **RETRY_ALLOWED**: orchestrator re-runs the worker (max 2 attempts total).
- If relay returns **STOP_FOR_REVIEW** or **BLOCKED**: stop; steward decides whether to open RECOVERY, adjust slice scope, or defer.

### Promotion caveat (common STOP_FOR_REVIEW procedural case)

Relay may return **STOP_FOR_REVIEW** (even when BUILD + tests + artifacts are green) when **promotion cannot be performed** from the worker worktree. This happens when the baseline branch is checked out elsewhere (git refuses fast-forward/branch moves across worktrees).

Steward action:

- Perform promotion from the checkout that currently owns the baseline branch, then re-run closeout with `--force` if needed.

### Shipping (GitHub)

After relay **CONTINUE** and successful **promotion** to a branch that can merge to **`main`**, the default path to production is:

1. Open (or update) a **pull request** to **`main`**.
2. Enable **auto-merge** so GitHub merges when required checks pass, including the full **CI** workflow (**`CI / pytest`** + **`CI / docker_entrypoint`**) ([GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md)). If that control is greyed out (private + Free), **Label PR automerge** applies **`automerge`** automatically; **Merge on green** merges only when the **entire** `ci.yml` run is `success` (both jobs must pass).
3. **Deploy VPS** runs on the resulting push to **`main`** ([GITHUB_ACTIONS_VPS_DEPLOY.md](../DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md)).

Orchestrator or agents with suitable credentials can enable auto-merge via the GitHub API so the steward does not click **Merge** for routine slices.

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

### Related

- [GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md) — PR auto-merge, branch protection, **`CI / pytest`** and **`CI / docker_entrypoint`**.  
- [PRODUCTION_DEPLOY_PROTOCOL.md](PRODUCTION_DEPLOY_PROTOCOL.md) — `main` + VPS + deploy Action.
