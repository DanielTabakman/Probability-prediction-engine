# PPE trust surface v1 — SELECTION

**Chapter:** `ppe_trust_surface_v1`  
**Display name:** Trust surface (thin chain + trust notes in MSOS)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §7  
**Relay plan:** [`PHASE_PLANS/ppe_trust_surface_v1_relay.json`](PHASE_PLANS/ppe_trust_surface_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_TRUST_SURFACE_V1.md`](SPRINT_PPE_TRUST_SURFACE_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #6.

**First slice:** `PPE-TrustSurf-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| G-05 honesty | Curated catalog with honest trust labels |
| Equity/index | Dividend not modeled; thin chains on smaller names |
| UX | Traders must see **why** a curve is approximate |

**Blocked until:** `msos_workflow_asset_parity_v1` **COMPLETE** (surfaces exist to attach trust UI).

---

## Acceptance (chapter)

1. Display payload exposes aggregate `trust_state` / per-series trust where applicable.
2. MSOS lab banner for `thin_chain` (amber) — distinct from Sample mode.
3. Catalog `trust_notes` rendered in picker or lab footer for enabled assets.
4. pytest contract for trust fields on mocked thin-chain fixture.
5. Evidence COMPLETE.

---

## Non-goals

- Dividend/discount modeling
- Auto-disable thin assets
- Trust scoring v2 rollups

---

## Next chapter

[`POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md`](POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md)
