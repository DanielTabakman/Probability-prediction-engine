# PPE multi-asset meta infrastructure program v1

**Purpose:** Charter **all cross-cutting infrastructure** so tier-1 asset batches (SOL → ~25 names) ship as **registry row + witness**, not repeated cross-layer fixes.

**As-of:** 2026-06-27 · **Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05 · **Parent program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)

**Master ADR:** [`PPE_MULTI_ASSET_META_INFRA_ADR.md`](PPE_MULTI_ASSET_META_INFRA_ADR.md)

---

## Agent load bundle

| Role | Path |
|------|------|
| Program (charter) | this file |
| Parent program | [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md) |
| Batch policy | [`ASSET_BATCH_EXPANSION_POLICY_V1.md`](ASSET_BATCH_EXPANSION_POLICY_V1.md) |
| Resolve chapter | `python scripts/resolve_sop.py --chapter <chapter_id> --json` |

---

## Problem

Universe v1 (`catalog.json`, registry v2, dynamic picker) proves **one** asset path. Scaling to ~25 enabled names fails without meta layers for:

| Failure mode | Without meta infra |
|--------------|-------------------|
| Live vs Sample | BTC-only SSR; cold WSGI; short client timeout |
| Enablement ritual | Manual per-batch edits; skipped witness steps |
| Cache bleed | Wrong chain on wrong ticker after warm caches |
| Cache cold spikes | TTL expiry after deploy warm |
| Workflow loop | P4→P7 drops `?asset=`; monitor shows BTC spot |
| Trust honesty | `thin_chain` invisible in MSOS |
| Production regressions | Prod witness checks BTC only |

---

## Meta chapter sequence (relay order)

Run **before or alongside** tier-1 batches. Default: finish **#1–#2**, then **#5** (workflow parity), then **#3–#4**; **#6–#7** before program closeout at ~20 assets.

| # | Chapter | Priority | Delivers |
|---|---------|----------|----------|
| 1 | [`ppe_asset_display_parity_v1`](POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md) | **HIGH** | WSGI TTL cache, asset SSR prefetch, deploy warm, Live UX |
| 2 | [`ppe_asset_enablement_pipeline_v1`](POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md) | **HIGH** | Batch witness + scripted enable gate; `--group` witness |
| 5 | [`msos_workflow_asset_parity_v1`](POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md) | **HIGH** | P4→P7 `?asset=` propagation — **queued #2 after enablement** (demo validation) |
| 3 | [`ppe_cache_isolation_audit_v1`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md) | **HIGH** | Asset-keyed cache audit + pytest isolation witnesses |
| 4 | [`ppe_display_cache_ops_v1`](POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md) | **MEDIUM** | Scheduled warm, cache health endpoint, ops runbook |
| 6 | [`ppe_trust_surface_v1`](POST_PPE_TRUST_SURFACE_V1_SELECTION.md) | **MEDIUM** | `trust_state` + `trust_notes` surfaced consistently in MSOS |
| 7 | [`msos_production_multi_asset_witness_v1`](POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md) | **HIGH** | Production witness: catalog + display per enabled asset |

**Then:** tier-1 **content** batches per [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md) (crypto tier1 → equity tier1a/b/c → commodity proxy).

---

## Enablement gate (binding — all batches)

Before any `enabled: true`:

