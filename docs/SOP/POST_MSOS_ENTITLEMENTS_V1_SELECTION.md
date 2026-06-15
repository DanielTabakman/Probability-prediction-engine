# MSOS entitlements v1 — SELECTION

**Chapter:** `msos_entitlements_v1`  
**Priority:** **HIGH** · **Playbook:** P4 monetization signal  
**Relay plan:** [`PHASE_PLANS/msos_entitlements_v1_relay.json`](PHASE_PLANS/msos_entitlements_v1_relay.json)

**Blocked until** `msos_access_identity_v1` **COMPLETE**.  
*(E2E witness may run in parallel or complete first — default queue order: after phase 6.)*

## Scope (in)

- Free tier accounts (default)
- Entitlement store + operator grant path
- Upgrade CTA (env-driven, no Stripe)
- ADR with Stripe hooks deferred

## Scope (out)

- Stripe Checkout / webhooks → phase 7b

## First slice

`MSOS-EntitleV1-Control-Slice001`
