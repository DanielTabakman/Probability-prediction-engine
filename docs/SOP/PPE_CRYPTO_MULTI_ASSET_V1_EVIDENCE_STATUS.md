---
archived: true
chapter_id: ppe_crypto_multi_asset_v1
closed: 2026-06-26
---

# PPE crypto multi-asset v1 — evidence status

**Chapter:** `ppe_crypto_multi_asset_v1`  
**Status:** **COMPLETE** 2026-06-26 — SELECTION 2026-06-25 (G-05)  
**SELECTION:** [`POST_PPE_CRYPTO_MULTI_ASSET_V1_SELECTION.md`](POST_PPE_CRYPTO_MULTI_ASSET_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json`](PHASE_PLANS/ppe_crypto_multi_asset_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md`](SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-CryptoMA-Control-Slice001 | **CLOSED** | `config/assets.yaml` registry scaffold; SELECTION finalized |
| PPE-CryptoMA-Core-Slice002 | **CLOSED** | Parameterized Deribit fetch (`currency`); `assets_registry.py`; export `asset_id` |
| PPE-CryptoMA-UI-Slice003 | **CLOSED** | Streamlit selector + embed `asset` payload |
| PPE-CryptoMA-Product-Slice004 | **CLOSED** | MSOS Strategy Lab asset switcher |
| PPE-CryptoMA-Platform-Slice005 | **CLOSED** | Deploy witness + display API query param |
| PPE-CryptoMA-Witness-Slice006 | **CLOSED** | pytest + operator checklist |
| PPE-CryptoMA-Closeout-Slice007 | **CLOSED** | Chapter COMPLETE |

---

## Witness checklist (chapter closeout)

- [ ] BTC implied lab smoke (regression)
- [ ] ETH implied lab smoke
- [ ] `display.json` includes `asset` block for ETH
- [ ] MSOS Strategy Lab ETH selector + labeled chart
- [ ] Production demo witness (BTC + ETH)
- [ ] Trust note visible when ETH BL is thin/noisy

## Operator sign-off

- [ ] Operator walked BTC + ETH in Strategy Lab on production URL
