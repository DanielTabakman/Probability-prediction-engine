# MVP1 cross-venue probability panel — SELECTION

**Chapter:** `mvp1_cross_venue_prob_panel`  
**Mechanical priority:** **MEDIUM**  
**Medium queue slot:** **2** (runs after `msos_storyboard_visual_parity_v1` and `msos_public_demo_launch_v1`; before LOW `mvp1_distribution_quant_research_v2`)  
**Relay plan:** [`PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json`](PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md)

## Status

**CHARTERED** 2026-06-13 — pre-chartered; **blocked** until prior **MEDIUM** backlog rows complete and **HIGH** `ppe_operator_visibility_v1` closes.

## Why this chapter

Shortest win for **quant data + arb candidate screening**: at matched (strike, horizon), compare Polymarket Yes% to options-implied P(BTC > K). Math already exists in `prediction_spread_probs.py`; missing pieces are **export**, **gap columns**, **match-quality flags**, and **daily snapshots** for backtest panels.

## Scope (in)

1. Cross-venue CSV export + implied-lab download  
2. Daily snapshot script (`artifacts/cross_venue_snapshots/`)  
3. Unit tests + evidence witness  

## Scope (out)

- Execution, auto-trade, alerts  
- Full backtest engine (forward-collect only)  
- MSOS shell download  

## First slice at SELECTION

`MVP1-CrossVenue-Control-Slice001`

## Operator

After merge: enable **Prediction markets (Polymarket)** in sidebar → implied lab → **Download cross-venue prob panel (CSV)**. Daily: `python scripts/collect_cross_venue_snapshot.py`.
