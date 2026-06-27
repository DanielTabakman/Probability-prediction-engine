# PPE asset display parity v1 — SELECTION

**Chapter:** `ppe_asset_display_parity_v1`  
**Display name:** Asset display parity (MSOS live mode for every enabled asset)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md) · chapter **#1**  
**ADR:** [`PPE_ASSET_DISPLAY_PARITY_ADR.md`](PPE_ASSET_DISPLAY_PARITY_ADR.md)  
**Relay plan:** [`PHASE_PLANS/ppe_asset_display_parity_v1_relay.json`](PHASE_PLANS/ppe_asset_display_parity_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md`](SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md)

---

## Status

**SELECTED** 2026-06-27 — infrastructure chapter so any **enabled** registry asset behaves like BTC in MSOS Strategy Lab.

**First slice:** `PPE-DisplayParity-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Operator intent | NVDA (and future assets) should open in **Live** mode, not Sample |
| Root cause | BTC-only SSR prefetch; cold WSGI builds; client timeout → Sample |
| Canon | G-05 multi-asset — parity is infrastructure, not per-ticker UI hacks |
| Dependency | `ppe_tradeable_universe_v1` catalog + picker **COMPLETE** |

**Blocked until:** ~~`ppe_tradeable_universe_v1` **COMPLETE**~~ **satisfied** 2026-06-27.

---

## Acceptance (chapter)

1. WSGI TTL cache for `display.json` keyed by `(asset_id, depth)`.
2. Optional `depth=summary|full` on display API (summary caps expiries for fast warm).
3. `scripts/warm_display_payload_cache.py` — in-process or HTTP warm for all enabled assets.
4. Deploy hook runs warm after `ppe_display_api` recreate.
5. MSOS Strategy Lab SSR prefetches `?asset=` on navigation.
6. Client shell keeps **Loading** (not Sample) when SSR payload matches; 120s fetch timeout.
7. pytest for cache + WSGI cache headers; evidence doc COMPLETE.

---

## Non-goals

- Enabling new registry rows (follow-on tier-1 chapters)
- Summary depth in MSOS UI (full depth remains default for lab)
- Entitlements per asset
- Streamlit embed parity beyond shared WSGI cache

---

## Next chapter after closeout

[`POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md`](POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md) (meta infra #2).
