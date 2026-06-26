# PPE equity options v1 — SELECTION (DEFERRED)

**Chapter:** `ppe_equity_options_v1`  
**Display name:** Equity options expansion (single-ticker v1)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-04 → G-05  
**Relay plan:** [`PHASE_PLANS/ppe_equity_options_v1_relay.json`](PHASE_PLANS/ppe_equity_options_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_EQUITY_OPTIONS_V1.md`](SPRINT_PPE_EQUITY_OPTIONS_V1.md)

---

## Status

**NOT SELECTED** — chartered placeholder only.

### Hard gates (all required before SELECTION)

1. `ppe_crypto_multi_asset_v1` **COMPLETE**
2. `msos_usable_demo_v1` **COMPLETE** + MCD criteria met
3. **G-04 signal:** row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) for NVIDIA/LEAPS or equivalent equity demand
4. Steward approves **one** seed ticker (default: `NVDA`)

### First slice at SELECTION

`PPE-Equity-Control-Slice001`

---

## Scope preview (not authorized until SELECTION)

- New adapter: `src/data/fetch_equity_options.py` (yfinance v0 or steward-approved vendor)
- Registry entry per equity symbol in `config/assets.yaml`
- Contract multiplier + dividend trust warnings
- Ticker search in MSOS (not currency dropdown)
- **One ticker** in v1 — no broad equity scanner

---

## Non-goals

- Multi-ticker scanner
- Live broker execution
- Replacing manual G-04 briefs until signal exists
