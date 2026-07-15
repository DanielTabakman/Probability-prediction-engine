# MSOS Strategy Lab embed shell v1 — SELECTION

**Chapter:** `msos_strategy_lab_embed_shell_v1`  
**Display name:** Strategy Lab PPE embed shell — storyboard chart region  
**Priority:** **HIGH** (MCD-required)  
**Relay plan:** [`PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json`](PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md)

## Status

**SELECTED** 2026-06-20 — steward: replace box-in-box Streamlit iframe on `/strategy-lab` with storyboard-aligned chart shell; PPE math stays in Python.

**Precondition met:** `msos_workflow_persistence_v1` **COMPLETE** 2026-06-20. No active blocker remains.

## Scope (in)

- PPE read-only display boundary (JSON payload and/or chromeless embed-only Streamlit view)
- MSOS Strategy Lab chart panel matching storyboard `03_ppe_lab` layout hierarchy
- Platform proxy/deploy updates if embed path changes
- Visual witness vs storyboard; pytest on both boundaries

## Scope (out)

- TypeScript port of PPE distribution/disagreement math
- Removing Streamlit as `app.*` authoritative lab
- Monitor/History live data (phase 5)
- Access-scoped embed (phase 4b)

## Blocker chain

`msos_production_wiring_v1` (done) → `msos_user_state_v1` → `msos_workflow_persistence_v1` → **this chapter**.

Does **not** block live product sequence phases 4a–7; runs in parallel slot after phase 3 closeout promotion.

## First slice at SELECTION (historical)

`MSOS-EmbedShellV1-Control-Slice001` was the historical first slice and is no longer pending.

## Focus playbook

- Priority tier: **P2** — visual/product polish; does not widen MVP1 math contracts
- Drift guards checked: **yes** — display/proxy only; no TS math
