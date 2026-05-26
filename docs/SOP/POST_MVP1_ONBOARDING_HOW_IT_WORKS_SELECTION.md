# Post–MVP1 onboarding / How it works — steward SELECTION (prep)

**Status:** Onboarding / How it works chapter **COMPLETE** — see [`MVP1_ONBOARDING_HOW_IT_WORKS_EVIDENCE_STATUS.md`](MVP1_ONBOARDING_HOW_IT_WORKS_EVIDENCE_STATUS.md).

## Deferred BUILD candidates

| Candidate | When to prefer |
|-----------|----------------|
| **Disagreement / candidate strip polish** ([`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 4) | After users have How it works context |
| **Feedback + beta instrumentation** (§15B slice 6) | When ready to collect structured product signal |
| **Sprint 003 evidence-plane** | Control-plane hardening |
| **Phase 3 commercial wrapper** | New charter |
| **Steward VPS CTA + outreach** | Commercial loop (not agent BUILD) |

**Steward parallel:** VPS `.env` CTA **pending**; §15F spot-check **pending**; paid-interest **N**.

## Relay run (when SELECTION picks a chapter)

1. Create or confirm phase plan under `docs/SOP/PHASE_PLANS/`.
2. Set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) — `phasePlanPath`, `sprintSpecPath`, `status: READY` (see [`ACTIVE_PHASE_MANIFEST.md`](ACTIVE_PHASE_MANIFEST.md)).
3. Run `run_ppe.cmd` from repo root (full phase).
4. After exit: `artifacts/orchestrator/LAST_RUN_REPORT.md` → new Cursor thread with `AGENT_CONTINUITY_BRIEF.md` only.
