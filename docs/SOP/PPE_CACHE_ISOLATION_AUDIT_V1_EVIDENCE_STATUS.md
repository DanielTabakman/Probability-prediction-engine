---
archived: true
chapter_id: ppe_cache_isolation_audit_v1
closed: 2026-06-28
---

# PPE cache isolation audit v1 — evidence status

**Chapter:** `ppe_cache_isolation_audit_v1`  
**Status:** **COMPLETE** 2026-06-28 (SELECTED 2026-06-27)  
**SELECTION:** [`POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json`](PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CacheIso-Control-Slice001 | **COMPLETE** | Cache inventory in evidence |
| PPE-CacheIso-Core-Slice002 | **COMPLETE** | `test_cache_isolation_witness.py` + asset-key fixes in fetch/viz |
| PPE-CacheIso-Platform-Slice003 | **COMPLETE** | `enable_asset_batch.py` runs isolation pytest before apply |
| PPE-CacheIso-Closeout-Slice004 | **COMPLETE** | Chapter close 2026-06-28 |

## Cache inventory

| Module | Key includes asset_id? | Notes |
|--------|------------------------|-------|
| `display_payload_cache.py` | yes | `(asset_id, depth)` |
| `embed_only_lab.py` | yes | passes `asset_id` to cached partials |
| `fetch_deribit.py` | yes | diagnostic cache keyed by currency |
| `fetch_equity_options.py` | yes | public API accepts `asset_id` |
| `app_cache.py` wrappers | yes | keyed by `asset_id` param |

## Witness checklist (chapter closeout)

- [x] `pytest tests/test_cache_isolation_witness.py -q` green — 2026-06-28
- [x] `enable_asset_batch.py --group crypto --dry-run` runs isolation gate — 2026-06-28 (#457)
- [x] Cross-asset display payload cache isolation (BTC/ETH) — 2026-06-28
