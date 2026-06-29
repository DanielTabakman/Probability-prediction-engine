# Asset batch wave 1 v1 — SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-06-29  
**Program:** [`PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md`](PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md) · [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md)

---

## Problem

Tier-1 chapters were closed on paper (`DONE` / evidence `COMPLETE`) while registry enablement never shipped (SPY/QQQ/IWM etc. missing on `main`).

## Relay order (after merge)

| # | Chapter | Assets | Queue |
|---|---------|--------|-------|
| 0 | `ppe_exposure_menu_v1` | NVDA + BTC paths | READY |
| 1 | `ppe_equity_universe_tier1a_v1` | SPY, QQQ, IWM | PLANNED |
| 2 | `ppe_equity_universe_tier1b_v1` | AAPL…META | PLANNED |
| 3 | `ppe_equity_universe_tier1c_v1` | TSLA, AMD, COIN | PLANNED |
| 4 | `ppe_commodity_proxy_tier1_v1` | GLD, SLV, USO | PLANNED |

Wave 2 blocked until wave 1 evidence **COMPLETE** — [`POST_PPE_ASSET_BATCH_WAVE2_V1_SELECTION.md`](POST_PPE_ASSET_BATCH_WAVE2_V1_SELECTION.md).

Agent ritual: [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md) · operator phrase **`asset batch wave 1`**.
