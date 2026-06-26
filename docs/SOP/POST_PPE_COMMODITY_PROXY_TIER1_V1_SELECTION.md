# PPE commodity proxy tier-1 v1 — SELECTION

**Chapter:** `ppe_commodity_proxy_tier1_v1`  
**Display name:** Commodity ETF options (GLD, SLV, USO)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json`](PHASE_PLANS/ppe_commodity_proxy_tier1_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md`](SPRINT_PPE_COMMODITY_PROXY_TIER1_V1.md)

---

## Status

**SELECTED** 2026-06-26 — batch chapter #6 (commodity proxies).

**Blocked until:** `ppe_tradeable_universe_v1` **COMPLETE**.

**Assets:** GLD, SLV, USO — `asset_class: commodity_proxy`, `venue: equity` (yfinance ETF options).

**Honesty rule:** UI labels must say **ETF options**, not COMEX/CME futures.

**First slice:** `PPE-CommProxy-Control-Slice001`

---

## Next chapter (deferred)

[`POST_PPE_CME_COMMODITY_V1_SELECTION.md`](POST_PPE_CME_COMMODITY_V1_SELECTION.md) — **LOW / validation-gated**
