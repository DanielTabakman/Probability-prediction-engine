# Post–MVP1 disagreement / candidate strip polish — steward SELECTION (prep)

**Status:** Disagreement / candidate strip polish chapter **COMPLETE** — see [`MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`](MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md).

## Deferred BUILD candidates

| Candidate | When to prefer |
|-----------|----------------|
| **Feedback + beta instrumentation** ([`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 6) | **Selected** — collect structured product signal after strip polish + How it works |
| **Sprint 003 evidence-plane** | Control-plane hardening when pilot pressure returns |
| **Phase 3 commercial wrapper** | New charter |
| **Steward VPS CTA + outreach** | Commercial loop (not agent BUILD) |

**Steward parallel:** VPS `.env` CTA **pending**; §15F spot-check **pending**; paid-interest **N**.

## Relay run (when SELECTION picks a chapter)

1. Create or confirm phase plan under `docs/SOP/PHASE_PLANS/`.
2. Set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) — `phasePlanPath`, `sprintSpecPath`, `status: READY` (see [`ACTIVE_PHASE_MANIFEST.md`](ACTIVE_PHASE_MANIFEST.md)).
3. Run `run_ppe.cmd` from repo root (full phase).
4. After exit: `artifacts/orchestrator/LAST_RUN_REPORT.md` → new Cursor thread with `AGENT_CONTINUITY_BRIEF.md` only.
