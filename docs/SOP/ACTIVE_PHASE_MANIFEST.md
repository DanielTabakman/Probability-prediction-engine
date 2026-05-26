# Active phase manifest

Machine-readable pointer for **`run_ppe.cmd`** (unified full-phase run). Steward updates at **SELECTION**; [`run_queue_cycle.cmd`](../../run_queue_cycle.cmd) may set **`READY`** from [`SLICE_QUEUE_V1.json`](SLICE_QUEUE_V1.json); `run_ppe.cmd` sets **`RUNNING`**; closeout sets **`COMPLETE`**.

## File

[`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) (tracked in git)

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `phasePlanPath` | For `READY` | Relay phase plan under `docs/SOP/PHASE_PLANS/` |
| `sprintSpecPath` | Recommended | Active sprint spec for the chapter |
| `selectionRecord` | Recommended | POST SELECTION or outcome doc |
| `status` | Yes | `READY` \| `RUNNING` \| `COMPLETE` |
| `notes` | Optional | Steward notes |

## Status transitions

- **SELECTION:** steward sets `phasePlanPath`, `sprintSpecPath`, `status: READY` — or `run_queue_cycle.cmd` sets them from the chapter queue
- **`run_ppe.cmd` start:** sets `RUNNING`
- **Closeout slice CONTINUE:** `post_relay_continue` sets `COMPLETE` when the closeout slice in the plan finishes
- **Failed/stopped phase:** steward resets to `READY` or updates plan path

## Steward checklist (SELECTION)

1. Charter chapter → phase plan JSON exists
2. Update this manifest (`READY`)
3. **Refresh Google Docs** (optional explicit pass): `refresh_google_docs.cmd` — or rely on **cycle-start** refresh when `run_ppe.cmd` starts
4. Run `run_ppe.cmd` from repo root (or `run_ppe.cmd --dry-run` first)
5. After exit: read `artifacts/orchestrator/LAST_RUN_REPORT.md`; **new Cursor thread** with `AGENT_CONTINUITY_BRIEF.md` only
6. After chapter closeout: **cycle-end** refresh runs automatically via `post_relay_continue`; review `artifacts/control_plane/google_docs_refresh_report.md`

See [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md) and [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).
