# PPE equity options v1 — evidence status

**Chapter:** `ppe_equity_options_v1`  
**Status:** **IN PROGRESS** (SELECTED 2026-06-26)  
**SELECTION:** [`POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md`](POST_PPE_EQUITY_OPTIONS_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/ppe_equity_options_v1_relay.json`](PHASE_PLANS/ppe_equity_options_v1_relay.json)  
**Sprint:** [`SPRINT_PPE_EQUITY_OPTIONS_V1.md`](SPRINT_PPE_EQUITY_OPTIONS_V1.md)  
**Adapter ADR:** [`PPE_EQUITY_OPTIONS_ADAPTER_ADR.md`](PPE_EQUITY_OPTIONS_ADAPTER_ADR.md)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-Equity-Control-Slice001 | **CLOSED** | Charter + ADR stub (NVDA schema; yaml in Core-Slice002) |
| PPE-Equity-Core-Slice002 | PENDING | `fetch_equity_options.py` |
| PPE-Equity-Core-Slice003 | PENDING | Forward/IV + trust flags |
| PPE-Equity-UI-Slice004 | PENDING | Streamlit equity path |
| PPE-Equity-Product-Slice005 | PENDING | MSOS ticker selector |
| PPE-Equity-Platform-Slice006 | PENDING | Embed API + deploy witness |
| PPE-Equity-Witness-Slice007 | PENDING | pytest + flake handling |
| PPE-Equity-Closeout-Slice008 | PENDING | Chapter close |

---

## Gates (satisfied at SELECTION)

- [x] `ppe_crypto_multi_asset_v1` COMPLETE
- [x] Steward approves seed ticker (default NVDA)
- [ ] G-04 validation row optional per SELECTION 2026-06-26

## Witness checklist (chapter closeout)

- [ ] Equity options fetch smoke for NVDA (mocked + live steward spot-check)
- [ ] Implied distribution BL + lognormal witness
- [ ] Trust warnings for thin chain / dividends
- [ ] MSOS Strategy Lab NVDA path
- [ ] Production demo witness

## Operator sign-off

- [ ] Operator walked NVDA equity ticker in Strategy Lab on production URL
