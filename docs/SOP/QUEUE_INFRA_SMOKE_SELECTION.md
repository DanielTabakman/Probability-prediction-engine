# Queue infra smoke — steward SELECTION (2026-05-26)

**Status:** **READY** — first chapter-level queue cycle on baseline **`build/msos-live-mirror-title`** (includes viz automation + `run_queue_cycle`).

**Purpose:** Prove mechanical SELECTION → generated phase plan → `ACTIVE_PHASE_MANIFEST` READY → `run_ppe.cmd` → closeout → queue item `DONE`, without product feature work.

**Not in scope:** New implied-lab UI, Phase 2 recovery merge, commercial validation ops.

---

## Chapter

| Field | Value |
|-------|--------|
| **chapterId** | `queue_infra_smoke` |
| **Sprint spec** | [`SPRINT_QUEUE_INFRA_SMOKE.md`](SPRINT_QUEUE_INFRA_SMOKE.md) |
| **Evidence** | [`QUEUE_INFRA_SMOKE_EVIDENCE_STATUS.md`](QUEUE_INFRA_SMOKE_EVIDENCE_STATUS.md) |
| **Queue** | [`SLICE_QUEUE_V1.json`](SLICE_QUEUE_V1.json) item `Q-INFRA-0001` |
| **Baseline** | `build/msos-live-mirror-title` |

---

## Acceptance (chapter)

1. `run_queue_cycle.cmd --dry-run` selects `Q-INFRA-0001` and validates plan shape.
2. `run_queue_cycle.cmd --max-chapters 1` completes with queue item **`DONE`** (or **`BLOCKED`** with actionable `LAST_RUN_REPORT.md`).
3. Targeted pytest on queue cycle tests green before closeout.
4. Evidence doc updated with run IDs and manifest/plan paths.

---

## After closeout

- Push branch when network allows; open/update PR to `main`.
- Enqueue real backlog chapters in `SLICE_QUEUE_V1.json` (replace infra smoke item or add new `PENDING` items).
