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

**Cursor discipline during phase:** steward SELECTION thread ≠ relay BUILD workers (fresh ACP per slice). Do not run a full phase + PR + planning in one IDE chat ([`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) §3.4).

### One-slice workflow

From repo root:

1. Ensure the work is referenced in the live frontier `docs/SOP/MVP1_FRONTIER.md` (MVP1 language).
2. Run:
   - `run_slice.cmd <sliceId>` or `run_ppe.cmd --slice <sliceId>` (requires manifest / `--plan`)
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
4. Wrapper runs `scripts/post_relay_continue.py` after each slice exit `0`; on `CONTINUE` + plan `closeout`, steering docs update automatically, **`PHASE_QUEUE` item marked DONE**, manifest `phasePlanPath` cleared, then MSOS Google Doc sync (best-effort).
5. **Continuous auto-cycle (optional):** `run_ppe.cmd --continuous` runs phases until the queue has no `READY` items, a non-zero exit, or five chapters (configurable via `ppe_run.py --continuous-max`).

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
  - Optional: set `PPE_NOTIFY=0` to disable Windows toast/beeps from `scripts/notify_run_finished.ps1`
- **UI smoke** (when applicable):
  - `artifacts/ui_smoke/<timestamp>/...`
- **Agent continuity** (after closeout job):
  - `docs/SOP/AGENT_CONTINUITY_BRIEF.md`
  - `artifacts/control_plane/continuity_brief.json`
- **MSOS mirror** (after closeout, best-effort):
  - `artifacts/msos_repo_truth_snapshot.md`
  - `artifacts/control_plane/msos_sync_report.json`
  - Google Doc **MSOS Repo Truth** (marker block only) — see [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md)

### Feedback loop (what gets updated after a run)

- If relay returns **CONTINUE** and the slice has phase-plan `closeout`: `post_relay_continue.py` runs `apply_control_closeout_v1` (updates `MVP1_FRONTIER.md`, `HANDOFF.md`, `PPE_INTEGRATED_STATUS.md`, `AGENT_CONTINUITY_BRIEF.md`), marks the chapter **DONE** in `PHASE_QUEUE.json`, clears manifest `phasePlanPath`, then `sync_msos_repo_truth_v1` (MSOS Google Doc only; skip does not fail closeout).
- **`run_ppe.cmd`** (default): runs `ppe_auto_select.py --apply` first — finalizes stale `COMPLETE` manifests, then selects the next `READY` queue item.
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
