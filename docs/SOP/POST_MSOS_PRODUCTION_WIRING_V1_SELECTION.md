# MSOS production wiring v1 — SELECTION

**Chapter:** `msos_production_wiring_v1`  
**Priority:** **HIGH**  
**Relay plan:** [`PHASE_PLANS/msos_production_wiring_v1_relay.json`](PHASE_PLANS/msos_production_wiring_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md)

## Status

**SELECTED** 2026-06-14 — operator: apex MSOS shell must behave like a real product walkthrough (sign-in, embed, CTAs, wired nav).

**Blocked until** `msos_public_demo_launch_v1` **COMPLETE**.

## Scope (in)

- Sign in → `app.marketstructureos.com` (env-configurable)
- Research beta CTA on MSOS homepage (`PPE_RESEARCH_OFFER_*`)
- Live PPE embed on Strategy Lab when build/env + proxy wired
- Wire dead nav/buttons to real routes or external targets
- Compose/Caddy/deploy docs for operator VPS rollout
- pytest + operator URL witness checklist

## Scope (out)

- Real account KPIs/theses in Command Center (`msos_user_state_v1` follow-on)
- Custom auth server, billing, live execution
- Replacing Streamlit as PPE authority

## First slice at SELECTION

`MSOS-ProdWireV1-Control-Slice001`

## Focus playbook

- Priority tier: **P3** — distribution / public URL must work
- Drift guards checked: **yes** — display/proxy only; no TS math port
