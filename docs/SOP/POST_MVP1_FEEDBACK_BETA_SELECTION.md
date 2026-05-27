# Post–MVP1 feedback + beta instrumentation — steward SELECTION (prep)

**Status:** Feedback + beta instrumentation chapter **COMPLETE** (2026-05-27) — see [`MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md`](MVP1_FEEDBACK_BETA_INSTRUMENTATION_EVIDENCE_STATUS.md).

## Deferred BUILD candidates

| Candidate | When to prefer |
|-----------|----------------|
| **Sprint 003 evidence-plane** ([`SPRINT_003_PHASE_2.md`](SPRINT_003_PHASE_2.md)) | Relay/control-plane hardening when pilot pressure returns; requires phase plan under `docs/SOP/PHASE_PLANS/` before queue `READY` |
| **Phase 3 commercial wrapper** | New charter |
| **Steward VPS CTA + outreach** | Commercial loop (not agent BUILD) |

**Steward parallel:** VPS `.env` CTA **pending**; §15F spot-check **pending**; paid-interest **N**.

## Relay run (when SELECTION picks a chapter)

1. Create or confirm phase plan under `docs/SOP/PHASE_PLANS/`.
2. Set queue item to **`READY`** in [`PHASE_QUEUE.json`](PHASE_QUEUE.json) (or run `ppe_auto_select.py --apply` after prior chapter closeout).
3. Set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) — `phasePlanPath`, `sprintSpecPath`, `status: READY` (or `run_ppe.cmd` auto-select).
4. Run `run_ppe.cmd` from repo root (or `run_ppe.cmd --continuous` for back-to-back chapters while queue has `READY` items).
5. After exit: `artifacts/orchestrator/LAST_RUN_REPORT.md` → new Cursor thread with `AGENT_CONTINUITY_BRIEF.md` only.
