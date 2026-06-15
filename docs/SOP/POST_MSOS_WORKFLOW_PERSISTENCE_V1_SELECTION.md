# MSOS workflow persistence v1 — SELECTION

**Chapter:** `msos_workflow_persistence_v1`  
**Display name:** MSOS thesis workflow store  
**Priority:** **HIGH**  
**Relay plan:** [`PHASE_PLANS/msos_workflow_persistence_v1_relay.json`](PHASE_PLANS/msos_workflow_persistence_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md)  
**Sequence:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) phase 3

## Status

**SELECTED** 2026-06-14 — steward: MSOS-native thesis/expression server store (long-term canon).

**Blocked until** `msos_user_state_v1` **COMPLETE**.

## Scope (in)

- Server-side MSOS workflow SQLite (or equivalent)
- Thesis + expression CRUD API; Command Center from MSOS records
- Optional `linked_snapshot_id` to PPE freezes
- Deprecate `localStorage` as primary persistence

## Scope (out)

- Cloudflare Access per-user scoping (phase 4)
- Monitor/History live (phase 5)
- PPE math port, live execution

## First slice at SELECTION

`MSOS-WorkflowV1-Control-Slice001`

## Focus playbook

- Priority tier: **P1** — chartered MSOS workflow completion
- Drift guards checked: **yes** — MSOS layer only; PPE read by reference
