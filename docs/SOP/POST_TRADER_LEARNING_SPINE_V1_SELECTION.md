# Trader Learning Spine v1 — SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-06-29  
**Program:** [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md)  
**Milestone:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md)

---

## Operator intent

Charter and queue the **learning spine** so BUILD is visible end-to-end: save → review → track accuracy — without waiting on architecture comprehension.

Supersedes **relay order** in [`POST_TRADER_WORKFLOW_SUPPLY_REFRESH_V1_SELECTION.md`](POST_TRADER_WORKFLOW_SUPPLY_REFRESH_V1_SELECTION.md) for spine chapters only. Exposure menu and asset-batch queue unchanged.

---

## SELECTION decisions

| # | Action | Rationale |
|---|--------|-----------|
| 1 | **Charter** `msos_trader_review_loop_v1` | P7 reads reviews; MSOS cannot **write** reviews — spine blocked |
| 2 | **Queue spine block** after `ppe_exposure_menu_v1` | Operator-approved READY chapter runs first |
| 3 | **Reorder** spine: review → dist download → cross-venue panel → dist timeseries collector | Closes trader loop before research/ops surfaces |
| 4 | **Keep** `horizon_replay_scrubber_v1` **PLANNED/blocked** | Archive gate unchanged |

---

## Relay order (spine block)

1. `msos_trader_review_loop_v1` — **P0 spine**  
2. `msos_strategy_lab_dist_download_v1` — P1  
3. `msos_cross_venue_strategy_lab_v1` — P2 · side channel  
4. `mvp1_distribution_timeseries_collector_v1` — P2 · ops  

---

## Explicit defer

- MSOS class-summary panel (reuse Streamlit rollup later)
- Horizon replay / outcome ghosts until `replay_ready`
- Full strategy P&L backtest engine
