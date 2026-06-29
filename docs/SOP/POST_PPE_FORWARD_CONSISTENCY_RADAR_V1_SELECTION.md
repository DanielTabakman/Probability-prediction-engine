# PPE forward consistency radar v1 — SELECTION

**Chapter:** `ppe_forward_consistency_radar_v1`  
**Display name:** Forward consistency radar (PPE dashboard payload)  
**Program:** [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**Registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) · `forward_consistency`  
**Relay plan:** [`PHASE_PLANS/ppe_forward_consistency_radar_v1_relay.json`](PHASE_PLANS/ppe_forward_consistency_radar_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_FORWARD_CONSISTENCY_RADAR_V1.md`](SPRINT_PPE_FORWARD_CONSISTENCY_RADAR_V1.md)

---

## Status

**SELECTED** 2026-06-29 — operator-approved relay ch.1 (minimum working radar = ch.1 + ch.2).

**First slice:** `PPE-FCR-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Engine + single-cell API | **SHIPPED** — `forward_consistency.py`, `/ppe-display-api/forward-consistency.json` |
| Strategy Lab panel | **SHIPPED** — `ForwardConsistencyPanel` |
| Trust surface | **COMPLETE** — prerequisite satisfied |
| Gap | No heatmap/dashboard payload; operator cannot scan enabled assets × expiries in one fetch |

**Blocked until:** trust surface **COMPLETE** (satisfied).

---

## Acceptance (chapter)

1. `ForwardConsistencyQualityFlag` enum + matrix builder over enabled assets × expiries.
2. `GET /ppe-display-api/forward-consistency/dashboard.json` returns `ForwardConsistencyDashboardPayload`.
3. Fixture `fixtures/forward_consistency_dashboard_v1.json` validates in pytest.
4. Copy remains research-only — no arbitrage branding.
5. Evidence doc COMPLETE.

---

## Non-goals

- MSOS `/forward-consistency` route (chapter 2)
- Daily snapshot collector (chapter 3 — separate archive charter)
- New venue adapters; Deribit path only

---

## Next chapter

[`POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md)
