# PPE Deribit crypto tier-1 v1 — evidence status

**Chapter:** `ppe_deribit_crypto_tier1_v1`  
**Status:** **STAGED** (registry merged; enable blocked — Deribit delist)  
**SELECTED:** 2026-06-26 · **Registry merge:** 2026-06-27

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CryptoT1-Control-Slice001 | **CLOSED** | Charter witness |
| PPE-CryptoT1-Core-Slice002 | **CLOSED** | SOL/BNB/XRP merged `enabled: false` |
| PPE-CryptoT1-Witness-Slice003 | **CLOSED** | Live Deribit check + pytest witness |
| PPE-CryptoT1-Closeout-Slice004 | **BLOCKED** | Enable after Deribit relists options |

## Gates

- [x] `ppe_tradeable_universe_v1` COMPLETE
- [x] SELECTION 2026-06-26
- [x] Registry rows merged from [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml)
- [x] `is_asset_enabled` honors `enabled: false` for crypto staging rows

## Deribit live check (2026-06-27)

Public API `get_instruments` (`kind=option`, `expired=false`):

| Currency | Live option instruments | Index / spot |
|----------|-------------------------|--------------|
| SOL | **0** | `sol_usd` index ~$70; spot `SOL_USDC` |
| BNB | **0** | — |
| XRP | **0** | — |

**Steward decision:** Document **skip enable** per SELECTION non-goals — Deribit has delisted tier-1 crypto options. Rows stay `enabled: false` until relist + `witness_asset_catalog.py --asset SOL --live` green.

## Per-asset witness

- [ ] SOL enabled + witness green — **blocked** (0 Deribit instruments)
- [x] BNB documented skip (0 Deribit instruments)
- [x] XRP documented skip (0 Deribit instruments)

## Enable when ready

```bash
python scripts/witness_asset_catalog.py --asset SOL --live
python scripts/enable_asset_batch.py --asset SOL --apply --live-witness
```
