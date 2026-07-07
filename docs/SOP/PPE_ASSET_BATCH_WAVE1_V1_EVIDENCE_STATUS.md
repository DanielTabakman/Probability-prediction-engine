# Asset batch wave 1 v1 — evidence status

**Program:** `ppe_asset_batch_wave1_v1`  
**Status:** **IN PROGRESS** (re-charter 2026-06-29; volume order 2026-06-29)  
**SELECTION:** [`POST_PPE_ASSET_BATCH_WAVE1_V1_SELECTION.md`](POST_PPE_ASSET_BATCH_WAVE1_V1_SELECTION.md)

## Baseline (main)

Enabled: BTC, ETH, SOL, NVDA, SPY, QQQ, IWM · Skipped: BNB, XRP · Missing: volume batches 2–4

## Volume batches

| Batch | Chapter | Assets | Status |
|-------|---------|--------|--------|
| **1** | `ppe_equity_universe_tier1a_v1` | SPY, QQQ, IWM | **COMPLETE** |
| 2 | `ppe_equity_universe_tier1b_v1` | TSLA, AMD, AAPL, MSFT, AMZN | BLOCKED (retrospect prod witness not green) |
| 3 | `ppe_equity_universe_tier1c_v1` | COIN, SLV, GLD, GOOGL, META | PENDING |
| 4 | `ppe_commodity_proxy_tier1_v1` | USO | PENDING |

Closeout: ≥20 enabled assets + prod multi-asset witness green.

## Batch-1 retrospect attempt - 2026-07-07

**Decision:** do not promote `ppe_equity_universe_tier1b_v1` yet. Batch-1 catalog/display witnesses are green, and the remaining-id OI refresh completed, but production witness is not green from desktop.

### Green checks

- `python scripts/witness_asset_catalog.py --asset SPY --asset QQQ --asset IWM --json` -> PASS (`catalog_ok=true`, SPY/QQQ/IWM display boundary ok).
- `python scripts/witness_asset_catalog.py --all-enabled --json` -> PASS (`enabled_count=7`, BTC/ETH/SOL/NVDA/SPY/QQQ/IWM display boundary ok).
- Per-asset local summary display builds passed for BTC, ETH, SOL, NVDA, SPY, QQQ, IWM.

### OI refresh

Method: yfinance top 3 expiries, calls + puts `openInterest` sum.

| Rank | Symbol | Open interest |
|------|--------|---------------|
| 1 | TSLA | 676,570 |
| 2 | AMD | 578,870 |
| 3 | COIN | 365,093 |
| 4 | AAPL | 272,621 |
| 5 | SLV | 225,668 |
| 6 | AMZN | 216,342 |
| 7 | MSFT | 182,945 |
| 8 | META | 173,807 |
| 9 | GOOGL | 118,535 |
| 10 | GLD | 112,538 |
| 11 | USO | 91,553 |

Retrospect note: ranks shifted materially versus the 2026-06-29 batch schedule; before promoting batch 2, decide whether to preserve the existing TSLA/AMD/AAPL/MSFT/AMZN relay slice or amend batch composition to the refreshed top five.

### Blocker

- `python scripts/msos_production_multi_asset_witness.py --json` -> FAIL: Python HTTPS verification reports expired `marketstructureos.com` certificate for every enabled asset.
- Unverified HTTPS probe to `https://marketstructureos.com/ppe-display-api/display.json?...` -> FAIL: HTTP 403 for every enabled asset.
- `python scripts/warm_display_payload_cache.py --depth summary --json` exceeded the local 180s command timeout for all enabled assets together, although per-asset summary builds passed individually.

**Next:** repair production witness reachability / certificate path, rerun prod multi-asset witness, then promote `ppe_equity_universe_tier1b_v1` READY if green.
