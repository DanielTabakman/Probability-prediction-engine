# MSOS production multi-asset witness v1 — SELECTION

**Chapter:** `msos_production_multi_asset_witness_v1`  
**Display name:** Production multi-asset witness (catalog + display regression)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §8  
**Relay plan:** [`PHASE_PLANS/msos_production_multi_asset_witness_v1_relay.json`](PHASE_PLANS/msos_production_multi_asset_witness_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1.md`](SPRINT_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #7.

**First slice:** `MSOS-MultiAssetWit-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Batch velocity | Each enable must not break prod for other assets |
| Current gap | `msos_production_demo_witness.py` BTC-centric |
| Deploy | Need post-deploy gate before declaring batch done |

**Blocked until:** `ppe_asset_enablement_pipeline_v1` **COMPLETE** (uses `--all-enabled` / groups).

---

## Acceptance (chapter)

1. `scripts/msos_production_multi_asset_witness.py` — prod HTTP for every enabled catalog asset.
2. SLA timeouts per venue (crypto vs equity); JSON report artifact.
3. Wired into Deploy VPS `production-witness` job (continue-on-error or gate per steward).
4. Optional Playwright: `/strategy-lab?asset=NVDA` Live pill smoke.
5. Evidence COMPLETE.

---

## Non-goals

- Replace MCD sign-off witness ([`msos_mcd_production_witness_v1`](POST_MSOS_MCD_PRODUCTION_WITNESS_V1_SELECTION.md))
- Full e2e journey ([`msos_e2e_product_witness_v1`](POST_MSOS_E2E_PRODUCT_WITNESS_V1_SELECTION.md))

---

## Next chapter

Tier-1 **content** batches — [`POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md) (default backlog order after crypto tier1).
