# PPE CME commodity v1 — SELECTION

**Chapter:** `ppe_cme_commodity_v1`  
**Display name:** CME commodity options (GC, SI, CL) — **DEFERRED**  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_cme_commodity_v1_relay.json`](PHASE_PLANS/ppe_cme_commodity_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_CME_COMMODITY_V1.md`](SPRINT_PPE_CME_COMMODITY_V1.md)

---

## Status

**CHARTERED · DEFERRED** 2026-06-26 — not promoted to READY until validation pull after tier-1 proxy use.

**Rationale:** True COMEX/NYMEX options need a new vendor adapter, contract specs, and trust model. [`ppe_commodity_proxy_tier1_v1`](POST_PPE_COMMODITY_PROXY_TIER1_V1_SELECTION.md) covers gold/silver/oil via ETF options first.

---

## Gates before BUILD

| Gate | Required |
|------|----------|
| `ppe_commodity_proxy_tier1_v1` COMPLETE | yes |
| Validation log: strong+ demand for native futures/options | yes |
| Steward approves CME data vendor + budget | yes |

---

## Seed instruments (when SELECTION'd)

| ID | Instrument | Venue |
|----|------------|-------|
| GC | Gold futures options | cme |
| SI | Silver futures options | cme |
| CL | Crude oil futures options | cme |

---

## Non-goals until SELECTION

- Any BUILD slices beyond Control charter
- Replacing ETF proxies without operator approval
