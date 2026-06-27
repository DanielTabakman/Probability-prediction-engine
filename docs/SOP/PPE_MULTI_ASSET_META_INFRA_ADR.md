# PPE multi-asset meta infrastructure ADR (v1)

**Status:** Accepted (charter — 2026-06-27)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05

---

## Context

[`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md) defines **what** assets ship and **batch chapter** order. Meta infra defines **how** each batch ships without repeating BTC-first mistakes.

MSOS remains display-only; PPE owns fetch, cache, witness, and display JSON.

---

## Decisions (binding)

### 1. Meta infra precedes bulk enablement

Tier-1 **content** chapters (SOL, SPY, AAPL, …) MUST NOT merge `enabled: true` until chapters **#1–#3** are COMPLETE or steward documents an explicit exception in evidence.

### 2. Display parity (chapter 1)

| Item | Detail |
|------|--------|
| WSGI cache | `display_payload_cache.py`; key `(asset_id, depth)` |
| MSOS SSR | `strategy-lab/page.tsx` prefetches `?asset=` |
| Deploy | post-recreate warm via `warm_display_payload_cache.py` |
| Client | 120s timeout; Loading before Sample |

### 3. Enablement pipeline (chapter 2)

| Item | Detail |
|------|--------|
| SSOT script | `scripts/enable_asset_batch.py` |
| Witness groups | `witness_asset_catalog.py --group {catalog_group}` |
| Registry gate | No `enabled: true` without witness JSON artifact |
| Runbook | [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md) |

### 4. Cache isolation (chapter 3)

All option/vendor caches MUST include `asset_id` (or venue+symbol resolved from asset) in cache keys. CI parametrized tests warm asset A then request asset B and assert payload/asset mismatch fails.

Audit scope: `embed_only_lab`, `fetch_deribit`, `fetch_equity_options`, Streamlit `@st.cache_data` wrappers, WSGI display cache.

### 5. Display cache ops (chapter 4)

| Item | Detail |
|------|--------|
| Scheduled warm | compose cron or sidecar; interval `< TTL` |
| Health | optional `GET /ppe-display-api/cache-status.json` |
| Env | `PPE_DISPLAY_CACHE_TTL_SECONDS`, refresh interval documented |

### 6. Workflow asset parity (chapter 5)

`?asset=` (or persisted thesis `asset_id`) MUST propagate:

- Strategy Lab → confirm → expression → monitor/history
- Server fetches use selected asset, not `DEFAULT_LAB_ASSET_ID`
- Paper trades / thesis store `asset_id`; monitor spot labels match

### 7. Trust surface (chapter 6)

Display payloads expose `trust_state` per expiry/series where applicable. MSOS shows catalog `trust_notes` and lab banners for `thin_chain` — no silent downgrade to Sample when chain is thin but valid.

### 8. Production multi-asset witness (chapter 7)

Extend production witness suite: for each enabled asset in `catalog.json`, HTTP 200 on `display.json?asset=X` within SLA; optional Playwright spot paths for BTC + one equity + one crypto non-BTC.

Distinct from legacy [`msos_mcd_production_witness_v1`](POST_MSOS_MCD_PRODUCTION_WITNESS_V1_SELECTION.md) (MCD sign-off) — this chapter is **ongoing regression** after each batch.

---

## Consequences

- More upfront infra slices before ~20 assets; batches become mechanical.
- Steward queue gains 7 meta chapters before/alongside content batches.
- Operator runs one runbook per batch instead of ad-hoc witness/deploy steps.
