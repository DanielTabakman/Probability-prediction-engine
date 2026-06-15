# MSOS user state v1 — SELECTION

**Chapter:** `msos_user_state_v1`  
**Display name:** Command Center bridge (PPE snapshots)  
**Priority:** **HIGH**  
**Relay plan:** [`PHASE_PLANS/msos_user_state_v1_relay.json`](PHASE_PLANS/msos_user_state_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_USER_STATE_V1.md`](SPRINT_MSOS_USER_STATE_V1.md)  
**Sequence:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) phase 2

## Status

**SELECTED** 2026-06-14 — steward: real Command Center from PPE snapshots before full MSOS workflow store.

**Blocked until** `msos_production_wiring_v1` **COMPLETE**.

## Scope (in)

- Read-only summary API from `ppe_frozen_evaluations.sqlite3`
- Command Center KPIs + current-work from API (honest snapshot labeling)
- Platform: read-only volume mount + deploy docs
- pytest + operator witness

## Scope (out)

- MSOS thesis/expression server persistence (phase 3)
- Per-user snapshot filtering (phase 4)
- Monitor/History fixtures replacement (phase 5)

## First slice at SELECTION

`MSOS-UserStateV1-Control-Slice001`

## Focus playbook

- Priority tier: **P1** — completes chartered MSOS product path for operator
- Drift guards checked: **yes** — read-only; no TS math
