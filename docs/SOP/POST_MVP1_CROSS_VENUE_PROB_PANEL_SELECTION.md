# MVP1 cross-venue probability panel — SELECTION

**Chapter:** `mvp1_cross_venue_prob_panel`  
**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) · chapter **3**  
**Mechanical priority:** **MEDIUM · slot 2**  
**Relay plan:** [`PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json`](PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md)

## Status

**CHARTERED** 2026-06-13 — **blocked** until `msos_public_demo_launch_v1` **COMPLETE**.

## Why

Quant data layer: Polymarket vs options P(BTC > K) gaps as CSV + daily snapshots. Prerequisite for scan v1 and backtest v1.

## First slice

`MVP1-CrossVenue-Control-Slice001`

## Operator

Merge **PR #149** → sidebar Polymarket on → implied lab CSV download · daily `collect_cross_venue_snapshot.py`.
