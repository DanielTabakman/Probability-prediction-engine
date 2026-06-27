# PPE Deribit crypto tier-1 v1 — evidence status

**Chapter:** `ppe_deribit_crypto_tier1_v1`  
**Status:** **IN_FLIGHT** 2026-06-27 (SELECTED 2026-06-26)

Promotion-recovery closeout on 2026-06-27 was rolled back: header COMPLETE did not match product state (SOL/BNB/XRP not in `config/assets.yaml`). Relay resumed from Control-Slice001.

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CryptoT1-Control-Slice001 | PENDING | Charter + evidence alignment |
| PPE-CryptoT1-Core-Slice002 | PENDING | Merge tier-1 manifest rows into registry |
| PPE-CryptoT1-Witness-Slice003 | PENDING | `witness_asset_catalog.py` per asset |
| PPE-CryptoT1-Closeout-Slice004 | PENDING | Chapter close |

## Gates

- [x] `ppe_tradeable_universe_v1` COMPLETE
- [x] SELECTION 2026-06-26

## Per-asset witness

- [ ] SOL enabled + witness green
- [ ] BNB enabled + witness green (or documented skip)
- [ ] XRP enabled + witness green (or documented skip)
