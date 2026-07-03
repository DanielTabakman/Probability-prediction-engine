---
archived: true
chapter_id: ppe_deribit_crypto_tier1_v1
closed: 2026-07-03
---

# PPE Deribit crypto tier-1 v1 — evidence status

**Chapter:** `ppe_deribit_crypto_tier1_v1` / **`ppe_sol_bybit_ship_v1`**  
**Status:** **COMPLETE** 2026-07-03 — SOL live via Bybit; BNB/XRP blocked on Deribit delist  
**SELECTED:** 2026-06-26 · **SOL enable:** 2026-06-28 (Bybit adapter) · **Registry merge:** 2026-06-27

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CryptoT1-Control-Slice001 | **CLOSED** | Charter witness |
| PPE-CryptoT1-Core-Slice002 | **CLOSED** | SOL on Bybit; BNB/XRP deribit rows disabled |
| PPE-CryptoT1-Witness-Slice003 | **CLOSED** | Bybit live probe + pytest |
| PPE-CryptoT1-Closeout-Slice004 | **PARTIAL** | SOL enabled; BNB/XRP skip documented |

## Gates

- [x] `ppe_tradeable_universe_v1` COMPLETE
- [x] Registry rows merged
- [x] SOL live options source (Bybit public API)

## Venue routing (2026-06-28)

| Asset | Venue | Live options | Status |
|-------|-------|--------------|--------|
| SOL | **bybit** | ~300+ USDT-settled instruments | **enabled** |
| BNB | deribit | 0 | disabled — skip |
| XRP | deribit | 0 | disabled — skip |

**Steward decision (2026-06-28):** Deribit delisted SOL/BNB/XRP options. **SOL** routes to **Bybit** (`fetch_bybit_options.py`, ~318 live instruments). Ship via **PR #425** branch `build/ppe-sol-bybit-adapter`. Queue: **`ppe_sol_bybit_ship_v1`** READY.

**Deribit check (2026-06-27):** SOL/BNB/XRP option instruments = 0.  
**Bybit check (2026-06-28):** SOL options live; fetch via `src/data/fetch_bybit_options.py`.

## Per-asset witness

- [x] SOL enabled + witness green (Bybit)
- [x] BNB documented skip (0 Deribit instruments)
- [x] XRP documented skip (0 Deribit instruments)

## Verify SOL

```bash
python scripts/probe_asset_data_source.py --asset SOL
python scripts/witness_asset_catalog.py --asset SOL --live
```
