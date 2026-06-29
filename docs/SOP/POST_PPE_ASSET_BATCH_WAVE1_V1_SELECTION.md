# Asset batch wave 1 v1 — SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-06-29 (volume order amendment 2026-06-29)  
**Program:** [`PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md`](PPE_ASSET_BATCH_WAVE1_V1_EVIDENCE_STATUS.md) · [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md)

---

## Problem

Tier-1 chapters were closed on paper (`DONE` / evidence `COMPLETE`) while registry enablement never shipped (SPY/QQQ/IWM etc. missing on `main`).

## SELECTION decisions

| # | Action | Rationale |
|---|--------|-----------|
| 1 | **Volume-ordered batches** — rank by summed options OI (yfinance, top 3 expiries) | Most-traded names first; same method for wave 2 when promoted |
| 2 | **Batch 1 due now** — `ppe_equity_universe_tier1a_v1` (SPY, QQQ, IWM) | OI ranks #1–#3 among remaining tier-1 ids |
| 3 | **Retrospect gate** before batch 2 | After batch 1 witness + deploy: review OI ranks, witness friction, cache warm — then promote batch 2 |
| 4 | **Skip BNB/XRP** | `blocked_no_live_options` on Deribit — document skip, do not block wave |
| 5 | **Wave 2 blocked** until wave 1 evidence **COMPLETE** | [`POST_PPE_ASSET_BATCH_WAVE2_V1_SELECTION.md`](POST_PPE_ASSET_BATCH_WAVE2_V1_SELECTION.md) |

---

## Volume batch schedule (wave 1)

Mechanical order uses existing relay chapter ids; asset lists remapped to OI rank (2026-06-29 probe).

| Batch | Chapter | Assets (OI rank) | Gate |
|-------|---------|------------------|------|
| **1** | `ppe_equity_universe_tier1a_v1` | SPY, QQQ, IWM (#1–3) | **DUE NOW** |
| **2** | `ppe_equity_universe_tier1b_v1` | TSLA, AMD, AAPL, MSFT, AMZN (#4–10 singles) | After batch 1 retrospect |
| **3** | `ppe_equity_universe_tier1c_v1` | COIN, SLV, GLD, GOOGL, META | After batch 2 |
| **4** | `ppe_commodity_proxy_tier1_v1` | USO | After batch 3 |

**Retrospect checklist (before batch 2):** re-run OI rank on remaining ids; confirm witness/cache/prod green on SPY/QQQ/IWM; adjust batch 2 list if ranks shifted materially.

**Wave 2 (deferred):** re-chunk [`assets_tier2_manifest.yaml`](../../config/assets_tier2_manifest.yaml) by the same OI method — not `catalog_group` order.

---

## Relay queue (after merge)

| # | Chapter | Assets | Queue |
|---|---------|--------|-------|
| 0 | `ppe_exposure_menu_v1` | NVDA + BTC paths | READY |
| 1 | `ppe_equity_universe_tier1a_v1` | SPY, QQQ, IWM | **DUE** |
| 2 | `ppe_equity_universe_tier1b_v1` | TSLA, AMD, AAPL, MSFT, AMZN | PLANNED (post-retrospect) |
| 3 | `ppe_equity_universe_tier1c_v1` | COIN, SLV, GLD, GOOGL, META | PLANNED |
| 4 | `ppe_commodity_proxy_tier1_v1` | USO | PLANNED |

Agent ritual: [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md) · operator phrase **`asset batch wave 1`**.
