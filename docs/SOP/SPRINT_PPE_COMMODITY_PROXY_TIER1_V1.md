# PPE commodity proxy tier-1 v1 — relay sprint spec

**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Manifest:** [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)  
**SELECTION:** [`POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md`](POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md)

---

## Sprint intent

Enable **GLD, SLV, USO** ETF options via equity adapter with `asset_class: commodity_proxy` and honest catalog labels.

---

## Slice acceptance

| Slice | Deliverable |
|-------|-------------|
| PPE-CommProxy-Control-Slice001 | Charter |
| PPE-CommProxy-Core-Slice002 | Registry + MSOS copy uses proxy labels from payload |
| PPE-CommProxy-Witness-Slice003 | Per-ETF witness |
| PPE-CommProxy-Closeout-Slice004 | Evidence COMPLETE |

---

## Non-goals

- CME GC/SI/CL native chains (see `ppe_cme_commodity_v1`)
