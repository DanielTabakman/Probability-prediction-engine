# PPE commodity proxy tier-1 v1 — relay sprint spec

**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Manifest:** [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)  
**SELECTION:** [`POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md`](POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md)

---

## Sprint intent

Prepare the first dispatchable product slice for **USO** ETF options via the equity adapter with `asset_class: commodity_proxy` and honest catalog labels.

This sprint is temporarily promoted ahead of asset-wave batches 2 and 3 for the founder acceptance witness in GitHub issue #5376. The override proves one complete installed Autobuilder run-through; it does not close batches 2 or 3 and does not permanently rewrite the asset-wave order.

---

## Slice acceptance

| Slice | Deliverable |
|-------|-------------|
| PPE-CommProxy-Control-Slice001 | USO-only charter/evidence packet and founder priority override |
| PPE-CommProxy-Core-Slice002 | Registry + MSOS copy uses USO proxy labels from payload |
| PPE-CommProxy-Witness-Slice003 | USO witness |
| PPE-CommProxy-Closeout-Slice004 | Evidence COMPLETE |

---

## Non-goals

- CME GC/SI/CL native chains (see `ppe_cme_commodity_v1`)
- GLD or SLV implementation in this chapter; GLD/SLV remain owned by asset-wave batch 3 records.
- Running Autobuilder `build next`, dry-run, or live dispatch.
- Product-main writes, merge authority, publication authority, Match Horizon work, or `msos-autobuilder` changes.
