# PPE tradeable universe v1 — SELECTION

**Chapter:** `ppe_tradeable_universe_v1`  
**Display name:** Tradeable universe infrastructure (registry v2 + catalog API)  
**Program:** [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md)  
**ADR:** [`PPE_TRADEABLE_UNIVERSE_ADR.md`](PPE_TRADEABLE_UNIVERSE_ADR.md)  
**Relay plan:** [`PHASE_PLANS/ppe_tradeable_universe_v1_relay.json`](PHASE_PLANS/ppe_tradeable_universe_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md`](SPRINT_PPE_TRADEABLE_UNIVERSE_V1.md)

---

## Status

**SELECTED** 2026-06-26 — infrastructure chapter for [`PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md`](PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md).

**First slice:** `PPE-Universe-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Operator intent | Major tradables on MSOS in a reasonable, scalable way |
| BTC/ETH + NVDA path | Proves two venues; batch adds need catalog SSOT |
| MSOS friction | `SUPPORTED_LAB_ASSET_IDS` hardcoding blocks scale |
| Canon | G-05 bounded multi-asset — infrastructure before breadth |

**Blocked until:** ~~`ppe_equity_options_v1` **COMPLETE**~~ **satisfied** 2026-06-26.

**First slice:** `PPE-Universe-Control-Slice001`

---

## Acceptance (chapter)

1. `config/assets.yaml` schema v2 (`asset_class`, `tier`, `enabled`, `catalog_group`).
2. `assets_registry.py`: `list_enabled_asset_ids()`, `list_catalog_entries()`.
3. `GET /ppe-display-api/catalog.json` grouped catalog.
4. `scripts/witness_asset_catalog.py` — per-asset and `--all-enabled` modes.
5. Streamlit lab selector reads registry only (no hardcoded BTC/ETH list).
6. MSOS Strategy Lab picker reads `catalog.json` (no hardcoded allowlist gate).
7. Tier-1 manifest committed; BTC/ETH/NVDA backward compatible.
8. Evidence doc COMPLETE.

---

## Non-goals

- Enabling tier-1 batch assets (follow-on chapters)
- CME commodity vendor
- Entitlements per asset
- Scanner / auto-discovery

---

## Next chapter after closeout

[`POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md`](POST_PPE_DERIBIT_CRYPTO_TIER1_V1_SELECTION.md) (default backlog order).
