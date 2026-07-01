# PPE Hyperliquid perp rail v1 — evidence status

**Chapter:** `ppe_hyperliquid_perp_rail_v1`  
**Program:** [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md)  
**Status:** **CHARTERED** — SELECTION 2026-06-30; BUILD not started  
**SELECTION:** [`POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json`](PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-HyperliquidPerp-Control-Slice001 | PENDING | |
| PPE-HyperliquidPerp-Core-Slice002 | PENDING | |
| PPE-HyperliquidPerp-Exposure-Slice003 | PENDING | |
| PPE-HyperliquidPerp-Product-Slice004 | PENDING | |
| PPE-HyperliquidPerp-Closeout-Slice005 | PENDING | |

## Acceptance checklist (chapter close)

- [ ] HYPE registry row (`exposure_only`, `venue: hyperliquid`)
- [ ] Probe CLI live mark + funding
- [ ] Exposure CLI `ok_perp_only` + Live `perp_long`
- [ ] Boundary API parity
- [ ] MSOS `/exposure` HYPE picker + Live perp card
- [ ] Witness green (exposure-only — no options chain)
- [ ] NVDA/BTC exposure regression clean

## Discovery note

`discover_asset_data_source.py --asset HYPE` → `blocked_no_live_options` (expected). **Do not** use asset-batch ritual for HYPE; use perp probe + exposure-only enable per program doc.
