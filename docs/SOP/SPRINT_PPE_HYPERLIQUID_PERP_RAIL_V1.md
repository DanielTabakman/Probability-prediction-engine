# PPE Hyperliquid perp rail v1 — sprint

**Controlling canon:** [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md)  
**Parent program:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)

---

## Sprint intent

Ship **HYPE perp exposure path** on Exposure menu: Hyperliquid public API → Live `perp_long` card. Exposure-only registry row. No execution. No options math.

---

## Preconditions (at SELECTION → READY)

1. Exposure menu v0 **COMPLETE** on `main`.
2. `perp_long` template exists in [`config/exposure_path_catalog.yaml`](../../config/exposure_path_catalog.yaml).
3. Hyperliquid venue documented in [`config/asset_venue_source_map.yaml`](../../config/asset_venue_source_map.yaml).

---

## Acceptance

1. HYPE registry row merged (`enabled: true` after live witness).
2. Probe CLI green for HYPE mark + funding (mocked in CI).
3. Exposure CLI + boundary return Live perp path; `status: ok_perp_only`.
4. MSOS `/exposure` renders HYPE without hardcoded allowlists.
5. `witness_asset_catalog --asset HYPE` green on exposure-only path.
6. No regression on NVDA/BTC exposure paths.
7. Gate green.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **PPE-HyperliquidPerp-Control-Slice001** | EVIDENCE | CONTROL | Evidence stub, relay wired, program linked |
| **PPE-HyperliquidPerp-Core-Slice002** | PRODUCT | PPE_CORE | `fetch_hyperliquid.py`, registry helpers, `exposure_only` gate |
| **PPE-HyperliquidPerp-Exposure-Slice003** | PRODUCT | PPE_CORE | Perp path activation, `ok_perp_only`, probe CLI + tests |
| **PPE-HyperliquidPerp-Product-Slice004** | PRODUCT | MSOS_UI | MSOS card chips (mark/funding), catalog parity test |
| **PPE-HyperliquidPerp-Closeout-Slice005** | EVIDENCE | CONTROL | COMPLETE; venue map + module registry note |

---

## Not now

- Execution rail
- HYPE options venues
- Strategy Lab asset
- Wave 1 batch merge
- Funding time series

---

## Focus playbook

- **Priority tier:** P2 side channel
- **Drift guards:** No execution language; perp path remains `path_not_recommendation`; do not fake options Live pill for HYPE
