# MSOS Strategy Lab distribution download v1 — SELECTION

**Chapter:** `msos_strategy_lab_dist_download_v1`  
**Priority:** **MEDIUM** · **P2**  
**Parent:** [`POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md`](POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md) Phase 2  
**Relay plan:** [`PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json`](PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json)

## Status

**SELECTED** 2026-06-29 — Streamlit export **shipped**; MSOS surface missing for self-serve traders.

## Scope

- Download distribution stats CSV from MSOS Strategy Lab embed (proxy to PPE export API or server action)  
- Honest simulation-only copy; asset param from `?asset=`  
- Witness: BTC + one equity ticker  

## Non-goals

- Multi-expiry batch zip; historical timeseries download (separate collector chapter)
