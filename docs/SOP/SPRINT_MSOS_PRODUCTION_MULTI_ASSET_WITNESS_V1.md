# MSOS production multi-asset witness v1 — relay sprint spec

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**SELECTION:** [`POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md`](POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Post-deploy regression: **every enabled catalog asset** returns healthy `display.json` on production.

---

## Slice acceptance

### MSOS-MultiAssetWit-Control-Slice001 (CONTROL)

- Witness spec + evidence stub

### MSOS-MultiAssetWit-Platform-Slice002 (PLATFORM)

- `scripts/msos_production_multi_asset_witness.py`
- Deploy VPS production-witness job hook

### MSOS-MultiAssetWit-Product-Slice003 (MSOS_UI)

- Optional Playwright Live pill spot check (NVDA + non-BTC crypto)

### MSOS-MultiAssetWit-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE
