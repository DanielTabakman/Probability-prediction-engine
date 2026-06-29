# MVP1 B–L density smoothing v1 — SELECTION

**Chapter:** `mvp1_bl_density_smoothing_v1`  
**Priority:** **MEDIUM** · **P2** · side channel  
**Relay plan:** [`PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json`](PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json)  
**Sprint:** [`SPRINT_MVP1_BL_DENSITY_SMOOTHING_V1.md`](SPRINT_MVP1_BL_DENSITY_SMOOTHING_V1.md)

## Status

**SELECTED** 2026-06-29 — dist quant v2 **COMPLETE**; prior partial branch `MVP1-BLDensitySmooth-Product-Slice002` to be rebuilt on current `main`.

## Why

Smoother Breeden–Litzenberger curves improve implied-lab legibility and export quality — next chapter per [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) §4 after dist quant v2.

## Scope

- Savitzky–Golay or constrained spline smoothing on BL second-derivative grid before normalization  
- Trust strip / summary panel honesty when smoothing applied  
- Tests on synthetic and fixture call marks  

## Non-goals

- Multi-asset smoothing params per ticker  
- MSOS TypeScript density math  