1. **Pipeline** — `enable_asset_batch.py --group X --dry-run` then `--apply` (after chapter #2)
2. **Witness** — `witness_asset_catalog.py --group X [--live]` green
3. **Display parity** — `display.json?asset=X` + MSOS Live pill (chapter #1)
4. **Cache isolation** — pytest isolation green for asset pair in group (chapter #3)
5. **Production** — multi-asset witness includes new group (chapter #7)

---

## Operator artifacts (target state)

| Artifact | Command / path |
|----------|----------------|
| Enable a batch | `python scripts/enable_asset_batch.py --group equity_index --dry-run` |
| Witness group | `python scripts/witness_asset_catalog.py --group equity_index` |
| Warm all enabled | `python scripts/warm_display_payload_cache.py` |
| Cache health | `GET /ppe-display-api/cache-status.json` |
| Isolation CI | `pytest tests/test_cache_isolation_witness.py -q` |
| Prod multi-asset | `python scripts/msos_production_multi_asset_witness.py` |

---

## Source docs (by chapter)

| Chapter | Sprint | SELECTION | Relay | Evidence |
|---------|--------|-----------|-------|----------|
| display parity | [`SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md`](SPRINT_PPE_ASSET_DISPLAY_PARITY_V1.md) | [`POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md`](POST_PPE_ASSET_DISPLAY_PARITY_V1_SELECTION.md) | [`ppe_asset_display_parity_v1_relay.json`](PHASE_PLANS/ppe_asset_display_parity_v1_relay.json) | [`PPE_ASSET_DISPLAY_PARITY_V1_EVIDENCE_STATUS.md`](PPE_ASSET_DISPLAY_PARITY_V1_EVIDENCE_STATUS.md) |
| enablement pipeline | [`SPRINT_PPE_ASSET_ENABLEMENT_PIPELINE_V1.md`](SPRINT_PPE_ASSET_ENABLEMENT_PIPELINE_V1.md) | [`POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md`](POST_PPE_ASSET_ENABLEMENT_PIPELINE_V1_SELECTION.md) | [`ppe_asset_enablement_pipeline_v1_relay.json`](PHASE_PLANS/ppe_asset_enablement_pipeline_v1_relay.json) | [`PPE_ASSET_ENABLEMENT_PIPELINE_V1_EVIDENCE_STATUS.md`](PPE_ASSET_ENABLEMENT_PIPELINE_V1_EVIDENCE_STATUS.md) |
| cache isolation | [`SPRINT_PPE_CACHE_ISOLATION_AUDIT_V1.md`](SPRINT_PPE_CACHE_ISOLATION_AUDIT_V1.md) | [`POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md`](POST_PPE_CACHE_ISOLATION_AUDIT_V1_SELECTION.md) | [`ppe_cache_isolation_audit_v1_relay.json`](PHASE_PLANS/ppe_cache_isolation_audit_v1_relay.json) | [`PPE_CACHE_ISOLATION_AUDIT_V1_EVIDENCE_STATUS.md`](PPE_CACHE_ISOLATION_AUDIT_V1_EVIDENCE_STATUS.md) |
| display cache ops | [`SPRINT_PPE_DISPLAY_CACHE_OPS_V1.md`](SPRINT_PPE_DISPLAY_CACHE_OPS_V1.md) | [`POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md`](POST_PPE_DISPLAY_CACHE_OPS_V1_SELECTION.md) | [`ppe_display_cache_ops_v1_relay.json`](PHASE_PLANS/ppe_display_cache_ops_v1_relay.json) | [`PPE_DISPLAY_CACHE_OPS_V1_EVIDENCE_STATUS.md`](PPE_DISPLAY_CACHE_OPS_V1_EVIDENCE_STATUS.md) |
| workflow asset parity | [`SPRINT_MSOS_WORKFLOW_ASSET_PARITY_V1.md`](SPRINT_MSOS_WORKFLOW_ASSET_PARITY_V1.md) | [`POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md`](POST_MSOS_WORKFLOW_ASSET_PARITY_V1_SELECTION.md) | [`msos_workflow_asset_parity_v1_relay.json`](PHASE_PLANS/msos_workflow_asset_parity_v1_relay.json) | [`MSOS_WORKFLOW_ASSET_PARITY_V1_EVIDENCE_STATUS.md`](MSOS_WORKFLOW_ASSET_PARITY_V1_EVIDENCE_STATUS.md) |
| trust surface | [`SPRINT_PPE_TRUST_SURFACE_V1.md`](SPRINT_PPE_TRUST_SURFACE_V1.md) | [`POST_PPE_TRUST_SURFACE_V1_SELECTION.md`](POST_PPE_TRUST_SURFACE_V1_SELECTION.md) | [`ppe_trust_surface_v1_relay.json`](PHASE_PLANS/ppe_trust_surface_v1_relay.json) | [`PPE_TRUST_SURFACE_V1_EVIDENCE_STATUS.md`](PPE_TRUST_SURFACE_V1_EVIDENCE_STATUS.md) |
| prod multi-asset witness | [`SPRINT_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1.md`](SPRINT_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1.md) | [`POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md`](POST_MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_SELECTION.md) | [`msos_production_multi_asset_witness_v1_relay.json`](PHASE_PLANS/msos_production_multi_asset_witness_v1_relay.json) | [`MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_EVIDENCE_STATUS.md`](MSOS_PRODUCTION_MULTI_ASSET_WITNESS_V1_EVIDENCE_STATUS.md) |

---

## Success criteria (program-level)

1. Adding asset #21 = manifest row + `enable_asset_batch.py --group …` + green witness — **no MSOS code change**.
2. No cross-asset cache bleed in CI isolation suite.
3. Strategy Lab **and** confirm/expression/monitor honor `?asset=` for every enabled name.
4. Production witness covers **all** enabled catalog assets after each deploy.

---

## Autobuilder boundary (binding)

Meta infra ships via **IDE BUILD** on `build/ppe-meta-infra-v1` → PR → merge. It does **not** preempt the VM relay loop.

| Rule | Detail |
|------|--------|
| Queue status | Meta chapters stay **`PLANNED`** until steward promotes after merge |
| Manifest | Do **not** point `ACTIVE_PHASE_MANIFEST` at meta plans while tier-1 content is **RUNNING** |
| Selection | Autobuilder continues **`ppe_equity_universe_tier1a_v1`** (or next content batch) unchanged |
| Desktop | No local `run_ppe.cmd` / relay — merge to `main`; VM pulls on next pass |
