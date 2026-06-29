# MSOS forward consistency radar v1 — SELECTION

**Chapter:** `msos_forward_consistency_radar_v1`  
**Display name:** Forward consistency radar (MSOS dashboard)  
**Program:** [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**Registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) · `forward_consistency`  
**Relay plan:** [`PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json`](PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_FORWARD_CONSISTENCY_RADAR_V1.md`](SPRINT_MSOS_FORWARD_CONSISTENCY_RADAR_V1.md)

---

## Status

**SELECTED** 2026-06-29 — operator-approved relay ch.2 (paired with ch.1).

**First slice:** `MSOS-FCR-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| PPE dashboard payload | Required from ch.1 — one API fetch for heatmap |
| Operator need | Distinguish BAD_DATA vs WATCH without opening Strategy Lab |
| Ship-to | OPERATOR first — internal / ops nav |

**Blocked until:** `ppe_forward_consistency_radar_v1` merged to `main`.

---

## Acceptance (chapter)

1. Route `/forward-consistency` — summary cards, heatmap, selected cell detail, raw JSON drawer.
2. Heatmap from single `dashboard.json` fetch (enabled assets × expiries).
3. Cell click → synthetic/future/edge/flags/reason (read-only).
4. Copy per program doc — research only, not a trade signal.
5. pytest coverage for page render + fixture dashboard.
6. Evidence doc COMPLETE.

---

## Non-goals

- Dislocation tape / timeline (chapter 4)
- Monitor trust hook (T4 — defer until trader validation)
- PPE math in TypeScript

---

## Next (program)

Chapter 3 `ppe_forward_consistency_collector_v1` — **deferred** until T3 archive charter separately approved.
