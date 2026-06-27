# PPE tradeable universe v1 — relay sprint spec

**Controlling canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**ADR:** [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md)  
**Prior chapter:** [`SPRINT_PPE_EQUITY_OPTIONS_V1.md`](SPRINT_PPE_EQUITY_OPTIONS_V1.md) (must be COMPLETE)  
**SELECTION:** [`POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md`](POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Ship **registry v2 + catalog API + witness harness + dynamic MSOS picker** so every follow-on tier-1 chapter is **registry rows + witness**, not cross-layer rewrites.

**Priority:** HIGH — gates all tier-1 asset batch chapters.

---

## Registry schema v2

See [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md). Extend existing `config/assets.yaml` in place; bump `version: 2`.

BTC/ETH remain `enabled: true`. NVDA follows equity chapter enablement.

---

## Technical constraints (binding)

| Rule | Detail |
|------|--------|
| Layer | Registry/catalog in `ppe-core` + `ppe-ui`; MSOS read-only |
| No TS math | Catalog has metadata only |
| Backward compat | Missing v2 fields default sensibly; BTC default unchanged |
| Catalog | Enabled assets only; grouped by `catalog.group` |
| Witness | Required before any new `enabled: true` in batch chapters |

---

## Slice acceptance

### PPE-Universe-Control-Slice001 (CONTROL)

- Program doc + ADR + tier1 manifest + evidence stub
- No runtime behavior change

### PPE-Universe-Core-Slice002 (PPE_CORE)

- Registry v2 helpers in `assets_registry.py`
- Schema migration on `config/assets.yaml` (BTC/ETH/NVDA fields)

### PPE-Universe-Core-Slice003 (PPE_CORE)

- `catalog.json` on display API route
- `witness_asset_catalog.py` scaffold (BTC/ETH/NVDA paths)

### PPE-Universe-UI-Slice004 (PPE_UI)

- `lab_asset_selection.py` uses `list_enabled_asset_ids()` only

### PPE-Universe-Product-Slice005 (MSOS_UI)

- Fetch `catalog.json`; grouped asset picker
- Remove `SUPPORTED_LAB_ASSET_IDS` as hard gate; keep type ergonomics via catalog

### PPE-Universe-Platform-Slice006 (PLATFORM)

- Deploy / Caddy path for `catalog.json` if needed
- `msos_production_demo_witness.py` catalog smoke

### PPE-Universe-Witness-Slice007 (CONTROL)

- pytest for registry, catalog JSON shape, witness script
- MSOS catalog integration test

### PPE-Universe-Closeout-Slice008 (CONTROL)

- Evidence COMPLETE; frontier steer to crypto tier1 chapter

---

## Non-goals

- Batch-enable tier-1 manifest assets
- Search UI (optional follow-up if >8 assets before batch chapters land)

---

## Sprint status

**IN PROGRESS** — UI-Slice004 CLOSED; Product-Slice005 MSOS catalog picker next.
