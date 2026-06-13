# MVP1 cross-venue scan v1 — SELECTION

**Chapter:** `mvp1_cross_venue_scan_v1`  
**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) · chapter **4**  
**Mechanical priority:** **MEDIUM · slot 3**  
**Relay plan:** [`PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json`](PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md`](SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md)

## Status

**CHARTERED** 2026-06-13 — **blocked** until `mvp1_cross_venue_prob_panel` **COMPLETE**.

## Why

Operators and quants should not read CSV rows manually. This chapter ships **ranked gap reports** from live data or saved snapshots.

## First slice

`MVP1-CrossVenueScan-Control-Slice001`

## Operator

`python scripts/run_cross_venue_scan.py` → read `artifacts/cross_venue_reports/latest.md`.
