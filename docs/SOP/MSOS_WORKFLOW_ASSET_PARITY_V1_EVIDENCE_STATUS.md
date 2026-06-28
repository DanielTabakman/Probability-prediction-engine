# MSOS workflow asset parity v1 — evidence status

**Chapter:** `msos_workflow_asset_parity_v1`  
**Status:** **CHARTERED** (SELECTED 2026-06-27)  
**SELECTION:** [`POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md`](POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json`](PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-WfAsset-Control-Slice001 | IN_PROGRESS | Propagation matrix (Confirm row verified) |
| MSOS-WfAsset-Product-Slice002 | IN_PROGRESS | Confirm asset-aware copy + gap; expression/monitor TBD |
| MSOS-WfAsset-Witness-Slice003 | IN_PROGRESS | Confirm panel asset witness added |
| MSOS-WfAsset-Closeout-Slice004 | PENDING | Chapter close |

## Asset propagation matrix (target)

| Surface | Reads `?asset=` / thesis asset | SSR fetch asset-aware |
|---------|-------------------------------|------------------------|
| Strategy Lab | yes (display parity) | yes |
| Confirm | yes (`?asset=` → `resolveDisplayAssetMeta`) | yes (`fetchDisplayPayloadClient(assetId)`) |
| Expression | partial (`?asset=` fetch; some BTC-hardcoded help copy) | partial (display fetch; strategy suggestion API still BTC-default) |
| Monitor | partial (`thesis.assetId` in feed) | partial |

**Confirm rule (Product-Slice002):** any workflow step that builds trader-facing copy from lab context must pass `resolveDisplayAssetMeta(payload, assetId)` — never rely on payload-only or BTC fixtures after hydration.

**Gap rule:** “The gap” must describe the disagreement in plain language (`buildGapDescription`) — not collapse to a one-word view label when implied range width is missing or zero.
