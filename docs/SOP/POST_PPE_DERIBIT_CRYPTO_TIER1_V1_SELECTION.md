# PPE Deribit crypto tier-1 v1 — SELECTION

**Chapter:** `ppe_deribit_crypto_tier1_v1`  
**Display name:** Deribit crypto tier-1 (SOL + BNB + XRP)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json`](PHASE_PLANS/ppe_deribit_crypto_tier1_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_DERIBIT_CRYPTO_TIER1_V1.md`](SPRINT_PPE_DERIBIT_CRYPTO_TIER1_V1.md)

---

## Status

**SELECTED** 2026-06-26 — batch chapter #2 in tradeable universe program.

**Operator priority (2026-06-26):** **SOL first** among new tradables — run immediately after `ppe_tradeable_universe_v1` closeout; defer equity index batches (SPY/QQQ) until SOL witness green.

**Blocked until:** `ppe_tradeable_universe_v1` **COMPLETE**.

**Assets:** SOL (primary), BNB, XRP (from [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml))

**First slice:** `PPE-CryptoT1-Control-Slice001`

---

## Acceptance

1. Registry rows merged (`enabled: false` until witness per asset).
2. Deribit fetch works for each listed currency (skip/delist if not on Deribit).
3. `witness_asset_catalog.py` green per enabled asset.
4. MSOS catalog shows crypto group entries without code changes.
5. Evidence doc COMPLETE.

---

## Non-goals

- Non-Deribit crypto venues
- SOL/BNB/XRP if Deribit delisted — steward documents skip in evidence

---

## Next chapter

[`POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md`](POST_PPE_EQUITY_UNIVERSE_TIER1A_V1_SELECTION.md)
