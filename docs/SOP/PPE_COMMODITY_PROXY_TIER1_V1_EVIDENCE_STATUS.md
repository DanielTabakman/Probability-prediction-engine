# PPE commodity proxy tier-1 v1 - evidence status

**Chapter:** `ppe_commodity_proxy_tier1_v1`  
**Program:** [`PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md`](PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md)  
**Status:** **READY_TO_BUILD** (temporary founder acceptance-witness priority override; USO only)

## Scope

This chapter is narrowed to **USO only**. GLD and SLV remain owned by asset-wave batch 3 records and are not claimed shipped here.

## Founder override

Daniel approved temporarily promoting USO ahead of asset-wave batches 2 and 3 so the installed Autobuilder can complete its first genuine end-to-end witness. USO has no special customer-demand claim and is not being elevated as a durable product-strategy priority; it is selected here because it is a small, already-chartered, credential-free PPE change that can use the existing equity-options adapter. This does not mark batches 2 or 3 complete and does not permanently rewrite the asset-wave order. After this witness, product priority returns to founder selection, with Match Horizon intended as the immediate separate follow-on.

## Control-Slice001 evidence

- `config/assets_tier1_manifest.yaml` assigns `ppe_commodity_proxy_tier1_v1` to `assets: [USO]`, `status: queued`, `wave: ppe_asset_batch_wave1_v1`, `volume_batch: 4`.
- `config/assets.yaml` does not contain GLD, SLV, or USO on current main; USO is not already implemented.
- `docs/SOP/PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md` records batch 2 as blocked, batch 3 as pending, and batch 4 as USO pending before this temporary override.
- Historical PR #396 published steering/queue-only closeouts and did not establish current product implementation for tier1b, tier1c, or USO.
- GitHub issue #5376 records the founder priority override and the requirement to prepare, not dispatch or implement, the USO packet.

| Slice | Status |
|-------|--------|
| PPE-CommProxy-Control-Slice001 | COMPLETE |
| PPE-CommProxy-Core-Slice002 | PENDING |
| PPE-CommProxy-Witness-Slice003 | PENDING |
| PPE-CommProxy-Closeout-Slice004 | PENDING |

## Per-asset witness

- [ ] USO - labeled as oil ETF with roll caveat

## Native dispatch packet

`PPE-CommProxy-Core-Slice002` is the selected first dispatchable product slice after the completed control prerequisite. It is bounded to:

- `config/assets.yaml`
- `src/viz/embed_display_boundary.py`
- `scripts/witness_asset_catalog.py`

Forbidden for this packet: unrelated product paths, product-main write, merge authority, publication authority, Match Horizon work, `msos-autobuilder` changes, Autobuilder dry-run/live dispatch, and USO product implementation during preparation.
