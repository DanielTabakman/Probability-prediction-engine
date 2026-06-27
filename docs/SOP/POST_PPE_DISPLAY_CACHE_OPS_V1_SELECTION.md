# PPE display cache ops v1 — SELECTION

**Chapter:** `ppe_display_cache_ops_v1`  
**Display name:** Display cache operations (scheduled warm + health)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §5  
**Relay plan:** [`PHASE_PLANS/ppe_display_cache_ops_v1_relay.json`](PHASE_PLANS/ppe_display_cache_ops_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_DISPLAY_CACHE_OPS_V1.md`](SPRINT_PPE_DISPLAY_CACHE_OPS_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #4.

**First slice:** `PPE-CacheOps-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Display parity | Deploy warm helps boot; TTL still expires |
| Equity cold | 30–120s builds unacceptable on cache miss under traffic |
| Ops | Need visibility into cache age / last warm |

**Blocked until:** `ppe_asset_display_parity_v1` **COMPLETE**.

---

## Acceptance (chapter)

1. Scheduled warm (compose cron, systemd timer, or sidecar) — interval `<` TTL default (120s).
2. Optional `GET /ppe-display-api/cache-status.json` — enabled assets, last warm timestamps.
3. [`PPE_DISPLAY_CACHE_OPS_V1.md`](PPE_DISPLAY_CACHE_OPS_V1.md) runbook (env vars, VPS ops).
4. Deploy workflow documents or invokes scheduled warm hook.
5. Evidence COMPLETE.

---

## Non-goals

- Multi-worker shared cache (Redis)
- MSOS client changes

---

## Next chapter

[`POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md`](POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md)
