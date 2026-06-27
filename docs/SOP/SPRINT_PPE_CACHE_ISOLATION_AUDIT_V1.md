# PPE cache isolation audit v1 — relay sprint spec

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Prove **no cross-asset cache bleed** before ~20 enabled names.

---

## Slice acceptance

### PPE-CacheIso-Control-Slice001 (CONTROL)

- Cache inventory in evidence stub

### PPE-CacheIso-Core-Slice002 (PPE_CORE)

- Fix any missing `asset_id` cache keys (minimal)
- `tests/test_cache_isolation_witness.py`

### PPE-CacheIso-Platform-Slice003 (PLATFORM)

- Enablement pipeline hooks isolation pytest for batch groups

### PPE-CacheIso-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE
