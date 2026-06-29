# Trader workflow supply refresh v1 — SELECTION outcome

**Status:** **SELECTION COMPLETE** 2026-06-29  
**Milestone:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md)  
**Direction:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — `trader-workflow-integration-v1`

---

## Problem

Relay queue hit `SUPPLY_LOW` because `horizon_replay_scrubber_v1` was **READY** in `PHASE_QUEUE.json` while the archive gate (`replay_ready`, ≥30d) is unsatisfied — blocking auto-select and side-channel promotion.

## SELECTION decisions

| # | Action | Rationale |
|---|--------|-----------|
| 1 | Demote `horizon_replay_scrubber_v1` queue → **PLANNED** / backlog → **blocked** until `replay_ready` | Matches [`POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md`](POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md) |
| 2 | **Queue** `mvp1_bl_density_smoothing_v1` | P8 report next P2 lab chapter; dist quant v2 **COMPLETE** |
| 3 | **Queue** `msos_strategy_lab_dist_download_v1` | Distribution export Phase 2 — MSOS download surface |
| 4 | **Queue** `msos_trader_workflow_horizon_nav_v1` | Trader workflow — Strategy Lab ↔ Options Horizon nav |
| 5 | **Queue** `msos_cross_venue_strategy_lab_v1` (side channel) | Cross-venue panel in MSOS embed |
| 6 | **Queue** `mvp1_distribution_timeseries_collector_v1` (side channel) | Daily dist-stats collector hardening |

## Relay order (mechanical)

Superseded for **spine chapters** by [`POST_TRADER_LEARNING_SPINE_V1_SELECTION.md`](POST_TRADER_LEARNING_SPINE_V1_SELECTION.md).

1. `mvp1_bl_density_smoothing_v1` — **medium** · side channel  
2. `msos_strategy_lab_dist_download_v1` — **medium**  
3. `msos_trader_workflow_horizon_nav_v1` — **medium**  
4. `msos_cross_venue_strategy_lab_v1` — **low** · side channel  
5. `mvp1_distribution_timeseries_collector_v1` — **low** · side channel  

`horizon_replay_scrubber_v1` auto-promotes when VM archive hits 30 days.

## Explicit defer (unchanged)

- `horizon_liquidation_overlay_v1`, `horizon_outcome_ghosts_v1`, `ppe_cme_commodity_v1` — validation/vendor gates  
- Live execution, Stripe automation, interaction modes 2–7
