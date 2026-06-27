# PPE asset display parity program (v1)

**Chapter id:** `ppe_asset_display_parity_v1`  
**SELECTION:** [`POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md`](POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md)  
**ADR:** [`PPE_ASSET_DISPLAY_PARITY_ADR.md`](PPE_ASSET_DISPLAY_PARITY_ADR.md)

---

## Problem

Enabling a new asset in `config/assets.yaml` updates `catalog.json` and the MSOS picker, but Strategy Lab still:

1. Server-renders BTC display data regardless of `?asset=`.
2. Rebuilds display payloads on every WSGI request (no TTL cache).
3. Drops to **Sample** when equity fetches exceed short client timeouts.

---

## Outcome

Any **enabled** asset gets the same MSOS Strategy Lab experience as BTC:

- SSR prefetch for selected asset on first paint.
- Cached repeat loads via `ppe_display_api`.
- Post-deploy warm for all enabled assets.
- **Live** pill when API is healthy; **Loading** during cold fetch (not premature Sample).

---

## Slices (relay)

See [`SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md`](SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md) and [`PHASE_PLANS/ppe_asset_display_parity_v1_relay.json`](PHASE_PLANS/ppe_asset_display_parity_v1_relay.json).

---

## Dependencies

| Chapter | Status |
|---------|--------|
| `ppe_tradeable_universe_v1` | COMPLETE |
| NVDA enabled + picker fix | Shipped 2026-06-27 |

---

## Evidence

[`PPE_ASSET_DISPLAY_PARITY_V1_EVIDENCE_STATUS.md`](PPE_ASSET_DISPLAY_PARITY_V1_EVIDENCE_STATUS.md)
