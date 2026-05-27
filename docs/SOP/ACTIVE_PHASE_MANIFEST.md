# Active phase manifest

Machine-readable pointer for **`run_ppe.cmd`** (unified full-phase run). Steward updates at **SELECTION**; automation may set **`RUNNING`** / **`COMPLETE`**.

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

- **SELECTION:** steward sets `phasePlanPath`, `sprintSpecPath`, `status: READY` (or `run_ppe.cmd` auto-select from `PHASE_QUEUE.json`)
- **`run_ppe.cmd` start:** sets `RUNNING`
- **Closeout slice CONTINUE:** `post_relay_continue` sets `COMPLETE`, marks the chapter **DONE** in `PHASE_QUEUE.json`, and **clears** `phasePlanPath`
- **Next chapter:** `run_ppe.cmd` / `ppe_auto_select.py` picks the first queue item with `status: READY` (or use `run_ppe.cmd --continuous` for back-to-back chapters)
- **Failed/stopped phase:** steward resets to `READY` or updates plan path

## Steward checklist (SELECTION)

1. Charter chapter → phase plan JSON exists
2. Update this manifest (`READY`)
3. Run `run_ppe.cmd` from repo root (or `run_ppe.cmd --dry-run` first)
4. After exit: read `artifacts/orchestrator/LAST_RUN_REPORT.md`; **new Cursor thread** with `AGENT_CONTINUITY_BRIEF.md` only

See [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md) and [`CONTEXT_RULES.md`](../CONTEXT_RULES.md).
