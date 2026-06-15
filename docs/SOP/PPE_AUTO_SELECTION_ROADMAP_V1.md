# PPE auto-SELECTION roadmap v1

Ordered chapter list in [`PHASE_SELECTION_ROADMAP.json`](PHASE_SELECTION_ROADMAP.json) drives **queue hydration** and **next READY** promotion when the manifest is idle (`COMPLETE`, empty `phasePlanPath`).

## Enable / disable

- **Default:** enabled when `PHASE_SELECTION_ROADMAP.json` exists.
- **Disable:** `PPE_AUTO_ROADMAP=0`
- **Force enable:** `PPE_AUTO_ROADMAP=1`

## Flow

```text
run_ppe.cmd
  → ppe_auto_select (prepare_selection_idle: sync roadmap → queue, **backlog propagate**, optional Cursor steward, bootstrap first pending → READY)
  → relay phase
  → post_relay_continue (chapter closeout)
  → maybe_advance_roadmap_and_select (closed → done, next pending → READY, auto-select)
```

**Cursor steward hook** (optional): when idle and no valid `pending` row after backlog propagation, [`ppe_steward_cursor.py`](../../scripts/ppe_steward_cursor.py) may charter the next chapter (`PPE_AUTO_STEWARD=1`). See [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md).

**Backlog propagation** (default on): [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) → roadmap `pending`. See [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md).

## Roadmap item fields

| Field | Meaning |
|-------|---------|
| `planPath` | Phase plan under `docs/SOP/PHASE_PLANS/` |
| `status` | `done` \| `pending` \| `ready` \| `skipped` |
| `reason` | Steward note (copied to queue) |
| `selectionPrep` | Optional prep doc path |
| `workerMode` | e.g. `deterministic` (queue + `PPE_WORKER_MODE`) |

**Auto-repair:** `ppe_queue_health.repair_roadmap` normalizes backlog vocabulary on the roadmap (`chartered` → `pending`, `blocked` → `skipped`) before propagate/bootstrap. Runs from preflight, `run_ppe.cmd`, and closeout hooks.

Queue mapping: `pending` → `PLANNED`, `ready` → `READY`, `done` → `DONE`.

## CLI

```bash
python scripts/ppe_roadmap_advance.py --repo-root . --sync --apply
python scripts/ppe_roadmap_advance.py --repo-root . --bootstrap --apply
python scripts/ppe_roadmap_advance.py --repo-root . --closed-plan docs/SOP/PHASE_PLANS/foo.json --apply
python scripts/ppe_roadmap_advance.py --repo-root . --full --apply --closed-plan docs/SOP/PHASE_PLANS/foo.json
```

## Continuous operator recipe

```bat
set PPE_WORKER_MODE=deterministic
set PPE_SKIP_ACP=1
run_ppe.cmd --continuous
```

Add new chapters by appending a **pending** row to the roadmap (and a valid phase plan) before the cycle idles.
