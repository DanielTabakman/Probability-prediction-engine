# PPE cache isolation audit v1 — evidence status

**Chapter:** `ppe_cache_isolation_audit_v1`  
**Status:** **CHARTERED** (SELECTED 2026-06-27)  
**SELECTION:** [`POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json`](PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CacheIso-Control-Slice001 | PENDING | Cache inventory |
| PPE-CacheIso-Core-Slice002 | PENDING | Fixes + test_cache_isolation_witness.py |
| PPE-CacheIso-Platform-Slice003 | PENDING | Pipeline hook |
| PPE-CacheIso-Closeout-Slice004 | PENDING | Chapter close |

## Cache inventory (fill at BUILD)

| Module | Key includes asset_id? | Notes |
|--------|------------------------|-------|
| `display_payload_cache.py` | yes | `(asset_id, depth)` |
| `embed_only_lab.py` | TBD | audit at slice 002 |
| `fetch_deribit.py` | TBD | |
| `fetch_equity_options.py` | TBD | |
| Streamlit `@st.cache_data` | TBD | |
