# PPE asset display parity v1 — relay sprint spec

**Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05  
**Program:** [`PPE_ASSET_DISPLAY_PARITY_PROGRAM_V1.md`](PPE_ASSET_DISPLAY_PARITY_PROGRAM_V1.md)  
**ADR:** [`PPE_ASSET_DISPLAY_PARITY_ADR.md`](PPE_ASSET_DISPLAY_PARITY_ADR.md)  
**Prior chapter:** [`SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md`](SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md) (must be COMPLETE)  
**SELECTION:** [`POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md`](POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Ship **display parity infrastructure** so every enabled registry asset opens in MSOS Strategy Lab **Live** mode with cached repeat loads — no per-asset UI forks.

**Priority:** HIGH — unblocks tier-1 batch chapters (SOL, equities) without MSOS rework.

---

## Technical constraints (binding)

| Rule | Detail |
|------|--------|
| Layer | Cache + depth in `ppe-core`; MSOS read-only prefetch + UX |
| No TS math | Client displays Python JSON only |
| WSGI cache | Process-local TTL; warm after deploy |
| Backward compat | Default BTC behavior unchanged when `?asset=` absent |

---

## Slice acceptance

### PPE-DisplayParity-Control-Slice001 (CONTROL)

- Program + ADR + SELECTION + evidence stub + relay plan

### PPE-DisplayParity-Core-Slice002 (PPE_CORE)

- `display_payload_cache.py` wired into WSGI provider
- `depth=summary|full` on `build_live_distribution_display_payload`
- `scripts/warm_display_payload_cache.py`

### PPE-DisplayParity-Product-Slice003 (MSOS_UI)

- Asset-aware SSR on `strategy-lab/page.tsx`
- Client shell: SSR match → Live; 120s timeout; no premature Sample

### PPE-DisplayParity-Platform-Slice004 (PLATFORM)

- Deploy warm hook in `deploy-vps.yml`
- pytest for cache + cache-control headers

### PPE-DisplayParity-Closeout-Slice005 (CONTROL)

- Evidence COMPLETE; steer to crypto tier1 chapter

---

## Witness (chapter close)

- [ ] `warm_display_payload_cache.py` OK for BTC + ETH + NVDA (mocked or live steward)
- [ ] MSOS `/strategy-lab?asset=NVDA` shows Live when display API healthy
- [ ] Repeat `display.json?asset=NVDA` within TTL served from cache (timing witness optional)
