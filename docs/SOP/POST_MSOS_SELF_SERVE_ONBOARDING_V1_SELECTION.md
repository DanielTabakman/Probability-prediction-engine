# MSOS self-serve onboarding v1 — SELECTION

**Chapter:** `msos_self_serve_onboarding_v1`  
**Display name:** Self-serve onboarding — public URL + guided tour  
**Milestone:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) workstream **A**  
**Relay plan:** [`PHASE_PLANS/msos_self_serve_onboarding_v1_relay.json`](PHASE_PLANS/msos_self_serve_onboarding_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_SELF_SERVE_ONBOARDING_V1.md`](SPRINT_MSOS_SELF_SERVE_ONBOARDING_V1.md)  
**Direction pivot:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — `trader-workflow-integration-v1`

---

## Status

**SELECTED** — steward SELECTION 2026-06-26 after `ppe_crypto_multi_asset_v1` COMPLETE.

**First slice:** `MSOS-SelfServeV1-Control-Slice001`

---

## SELECTION rationale

| Input | Decision |
|-------|----------|
| Milestone workstream B (crypto) | **COMPLETE** 2026-06-26 |
| Relay pipeline | **SUPPLY_LOW** — no READY queue item |
| Workstream A (self-serve) | **Selected** — charter relay chapter |
| Workstream C (loop fidelity) | Parallel follow-on — not blocking A |
| Equity (`ppe_equity_options_v1`) | **DEFER** — G-04 gate unchanged |

**Operator:** after manifest READY, IDE BUILD from starter or VM `run_ppe.cmd`.

---

## Acceptance (chapter)

1. Production self-serve path documented in [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md).
2. Guided tour production-green per sprint acceptance.
3. Evidence doc complete at closeout.

---

## Non-goals

- Multi-route P4→P7 tour (workflow loop fidelity chapter)
- Equity onboarding
- Billing / signup automation
