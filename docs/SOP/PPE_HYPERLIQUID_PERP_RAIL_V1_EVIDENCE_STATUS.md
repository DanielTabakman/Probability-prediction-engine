# PPE Hyperliquid perp rail v1 — evidence status

**Chapter:** `ppe_hyperliquid_perp_rail_v1`
**Program:** [`PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md`](PPE_HYPERLIQUID_PERP_RAIL_PROGRAM_V1.md)
**Status:** **HISTORICALLY AMBIGUOUS / NOT READY** - SELECTION 2026-06-30; current `origin/main` contains HYPE implementation/tests and a Product-Slice004 workflow metric, but this evidence table was never reconciled to chapter COMPLETE on main. Issue #5374 removed the false READY row and did not rerun live Hyperliquid or MSOS runtime checks.
**SELECTION:** [`POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md`](POST_PPE_HYPERLIQUID_PERP_RAIL_V1_SELECTION.md)
**Phase plan:** [`PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json`](PHASE_PLANS/ppe_hyperliquid_perp_rail_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-HyperliquidPerp-Control-Slice001 | PENDING | |
| PPE-HyperliquidPerp-Core-Slice002 | PENDING | |
| PPE-HyperliquidPerp-Exposure-Slice003 | PENDING | |
| PPE-HyperliquidPerp-Product-Slice004 | IMPLEMENTED_ON_MAIN | Workflow metric closed 2026-07-01; evidence closeout remains unreconciled |
| PPE-HyperliquidPerp-Closeout-Slice005 | PENDING | |

## Acceptance checklist (chapter close)

- [x] HYPE registry row (`exposure_only`, `venue: hyperliquid`) - repository implementation/test witness only
- [ ] Probe CLI live mark + funding - no exact live runtime witness found in current main; issue #5374 did not rerun it
- [x] Exposure CLI `ok_perp_only` + Live `perp_long` - automated/mocked test witness only
- [ ] Boundary API parity
- [ ] MSOS `/exposure` HYPE picker + Live perp card - no exact manual runtime witness found in current main; issue #5374 did not rerun the website
- [ ] Witness green (exposure-only — no options chain)
- [ ] NVDA/BTC exposure regression clean

## Discovery note

`discover_asset_data_source.py --asset HYPE` → `blocked_no_live_options` (expected). **Do not** use asset-batch ritual for HYPE; use perp probe + exposure-only enable per program doc.
