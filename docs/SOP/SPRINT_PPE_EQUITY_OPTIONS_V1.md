# PPE equity options v1 — relay sprint spec (DEFERRED)

**Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-04/G-05  
**Prior chapter:** [`SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md`](SPRINT_PPE_CRYPTO_MULTI_ASSET_V1.md) (must be COMPLETE)  
**Validation brief:** [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md)  
**SELECTION:** [`POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md`](POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent (when selected)

Ship **one liquid equity options name** (default NVDA) through the same belief → implied distribution → disagreement → expression workflow, with honest trust labeling for chain quality and corporate-action caveats.

**Priority:** LOW — deferred until crypto chapter + validation signal.

---

## Planned slices (do not BUILD until SELECTION)

| sliceId | Preset | Intent |
|---------|--------|--------|
| PPE-Equity-Control-Slice001 | CONTROL | Charter accept; equity adapter ADR stub |
| PPE-Equity-Core-Slice002 | PPE_CORE | `fetch_equity_options.py`; normalize to Deribit-shaped marks |
| PPE-Equity-Core-Slice003 | PPE_CORE | Forward/IV for equity; multiplier; trust flags |
| PPE-Equity-UI-Slice004 | PPE_UI | Streamlit ticker path; BL + lognormal witness |
| PPE-Equity-Product-Slice005 | MSOS_UI | Ticker selector; dynamic copy |
| PPE-Equity-Platform-Slice006 | PLATFORM | Embed API `?symbol=NVDA` |
| PPE-Equity-Witness-Slice007 | CONTROL | Per-ticker smoke; yfinance flake handling |
| PPE-Equity-Closeout-Slice008 | CONTROL | Evidence + validation log update |

---

## Non-goals

- Multi-ticker scanner
- Live broker execution
- Replacing manual G-04 briefs until signal exists

---

## Sprint status

**CHARTERED DEFERRED** — await gates in SELECTION doc.
