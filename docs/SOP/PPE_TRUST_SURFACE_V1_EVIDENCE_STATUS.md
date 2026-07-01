---
archived: true
chapter_id: ppe_trust_surface_v1
closed: 2026-06-28
---

# PPE trust surface v1 — evidence status

**Chapter:** `ppe_trust_surface_v1`  
**Status:** **COMPLETE** 2026-06-28 (SELECTED 2026-06-27; promoted READY 2026-06-28)  
**SELECTION:** [`POST_PPE_TRUST_SURFACE_V1_SELECTION.md`](POST_PPE_TRUST_SURFACE_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_trust_surface_v1_relay.json`](PHASE_PLANS/ppe_trust_surface_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-TrustSurf-Control-Slice001 | **COMPLETE** | Trust field contract (this doc §Trust field contract) |
| PPE-TrustSurf-Core-Slice002 | **COMPLETE** | Per-row trust_state + payload aggregation |
| PPE-TrustSurf-Product-Slice003 | **COMPLETE** | MSOS thin-chain/degraded banners + catalog trust_notes in picker |
| PPE-TrustSurf-Closeout-Slice004 | **COMPLETE** | Chapter close |

---

## Trust field contract

Binding contract for chapter slices 002–003. MSOS must surface honest trust labels; Sample mode remains distinct from thin-chain Live.

### `trust_state` (display payload)

| Value | Meaning | MSOS treatment |
|-------|---------|----------------|
| `ok` | Chain depth and quotes sufficient for displayed curve | No trust banner |
| `thin_chain` | One or more export rows flagged thin; curve is approximate | Amber lab banner in Live mode (not Sample) |
| `degraded` | Fetch/quote errors or partial chain on one or more rows | Amber/degraded banner; copy references approximate curve |

**Payload locations (both required for Core-Slice002 parity):**

- Top-level: `display.json.trust_state`
- Mirror: `display.json.meta.trust_state`

**Aggregation rule** (canonical — [`embed_display_boundary.py`](../../src/viz/embed_display_boundary.py)):

1. Collect per-row `trust_state` from export rows (default row value: `ok`).
2. If any row is `thin_chain` → aggregate **`thin_chain`**.
3. Else if any row is `error`, `fail`, or `degraded` → aggregate **`degraded`**.
4. Else → **`ok`**.

Per-row `trust_state` source of truth for Core-Slice002: set on export rows where chain depth or quote quality warrants `thin_chain` or `degraded` (equity dividend-not-modeled paths may contribute `trust_notes` without changing aggregate unless row flags apply).

### `trust_notes` (catalog / registry)

| Field | Type | Source |
|-------|------|--------|
| `trust_notes` | `string[]` | `config/assets.yaml` per asset; exposed via [`catalog_entry_for_asset`](../../src/data/assets_registry.py) |

**Examples:** `"Dividends not modeled"`, `"Thin options chain — curve approximate"`.

**MSOS treatment (Product-Slice003):**

- Picker or lab footer renders non-empty `trust_notes` for the selected asset.
- `trust_notes` are **informational**; aggregate `trust_state` drives banner severity.

### Distinction from Sample mode

| Signal | Meaning |
|--------|---------|
| Sample mode | No live quotes; fixture/demo payload |
| `thin_chain` Live | Real quotes with insufficient depth — curve still shown with warning |

### pytest contract (Core-Slice003 gate)

- Mocked thin-chain fixture: payload exposes `trust_state: thin_chain` at top-level and under `meta`.
- Catalog API includes `trust_notes` array for assets that declare them in registry.

---

## Witness checklist (chapter closeout)

- [ ] `pytest` contract for trust fields on mocked thin-chain fixture
- [x] MSOS lab banner for `thin_chain` (amber) — distinct from Sample mode
- [x] Catalog `trust_notes` rendered in picker or lab footer for enabled assets
- [ ] Evidence COMPLETE
