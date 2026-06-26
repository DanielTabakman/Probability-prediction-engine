# PPE equity options adapter ADR (v1 stub)

**Status:** Proposed (charter — Control-Slice001)  
**Chapter:** `ppe_equity_options_v1`  
**Sprint:** [`SPRINT_PPE_EQUITY_OPTIONS_V1.md`](SPRINT_PPE_EQUITY_OPTIONS_V1.md)  
**Validation brief:** [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-04/G-05

---

## Context

Crypto multi-asset v1 threads `asset_id` through Deribit fetch → implied distribution → MSOS display. A **single liquid equity name** (default **NVDA**) must reuse the same belief → distribution → disagreement workflow without porting math to TypeScript or widening MVP1 evidence contracts.

Equity chains differ from Deribit crypto: contract multiplier (100 shares), dividend/corporate-action carry, thinner OI on far-dated LEAPS, and vendor flake (Yahoo Finance).

---

## Decisions (binding for v1 BUILD)

### 1. Seed ticker

| Field | Decision |
|-------|----------|
| Default ticker | **NVDA** (steward may approve alternate single name before Core-Slice002) |
| Scope | One equity `asset_id` in registry — no scanner |

### 2. Data adapter

| Layer | Decision |
|-------|----------|
| Fetch module | `src/data/fetch_equity_options.py` (new) |
| Primary vendor (v1) | **Yahoo Finance** via existing `fetch_yahoo.py` patterns where possible |
| Normalization | Map equity option marks to **Deribit-shaped** columns consumed by `implied_distribution.py` (strike, mark, expiry, underlying) |
| Registry | Extend `config/assets.yaml` with `venue: equity`; `enabled: false` until Core-Slice002 wires fetch |

### 3. Trust and labeling

| Rule | Detail |
|------|--------|
| Thin chain | Surface trust warning when OI/volume below threshold |
| Dividends | **Not modeled** in v1 — explicit trust note in registry + lab copy |
| Corporate actions | Manual steward caveat in evidence witness; no auto-adjust |
| MSOS | Reads `display.json` metadata only — no equity math in TypeScript |

### 4. Layer boundaries

| Work | Path |
|------|------|
| Fetch + normalize | `src/data/` |
| Distribution math | `src/engine/` (unchanged contracts) |
| Streamlit lab | `src/viz/` |
| Strategy Lab shell | `apps/msos-web/` |

---

## Non-goals (v1)

- Multi-ticker equity scanner
- Live broker execution or order routing
- Dividend/discount curve modeling
- Replacing manual G-04 interview briefs

---

## Open questions (resolve in Core-Slice002+)

1. Minimum chain depth for BL curve eligibility on NVDA LEAPS
2. Whether `?symbol=NVDA` aliases existing `?asset=NVDA` on embed API
3. Smoke strategy for yfinance flake (cached fixture vs skip marker)

---

## Acceptance (Control-Slice001)

- ADR committed; NVDA registry schema documented (`enabled: false` until Core-Slice002)
- No runtime behavior change for BTC/ETH Deribit paths
- Evidence doc + charter witness green
