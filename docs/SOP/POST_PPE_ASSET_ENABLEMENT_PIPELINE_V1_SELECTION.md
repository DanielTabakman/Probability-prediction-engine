# PPE asset enablement pipeline v1 — SELECTION

**Chapter:** `ppe_asset_enablement_pipeline_v1`  
**Display name:** Asset enablement pipeline (batch witness + scripted gate)  
**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md) · §3  
**Relay plan:** [`PHASE_PLANS/ppe_asset_enablement_pipeline_v1_relay.json`](PHASE_PLANS/ppe_asset_enablement_pipeline_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_ASSET_ENABLEMENT_PIPELINE_V1.md`](SPRINT_PPE_ASSET_ENABLEMENT_PIPELINE_V1.md)

---

## Status

**SELECTED** 2026-06-27 — meta infra chapter #2.

**First slice:** `PPE-EnablePipe-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Operator intent | ~25 assets without repeating NVDA-style manual ritual |
| Universe program | "registry row + witness" promise |
| Risk | Skipped witness steps when batches land fast |

**Blocked until:** `ppe_asset_display_parity_v1` **COMPLETE** (Live UX before bulk enable).

---

## Acceptance (chapter)

1. `witness_asset_catalog.py --group {catalog_group}` and `--manifest-slice {tier1a|tier1b|…}`.
2. `scripts/enable_asset_batch.py` — dry-run → witness → apply `enabled: true` in `config/assets.yaml`.
3. [`ASSET_ENABLEMENT_RUNBOOK_V1.md`](ASSET_ENABLEMENT_RUNBOOK_V1.md) — single operator path.
4. CI gate: diff touching `enabled: true` requires witness artifact or `--group` pass in test.
5. Evidence COMPLETE.

---

## Non-goals

- New fetch vendors
- MSOS picker changes (universe v1 done)
- Auto-enable without steward `--apply`

---

## Next chapter

[`POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md)
