# PPE display cache ops v1 — relay sprint spec

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md`](POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Keep display cache **warm between TTL expiry** and give operators cache health visibility.

---

## Slice acceptance

### PPE-CacheOps-Control-Slice001 (CONTROL)

- Ops runbook stub + evidence

### PPE-CacheOps-Core-Slice002 (PPE_CORE)

- Optional `cache-status.json` on display API
- Scheduled warm (compose / deploy hook)

### PPE-CacheOps-Platform-Slice003 (PLATFORM)

- [`PPE_DISPLAY_CACHE_OPS_V1.md`](PPE_DISPLAY_CACHE_OPS_V1.md) runbook
- VPS timer or sidecar documented

### PPE-CacheOps-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE
