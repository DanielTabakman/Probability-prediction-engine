# Repo housekeeping v1 — SELECTION (pending)

**Chapter:** `repo_housekeeping_v1`  
**Relay plan:** [`PHASE_PLANS/repo_housekeeping_v1_relay.json`](PHASE_PLANS/repo_housekeeping_v1_relay.json)  
**Sprint:** [`SPRINT_REPO_HOUSEKEEPING_V1.md`](SPRINT_REPO_HOUSEKEEPING_V1.md)

## Status

**NOT SELECTED** — pre-chartered in backlog as **`blocked`** after MSOS P4 closeout. Update this file at SELECTION with date and verified preconditions.

## Trigger (charter rationale)

Periodic control-plane hygiene between major product chapters:

- Worktree accumulation under `_worktrees/acp_orchestrator/`
- Queue / roadmap drift after manual edits
- Optional consistency witness before next MSOS or MVP1 chapter

## Preconditions (verify at SELECTION)

| Check | Expected |
|-------|----------|
| MSOS P4 Strategy Lab **COMPLETE** | [`MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md`](MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md) |
| Backlog row | `repo_housekeeping_v1` promoted **`queued`** via `post_relay_continue` |
| Active manifest | Idle or this chapter **READY** after propagation |

## Scope

| In | Out |
|----|-----|
| `ppe_queue_health --apply` | `src/**`, `apps/msos-web/**` |
| Worktree prune (Keep=3) | Artifact bulk delete without retention note |
| `control_plane_consistency_check` | Relay runtime / product features |
| Optional SOP trim (≤1 doc, named in evidence) | Cross-module refactors |

**Layer preset:** `CONTROL` — [`REPO_LAYER_PATH_PREFIXES.json`](REPO_LAYER_PATH_PREFIXES.json)

## Success criteria

1. Evidence doc [`REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md`](REPO_HOUSEKEEPING_V1_EVIDENCE_STATUS.md) — **COMPLETE**
2. Consistency report **passed**
3. Queue health — no unresolved issues (or documented exceptions)

## First slice

`RepoHousekeeping-Control-Slice001` (deterministic relay; no IDE BUILD unless Evidence slice edits scripts).

## Operator

`run_ppe_auto_local_loop.cmd` or `run_ppe_local.cmd` after backlog promotion. All slices deterministic — no `mark_ide_product_ready` unless Evidence slice scope expands.
