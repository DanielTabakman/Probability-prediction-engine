# MSOS workflow asset parity v1 — SELECTION

**Chapter:** `msos_workflow_asset_parity_v1`  
**Display name:** Workflow asset parity (P4→P7 asset propagation)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §6  
**Relay plan:** [`PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json`](PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_WORKFLOW_ASSET_PARITY_V1.md`](SPRINT_MSOS_WORKFLOW_ASSET_PARITY_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #5.

**First slice:** `MSOS-WfAsset-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Milestone | Trader workflow integration — return loop, not one-off lab visit |
| Gap | Strategy Lab asset-aware; confirm/monitor still BTC-default |
| Canon loop | thesis → disagree → express → monitor must preserve asset |

**Blocked until:** `ppe_asset_display_parity_v1` **COMPLETE** (satisfied). **Queue:** runs **immediately after** `ppe_asset_enablement_pipeline_v1` (promoted 2026-06-28 — demo validation signal).

---

## Acceptance (chapter)

1. `?asset=` propagates Strategy Lab → confirm → expression (links + SSR fetch).
2. Thesis / paper trade persistence stores `asset_id`; reload honors it.
3. Monitor/history uses thesis asset for display fetch and spot labels (not hardcoded BTC).
4. Integration tests for NVDA (or SOL) full P4→P7 path with asset param.
5. Evidence COMPLETE.

---

## Non-goals

- New PPE math
- Multi-asset portfolio view
- Entitlements

---

## Next chapter

[`POST_PPE_TRUST_SURFACE_V1_SELECTION.md`](POST_PPE_TRUST_SURFACE_V1_SELECTION.md)
