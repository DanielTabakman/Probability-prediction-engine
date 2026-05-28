# Post–Phase 3 commercial wrapper — steward SELECTION prep

**Status:** prep for next BUILD chapter after Phase 3 + Sprint 003 closeout on **`main`**.

**Inputs:** Phase 3 commercial wrapper **COMPLETE** (2026-05-28); Sprint 003 evidence-plane **COMPLETE** (2026-05-27); [`PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md`](PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md).

---

## Candidates

| Candidate | Notes |
|-----------|--------|
| **Post-Phase3 steering + smoke witness refresh** | Sync stale `MVP1_FRONTIER` / integrated status; dual smoke after commercial wrapper + pytest witness — bounded CONTROL/EVIDENCE chapter. |
| Steward VPS CTA + outreach | Parallel commercial loop — not agent BUILD. |
| New product surface / billing | Requires new charter — defer. |

---

## Steward actions

1. Pick chapter → record in [`POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md`](POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md).
2. Add phase plan to [`PHASE_QUEUE.json`](PHASE_QUEUE.json) as **`READY`** (or run `ppe_auto_select` after agent queues it).
3. Set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) via `python scripts/ppe_auto_select.py --apply` when manifest is **COMPLETE**.
