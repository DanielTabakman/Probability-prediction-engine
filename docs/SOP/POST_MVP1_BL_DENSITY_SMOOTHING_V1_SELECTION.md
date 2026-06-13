# MVP1 B–L density smoothing v1 — SELECTION (pending)

**Chapter:** `mvp1_bl_density_smoothing_v1`  
**Priority:** **MEDIUM** (`mediumQueueSlot`: 1 · P2 demo wedge — not `high`)  
**Sprint:** [`SPRINT_MVP1_BL_DENSITY_SMOOTHING_V1.md`](SPRINT_MVP1_BL_DENSITY_SMOOTHING_V1.md)  
**Relay plan:** [`PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json`](PHASE_PLANS/mvp1_bl_density_smoothing_v1_relay.json)

## Status

**CHARTERED** — inserted on roadmap + queue **immediately after** `mvp1_distribution_quant_research_v2` via `queueAfterPlanPath` + `ppe_queue_insert_after.py`.

## Intent

Smoother **market-implied B–L** density (Method A in implied-distribution plan): IV- or spline-smoothed `C(K)` before `d²C/dK²`. Same orange legend; fewer jagged charts and skipped BL rows during research demos.

## Run order

1. `mvp1_distribution_quant_research_v2` (current — READY)
2. **`mvp1_bl_density_smoothing_v1`** (PLANNED — next after dist quant closeout)
3. `mvp1_cross_venue_prob_panel` → scan → backtest

## First slice at SELECTION

`MVP1-BLDensitySmooth-Control-Slice001`
