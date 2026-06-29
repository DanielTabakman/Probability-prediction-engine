# PPE forward consistency radar v1 — SELECTION

**Chapter:** `ppe_forward_consistency_radar_v1`  
**Module:** `forward_consistency` — [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**Registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) · [`PPE_MODULE_REGISTRY.json`](PPE_MODULE_REGISTRY.json)  
**Relay plan:** [`PHASE_PLANS/ppe_forward_consistency_radar_v1_relay.json`](PHASE_PLANS/ppe_forward_consistency_radar_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_FORWARD_CONSISTENCY_RADAR_V1.md`](SPRINT_PPE_FORWARD_CONSISTENCY_RADAR_V1.md)

---

## Status

**SELECTED** 2026-06-29 — module registry chapter for `forward_consistency` (T1 → T3 target).

**First slice:** `PPE-FCR-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| MSOS pillars | **Edge** + **Legibility** — test internal consistency without execution language |
| Trust surface COMPLETE | Operators need cross-asset/expiry view, not only Strategy Lab single cell |
| Engine shipped | Per-cell API + Lab panel exist; gap is aggregated dashboard boundary |
| Archive discipline | T3 collector deferred to follow-on chapter after archive charter approval |

**Blocked until:** `ppe_trust_surface_v1` **COMPLETE** ✓

---

## Integration tier charter (this chapter)

| Field | Value |
|-------|--------|
| Current tier | T1 |
| Target tier (chapter 1 closeout) | T1 complete + dashboard boundary |
| MSOS UI chapter | `msos_forward_consistency_radar_v1` (separate SELECTION after ch.1 merge) |

---

## Acceptance (chapter 1 — `ppe_forward_consistency_radar_v1`)

1. Structured `quality_flags` on forward consistency checks (Python).
2. `ForwardConsistencyDashboardPayload` fixture + WSGI `dashboard.json` route.
3. pytest boundary tests green.
4. Registry JSON + HTML map updated at closeout.
5. Evidence COMPLETE.

---

## Non-goals (chapter 1)

- MSOS `/forward-consistency` page (chapter 2)
- Snapshot collector (chapter 3)
- New venue adapters
- Execution / order-routing language

---

## Next chapter

`msos_forward_consistency_radar_v1` — MSOS heatmap + detail UI (T2).
