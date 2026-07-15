# MSOS entitlements v1 — SELECTION

**Chapter:** `msos_entitlements_v1`
**Priority:** **HIGH** · **Playbook:** P4 monetization signal
**Relay plan:** [`PHASE_PLANS/msos_entitlements_v1_relay.json`](PHASE_PLANS/msos_entitlements_v1_relay.json)

**SELECTED AND COMPLETE** 2026-06-19. Historical prerequisite `msos_access_identity_v1` later completed; this chapter closed through PR #232 / merge commit `a5aaed8072f931203439bd92a4707e5380370db1`.
*(E2E witness may run in parallel or complete first — default queue order: after phase 6.)*

## Scope (in)

- Free tier accounts (default)
- Entitlement store + operator grant path
- Upgrade CTA (env-driven, no Stripe)
- ADR with Stripe hooks deferred

## Scope (out)

- Stripe Checkout / webhooks → phase 7b

## First slice (historical)

`MSOS-EntitleV1-Control-Slice001` was the historical first slice and is no longer pending.
