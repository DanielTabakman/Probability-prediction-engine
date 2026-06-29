# MSOS trader review loop v1 — SELECTION

**Chapter:** `msos_trader_review_loop_v1`  
**Priority:** **P0** · **spine** · WORKFLOW pillar  
**Parent program:** [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md)  
**Relay plan:** [`PHASE_PLANS/msos_trader_review_loop_v1_relay.json`](PHASE_PLANS/msos_trader_review_loop_v1_relay.json)

## Status

**SELECTED** 2026-06-29 — closes P7 gap: Monitor reads review state but only Streamlit can save reviews.

## Scope

- `/monitor` snapshot detail route with post-mortem form  
- Server API to **upsert** `snapshot_reviews` (same statuses as `frozen_evaluation_store.REVIEW_STATUSES`)  
- Command Center / Monitor KPI refresh after save  
- Owner scoping via existing workflow owner + `frozen_evaluations.owner_email` when present  

## Non-goals

- New review statuses or classifier changes  
- Streamlit removal (keep parity)  
- Live execution or P&L scoring  
- Full class-summary analytics panel (defer)
