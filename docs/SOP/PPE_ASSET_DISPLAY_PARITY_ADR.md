# PPE asset display parity ADR (v1)

**Status:** Accepted (charter — 2026-06-27)  
**Program:** [`PPE_ASSET_DISPLAY_PARITY_PROGRAM_V1.md`](PPE_ASSET_DISPLAY_PARITY_PROGRAM_V1.md)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05

---

## Context

After `ppe_tradeable_universe_v1`, MSOS can **pick** any enabled asset from `catalog.json`, but **display** still behaved like a BTC-first product:

- Next.js SSR always prefetched default BTC `display.json`.
- `ppe_display_api` rebuilt payloads per request with no cross-request cache.
- Equity cold fetches (Yahoo) take 30–120s; the client fell back to **Sample** mode.

Operator expectation: **one infrastructure chapter** — enable asset in registry → same Live UX as BTC.

---

## Decisions (binding)

### 1. WSGI TTL cache (PPE core)

| Item | Detail |
|------|--------|
| Module | `src/viz/display_payload_cache.py` |
| Key | `(asset_id, depth)` |
| TTL | `PPE_DISPLAY_CACHE_TTL_SECONDS` (default 120) |
| Toggle | `PPE_DISPLAY_CACHE_ENABLED` (default on) |
| HTTP | `Cache-Control: public, max-age={ttl}` on successful `display.json` |

Streamlit `@st.cache_data` does not survive WSGI worker requests; this cache is process-local for `ppe_display_api`.

### 2. Display depth query param

| Value | Behavior |
|-------|----------|
| `full` (default) | All expiries (lab chart behavior) |
| `summary` | Cap expiries (`DISPLAY_SUMMARY_MAX_EXPIRIES`, default 5) for warm / smoke |

MSOS lab continues to request full depth; warm script may use full to populate production cache.

### 3. Deploy warm

After VPS deploy recreates `ppe_display_api`, run:

```bash
python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765
```

Non-fatal on failure (logged); first user hit may still be cold.

### 4. MSOS SSR + client (read-only)

| Layer | Change |
|-------|--------|
| `strategy-lab/page.tsx` | Prefetch `fetchDisplayPayload(assetId)` from `?asset=` |
| `StrategyLabClientShell` | Live when SSR payload matches; Loading until client confirm or timeout |
| `ppeDisplayPayload.ts` | 120s fetch timeout (`DISPLAY_PAYLOAD_FETCH_TIMEOUT_MS`) |

No TypeScript math; display JSON remains Python SSOT.

---

## Consequences

- Repeat loads within TTL are fast for all enabled assets.
- First cold load after deploy depends on warm script + vendor latency.
- Cache is per worker process; recreate clears it (warm restores).
