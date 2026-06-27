# MSOS workflow asset parity v1 — relay sprint spec

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**SELECTION:** [`POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md`](POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Trader workflow loop preserves **selected asset** from lab through monitor — not BTC-default after navigation.

---

## Slice acceptance

### MSOS-WfAsset-Control-Slice001 (CONTROL)

- Asset propagation matrix doc in evidence

### MSOS-WfAsset-Product-Slice002 (MSOS_UI)

- confirm / expression / monitor asset-aware fetch + links
- thesis / paper trade `asset_id` persistence

### MSOS-WfAsset-Witness-Slice003 (CONTROL)

- Integration tests P4→P7 with `?asset=NVDA` (or SOL)

### MSOS-WfAsset-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE
