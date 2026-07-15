# PPE commodity proxy tier-1 v1 - SELECTION

**Chapter:** `ppe_commodity_proxy_tier1_v1`  
**Display name:** Commodity ETF options (USO)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json`](PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md`](SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md)

---

## Status

**Original selection:** 2026-06-26 - commodity-proxy batch chapter.

**Temporary priority override:** 2026-07-15 - USO-only acceptance witness for the installed Autobuilder.

**Completed prerequisite:** `PPE-CommProxy-Control-Slice001`

**Selected native dispatchable slice:** `PPE-CommProxy-Core-Slice002`

**Selected native dispatchable:** true

**Assets:** USO - `asset_class: commodity_proxy`, `venue: equity` (yfinance ETF options).

**Founder override:** USO is temporarily promoted ahead of incomplete asset-wave batches 2 and 3 to prove the installed Autobuilder's first genuine end-to-end witness. Batches 2 and 3 remain incomplete/blocked or pending in the wave evidence; this selection does not permanently redefine asset-wave order.

**Priority note:** USO has no special customer-demand claim and is not being elevated as a durable product-strategy priority. It is temporarily selected because it is a small, already-chartered, credential-free PPE change that can use the existing equity-options adapter and isolate the first installed Autobuilder witness. After this witness, product priority returns to founder selection; Match Horizon remains the intended immediate separate follow-on.

**Excluded from this chapter:** GLD, SLV. They remain under their actual wave/batch records and are not claimed shipped here.

**Honesty rule:** UI labels must say **ETF options**, not COMEX/CME futures.

**Allowed product paths for `PPE-CommProxy-Core-Slice002`:** `config/assets.yaml`, `src/viz/embed_display_boundary.py`, `scripts/witness_asset_catalog.py`

**Forbidden authority:** unrelated paths, product-main write, merge/publication authority, Match Horizon work, and `msos-autobuilder` changes.

**First dispatchable product slice:** `PPE-CommProxy-Core-Slice002`

---

## Next chapter (deferred)

[`POST_PPE_CME_COMMODITY_V1_SELECTION.md`](POST_PPE_CME_COMMODITY_V1_SELECTION.md) - **LOW / validation-gated**
