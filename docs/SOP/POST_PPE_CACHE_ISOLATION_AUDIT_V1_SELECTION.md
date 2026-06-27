# PPE cache isolation audit v1 — SELECTION

**Chapter:** `ppe_cache_isolation_audit_v1`  
**Display name:** Cache isolation audit (asset-key witness suite)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §4  
**Relay plan:** [`PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json`](PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_CACHE_ISOLATION_AUDIT_V1.md`](SPRINT_PPE_CACHE_ISOLATION_AUDIT_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #3.

**First slice:** `PPE-CacheIso-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Enablement gate #5 | Cache isolation — `asset_id` in all option caches |
| Scale risk | Warm BTC cache serving wrong ticker on asset switch |
| Display parity | WSGI cache keyed; Streamlit/vendor caches un audited |

**Blocked until:** `ppe_asset_enablement_pipeline_v1` **COMPLETE** (witness groups define test matrix).

---

## Acceptance (chapter)

1. Cache inventory doc section in ADR or [`PPE_CACHE_ISOLATION_AUDIT_V1_EVIDENCE_STATUS.md`](PPE_CACHE_ISOLATION_AUDIT_V1_EVIDENCE_STATUS.md).
2. Fixes for any cache missing `asset_id` key (minimal diffs).
3. `tests/test_cache_isolation_witness.py` — parametrized cross-asset isolation (mocked I/O).
4. Enablement pipeline requires isolation pytest green for batch group.
5. Evidence COMPLETE.

---

## Non-goals

- Redis / shared cache layer
- Performance optimization beyond key correctness

---

## Next chapter

[`POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md`](POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md)
