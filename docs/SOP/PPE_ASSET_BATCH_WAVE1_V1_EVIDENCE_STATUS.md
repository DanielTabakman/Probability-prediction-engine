# Asset batch wave 1 v1 — evidence status

**Program:** `ppe_asset_batch_wave1_v1`  
**Status:** **IN PROGRESS** (re-charter 2026-06-29; volume order 2026-06-29)  
**SELECTION:** [`POST_PPE_ASSET_BATCH_WAVE1_V1_SELECTION.md`](POST_PPE_ASSET_BATCH_WAVE1_V1_SELECTION.md)

## Baseline (main)

Enabled: BTC, ETH, SOL, NVDA · Skipped: BNB, XRP · Missing: SPY/QQQ/IWM + volume batches 2–4

## Volume batches

| Batch | Chapter | Assets | Status |
|-------|---------|--------|--------|
| **1** | `ppe_equity_universe_tier1a_v1` | SPY, QQQ, IWM | **DUE** |
| 2 | `ppe_equity_universe_tier1b_v1` | TSLA, AMD, AAPL, MSFT, AMZN | PENDING (retrospect after batch 1) |
| 3 | `ppe_equity_universe_tier1c_v1` | COIN, SLV, GLD, GOOGL, META | PENDING |
| 4 | `ppe_commodity_proxy_tier1_v1` | USO | PENDING |

Closeout: ≥20 enabled assets + prod multi-asset witness green.
