# Options Horizon region workflow v1 — SELECTION

**Chapter:** `horizon_region_workflow_v1`  
**Display name:** Options Horizon region workflow (MSOS persistence)  
**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**Schema:** [`REGION_INTENT_SCHEMA_V1.md`](../VISION/OPTIONS_HORIZON/REGION_INTENT_SCHEMA_V1.md)  
**Relay plan:** [`PHASE_PLANS/horizon_region_workflow_v1_relay.json`](PHASE_PLANS/horizon_region_workflow_v1_relay.json)  
**Sprint:** [`SPRINT_OPTIONS_HORIZON_REGION_WORKFLOW_V1.md`](SPRINT_OPTIONS_HORIZON_REGION_WORKFLOW_V1.md)

---

## Status

**CHARTERED** 2026-06-27 — closes milestone “region saves to workflow”; **LOW / P2** side channel.

**First slice:** `Horizon-RegionWf-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Vision contract | RegionIntent should persist via MSOS workflow API as `kind: "horizon_region"` |
| v1 gap | `localStorage` only in `horizonRegion.ts` |
| Dependency | Chart polish chapter ships first so persisted regions attach to a credible UI |

**Blocked until:** `horizon_chart_polish_v1` **COMPLETE** (2026-06-28).

---

## Acceptance (chapter)

1. Save/load RegionIntent via MSOS API (user-scoped), with `localStorage` as offline fallback.
2. Deep-link includes `region_id` when a saved region is active.
3. Copy remains simulation-only per [`MSOS_PUBLIC_COPY_V1.md`](MSOS_PUBLIC_COPY_V1.md).
4. pytest or integration test for round-trip save/load (mocked store).
5. Evidence doc COMPLETE.

---

## Non-goals

- Theses nav page (`/theses` remains disabled until separate MSOS program)
- Cross-device sync beyond existing MSOS user store
- Execution or order routing

---

## Next (program)

Deferred H5 overlays: `horizon_replay_scrubber_v1` when archive ≥30 days.
