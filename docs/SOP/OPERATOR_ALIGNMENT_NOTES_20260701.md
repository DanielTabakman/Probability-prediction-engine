# Operator alignment notes (2026-07-01)

**Plane:** CONTROL-PLANE · **Audience:** stewards, operator threads  
**Purpose:** gaps observed after relay finish hardening (#1044) and follow-up passes.

**Direction SSOT:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — pivot `trader-workflow-integration-v1`.

---

## Relay state (as of follow-up pass)

| Item | Status |
|------|--------|
| `msos_strategy_lab_dist_download_v1` | **DONE** (closeout shipped) |
| `msos_forward_consistency_radar_v1` | **DONE** (VM advanced past FCR during recovery) |
| Active VM verdict | `IDE_BUILD` — `MSOS-VisParityV1-Product-Slice002` (`CLOSEOUT_PENDING`) |
| Next BUILD candidate (steering) | `msos_trader_workflow_horizon_nav_v1` |

**Alignment gap:** steering says horizon-nav is next BUILD candidate; relay queue auto-selected **MSOS viz parity v1** chapter. Reconcile in steward pass: either promote horizon-nav in `PHASE_QUEUE.json` or accept viz-parity as spine prerequisite (document in SELECTION).

---

## Closed / mitigated

- **Loop-host env on SSH handoff** — merged #1044 (`call_ppe_operator_local.cmd` before finish).
- **CLOSEOUT_ONLY explicit finish** — `finish_ide_build --finish-handoff`.
- **VM git pull blocked by relay SOP drift** — `fix_vm_operator` resets; follow-up PR adds `--reset-runtime-sop` before pull in `DESKTOP_CONTINUE`.
- **Token audit WATCH** — move relay finish detail to on-demand [`ppe-relay-finish-hygiene.mdc`](../../.cursor/rules/ppe-relay-finish-hygiene.mdc).
- **Duplicate PR #1045** — closed (superseded by #1044).

---

## Open gaps (steward / ops)

### 1. VM `git pull` before handoff (P1 — PR in flight)

**Symptom:** `DESKTOP_CONTINUE` step 2 fails when VM has uncommitted `PHASE_QUEUE.json`, `DEV_CHANGELOG`, etc.  
**Mitigation:** `python scripts/ppe_operator_git_sync.py --reset-runtime-sop` then pull (wired into `DESKTOP_CONTINUE`).

### 2. Desktop worktree / branch hygiene (P1 — process)

**Symptom:** `main` locked by exposure-menu worktree; operator threads run on mixed control-plane + product dirty trees.  
**SOP:** [`PARALLEL_AGENT_CHECKLIST_V1.md`](PARALLEL_AGENT_CHECKLIST_V1.md) — one worktree per slice; operator thread opens from orchestrator worktree or clean `main`.

### 3. `PPE_MSOS_MIRROR_DOC_ID` on VM (P2 — env)

**Symptom:** Google Docs sync errors during closeout (non-fatal).  
**Fix:** set in VM `ppe_operator_near_zero_api.local.cmd` or env per [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md).

### 4. Research archive staleness (P2 — data)

Cross-venue PM, horizon surface, BTC distribution archives stale — separate from relay; charter **research pipeline** thread.

### 5. `relay_decision_reconcile` (P2 — control-plane)

Steward backlog item — formalize when auto-selected chapter ≠ steering `nextBuildCandidate`.

**Hardened plan (2026-07-02):** [`STEERING_COORDINATION_PROGRAM_V1.md`](STEERING_COORDINATION_PROGRAM_V1.md) — charter-ready; high priority in [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) (`steering_coordination_program_v1`). Phase 0 (`ppe_milestone_gate.py`) shipped; Phase 1–3 pending charter.

### 6. `fix_vm_operator` manifest rewind (P2 — control-plane)

**Symptom:** `fix_vm_operator` resets `ACTIVE_PHASE_MANIFEST.json` from `origin/main`, which can **rewind** the active chapter (observed: FCR reappeared after recovery).  
**Mitigation:** prefer `--reset-runtime-sop` + `git pull` when stack is up; reserve `fix_vm_operator` for `STACK_DOWN`.

---

## Direction / SOP recommendations

1. **Spine vs steering:** Add one paragraph to [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md): relay spine order (review loop → dist download → FCR → viz parity → …) vs UX backlog BUILD order — which wins when they diverge (relay queue READY wins until steward retargets `PHASE_QUEUE.json`).

2. **Operator ritual:** After each chapter COMPLETE, run `context_window_closeout.cmd --record` on operator thread; next thread loads only `AGENT_CONTINUITY_BRIEF.md` + `ACTIVE_PRODUCT_DIRECTION.json` (already policy — enforce for long finish sessions).

3. **VM phase mirror:** Prefer `docs/SOP/VM_OPERATOR_PHASE.json` + local status before SSH (merged in #1044 operator-ssh path) — reduces 20-minute SSH spirals.

4. **Between-chapter housekeeping:** WIP on dirty branch (`repo_between_chapter_housekeeping_relay`) — align with `fix_vm_operator` git hygiene; consider one relay slice after every N chapters.

---

## Next operator actions

1. **Relay:** VM may show `MSOS-FCR-Product-Slice002` again after manifest rewind — run `DESKTOP_CONTINUE` after follow-up PR merges; trust VM brief after `git pull` on loop host.
2. Merge follow-up PR (token slim + VM `--reset-runtime-sop`).
3. Steward: reconcile viz-parity vs horizon-nav queue order.
