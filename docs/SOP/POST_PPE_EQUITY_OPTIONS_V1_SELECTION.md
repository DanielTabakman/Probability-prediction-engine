# PPE equity options v1 — SELECTION

**Chapter:** `ppe_equity_options_v1`  
**Display name:** Equity options expansion (single-ticker v1)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-04 → G-05  
**Relay plan:** [`PHASE_PLANS/ppe_equity_options_v1_relay.json`](PHASE_PLANS/ppe_equity_options_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_EQUITY_OPTIONS_V1.md`](SPRINT_PPE_EQUITY_OPTIONS_V1.md)

---

## Status

**SELECTED** — steward SELECTION 2026-06-26 (usable demo + crypto wedge complete; G-04 validation optional signal, not a hard gate).

**First slice:** `PPE-Equity-Control-Slice001`

**Queue order:** after `msos_self_serve_onboarding_v1` closeout.

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| `msos_usable_demo_v1` | **COMPLETE** |
| `ppe_crypto_multi_asset_v1` | **COMPLETE** |
| Operator intent | Equity wedge back on the BUILD table |
| Seed ticker | **NVDA** (default) unless steward overrides at Control slice |

---

## Scope (authorized at SELECTION)

- New adapter: `src/data/fetch_equity_options.py` (yfinance v0 or steward-approved vendor)
- Registry entry per equity symbol in `config/assets.yaml`
- Contract multiplier + dividend trust warnings
- Ticker search in MSOS (not currency dropdown)
- **One ticker** in v1 — no broad equity scanner

---

## Non-goals

- Multi-ticker scanner
- Live broker execution
