# MSOS public demo launch v1 — SELECTION

**Chapter:** `msos_public_demo_launch_v1`  
**Priority:** **MEDIUM**  
**Relay plan:** [`PHASE_PLANS/msos_public_demo_launch_v1_relay.json`](PHASE_PLANS/msos_public_demo_launch_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md`](SPRINT_MSOS_PUBLIC_DEMO_LAUNCH_V1.md)

## Status

**SELECTED** 2026-06-13 — operator: ship public URL + research-beta CTA after visual parity.

**Blocked until** `msos_storyboard_visual_parity_v1` **COMPLETE**.

## Scope (in)

- VPS: `msos_web` live on apex; deploy witness doc updated
- Research beta CTA on MSOS homepage (env-driven; honest copy)
- Operator URL check-in checklist (compare local vs production)
- ntfy **check-in** ping when chapter closes (via control-plane hook)

## Scope (out)

- Paywall automation, billing, live execution
- Replacing Streamlit PPE lab (stays on `app.*` per stack ADR)

## First slice at SELECTION

`MSOS-PublicLaunchV1-Control-Slice001`
