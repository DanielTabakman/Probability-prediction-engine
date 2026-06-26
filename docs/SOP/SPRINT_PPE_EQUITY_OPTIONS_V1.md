# PPE equity options v1 — relay sprint spec

**Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-04/G-05  
**Prior chapter:** [`SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md`](SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md) (COMPLETE)  
**Adapter ADR:** [`PPE_EQUITY_OPTIONS_ADAPTER_ADR.md`](PPE_EQUITY_OPTIONS_ADAPTER_ADR.md)  
**Validation brief:** [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md)  
**SELECTION:** [`POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md`](POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Ship **one liquid equity options name** (default **NVDA**) through the same belief → implied distribution → disagreement → expression workflow, with honest trust labeling for chain quality and corporate-action caveats.

**Priority:** P2 — SELECTED 2026-06-26 after crypto multi-asset + usable demo COMPLETE.

---

## Asset registry extension (v1)

File: `config/assets.yaml` — NVDA scaffold (`venue: equity`, `enabled: false` until Core-Slice002).

See [`PPE_EQUITY_OPTIONS_ADAPTER_ADR.md`](PPE_EQUITY_OPTIONS_ADAPTER_ADR.md) for adapter decisions.

---

## Technical constraints (binding)

| Rule | Detail |
|------|--------|
| Layer | Math/fetch in `ppe-core`; lab in `ppe-ui`; shell in `msos-shell` |
| No TS math | MSOS reads `display.json` only |
| Normalization | Equity marks → Deribit-shaped columns for existing engine |
| Backward compat | BTC/ETH Deribit paths unchanged; missing equity stays disabled |
| Trust | Thin chain + dividend caveats surfaced in lab and payload |

---

## Slice acceptance

### PPE-Equity-Control-Slice001 (CONTROL)

- SELECTION record finalized; evidence stub; equity adapter ADR (NVDA registry schema documented; yaml lands Core-Slice002)
- No product behavior change

### PPE-Equity-Core-Slice002 (PPE_CORE)

- `fetch_equity_options.py`; normalize to Deribit-shaped marks
- Enable NVDA in registry; tests with mocked vendor payloads

### PPE-Equity-Core-Slice003 (PPE_CORE)

- Forward/IV for equity; contract multiplier; trust flags
- `distribution_export.py` equity path

### PPE-Equity-UI-Slice004 (PPE_UI)

- Streamlit ticker path; BL + lognormal witness
- Asset selector includes NVDA when enabled

### PPE-Equity-Product-Slice005 (MSOS_UI)

- Ticker selector; dynamic copy from payload metadata

### PPE-Equity-Platform-Slice006 (PLATFORM)

- Embed API `?symbol=NVDA` or `?asset=NVDA` per ADR resolution
- `msos_production_demo_witness.py` equity path

### PPE-Equity-Witness-Slice007 (CONTROL)

- Per-ticker smoke; yfinance flake handling
- Operator checklist in evidence doc

### PPE-Equity-Closeout-Slice008 (CONTROL)

- Evidence doc COMPLETE; validation log update; frontier steer note

---

## Non-goals

- Multi-ticker scanner
- Live broker execution
- Dividend/discount modeling in v1

---

## Sprint status

**IN PROGRESS** — Slices 001–007 CLOSED; Closeout-Slice008 pending.
