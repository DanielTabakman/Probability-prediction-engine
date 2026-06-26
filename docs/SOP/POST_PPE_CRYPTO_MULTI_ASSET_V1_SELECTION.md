# PPE crypto multi-asset v1 — SELECTION

**Chapter:** `ppe_crypto_multi_asset_v1`  
**Display name:** Deribit crypto expansion (BTC + ETH)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — Guide G-05 (bounded multi-asset)  
**Relay plan:** [`PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json`](PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md`](SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md)

---

## Status

**SELECTED** — workstream **B** of [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md).

**First slice:** `PPE-CryptoMA-Control-Slice001`

## SELECTION rationale (2026-06-25)

| Input | Decision |
|-------|----------|
| Operator intent | **Crypto first**, stocks later |
| BTC wedge stability | Reference loop shipped; expansion is parameterization + second currency |
| Venue | **Deribit only** — ETH uses same API as BTC |
| Stocks | **Explicitly out of scope** — see `ppe_equity_options_v1` (deferred) |
| Active demo track | Usable demo **COMPLETE** — workstream B relay (crypto) active |

**First slice:** `PPE-CryptoMA-Control-Slice001`

**Entry evidence (G-05):** Operator SELECTION + ETH UI placeholder already in Command Center fixtures; BTC loop is production witness path.

**Operator:** after manifest READY, run `run_ppe.cmd` or open IDE BUILD starter.

---

## Acceptance (chapter)

1. `config/assets.yaml` registry with `BTC` (default) and `ETH` (Deribit).
2. Parameterized Deribit fetch path — no duplicate `fetch_deribit_eth_*` copy-paste.
3. Asset-keyed caches — switching asset cannot serve stale BTC data.
4. Streamlit implied lab: asset selector; BTC default unchanged.
5. `distribution_display_boundary` payload includes `asset: { id, label, venue }`.
6. MSOS Strategy Lab: asset selector or query param; axis/copy driven from payload.
7. Witness: ETH smoke + production demo witness; BTC regression green.
8. Evidence doc complete.

---

## Non-goals

- Equities / LEAPS / yfinance options
- Third+ crypto currencies (SOL, etc.) without follow-on SELECTION
- Polymarket / event markets as same chart
- MSOS entitlements per asset
- Auto-trade or execution
