# PPE tradeable universe ADR (v1)

**Status:** Accepted (charter — 2026-06-26)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**Canon:** [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) — G-05

---

## Context

BTC + ETH ship via `config/assets.yaml` and a parameterized Deribit path. NVDA equity is in flight. Scaling to ~25–30 major tradables fails if every asset requires edits to Python hardcoded lists **and** TypeScript `SUPPORTED_LAB_ASSET_IDS`.

MSOS must remain display-only; PPE owns fetch, normalization, and implied distribution math.

---

## Decisions (binding)

### 1. Registry v2 is SSOT

| Field | Purpose |
|-------|---------|
| `version: 2` | Schema bump on `config/assets.yaml` |
| `asset_class` | `crypto` \| `equity_index` \| `equity_mega` \| `commodity_proxy` |
| `venue` | `deribit` \| `equity` (commodity proxies use `equity` fetcher) |
| `tier` | `core` \| `extended` \| `experimental` |
| `enabled` | `true` only after witness gate passes |
| `catalog.group` | Picker grouping key (see manifest) |
| `spread_width` | Per-asset BL/spread default |
| `trust_notes` | Surfaced in lab + payload |

Staging manifest for tier-1 rows: [`config/assets_tier1_manifest.yaml`](../../config/assets_tier1_manifest.yaml). Relay chapters merge rows into runtime registry.

### 2. Catalog API

| Endpoint | Owner | Consumer |
|----------|-------|----------|
| `GET /ppe-display-api/catalog.json` | PPE embed / display boundary | MSOS Strategy Lab, Streamlit lab |

Response includes `default_asset_id`, grouped enabled assets, labels, `asset_class`, `venue`, `tier`. **No prices or curves in catalog.**

### 3. Enablement gate

`enabled: true` requires `scripts/witness_asset_catalog.py` pass for that asset (fetch, display boundary, optional MSOS smoke). CI may use mocked vendor fixtures; production witness uses live steward spot-check per chapter closeout.

### 4. Venue routing (no per-ticker fetch forks)

| `venue` | Fetch module | Normalization |
|---------|--------------|---------------|
| `deribit` | `fetch_deribit.py` | Native |
| `equity` | `fetch_equity_options.py` | Deribit-shaped marks for engine |

Commodity proxies (GLD, SLV, USO) use `venue: equity` with `asset_class: commodity_proxy` and honest UI labels.

**Agent discovery:** Before enablement or tier-1 batch BUILD, run [`ASSET_DATA_SOURCE_DISCOVERY_V1.md`](ASSET_DATA_SOURCE_DISCOVERY_V1.md) — `scripts/probe_asset_data_source.py` + [`config/asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml).

### 5. MSOS picker

- Fetch `catalog.json` on Strategy Lab load.
- Grouped selector when enabled count > 8; search optional in Product slice.
- Remove hardcoded asset allowlist as **gate**; validate against catalog + `display.json` payload.
- Marketing copy: live market count from catalog, not hand-edited hero strings.

### 6. Layer boundaries

| Work | Path |
|------|------|
| Registry + catalog | `config/`, `src/data/assets_registry.py`, `src/viz/embed_display_boundary.py` |
| Witness | `scripts/witness_asset_catalog.py` |
| MSOS shell | `apps/msos-web/` — read only |

---

## Non-goals

- Multi-ticker scanner or dynamic symbol discovery
- CME vendor integration in universe v1 (separate deferred chapter)
- Entitlements per asset
- Dividend / carry modeling in v1

---

## Open questions (resolve in BUILD)

1. Search UX threshold — 8 vs 12 enabled assets before filter UI
2. Whether `catalog.json` is cached at CDN edge or always `no-store`
3. Experimental tier badge copy in MSOS vs Streamlit only

---

## Acceptance (program infrastructure chapter)

- ADR + program doc + tier1 manifest committed
- Registry v2 schema documented; BTC/ETH backward compatible
- `catalog.json` + `witness_asset_catalog.py` shipped in `ppe_tradeable_universe_v1`
- MSOS reads catalog dynamically
