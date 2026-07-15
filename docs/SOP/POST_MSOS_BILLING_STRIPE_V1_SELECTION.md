# MSOS billing Stripe v1 — SELECTION

**Chapter:** `msos_billing_stripe_v1`  
**Priority:** MEDIUM · **Playbook:** P4  
**Status:** **SELECTED / DEFERRED** 2026-06-14. Issue #5374 removed the false READY row; BUILD remains deferred until operator enables Stripe prerequisites/secrets.

**Historical prerequisite cleared:** `msos_entitlements_v1` is COMPLETE. **Active blocker:** operator Stripe setup / price ID / secrets are not enabled.

## Scope (in)

- Self-serve pay → entitlement upgrade
- Webhooks + secrets discipline

## Scope (out)

- Entitlement model (prior chapter)

## First slice (when BUILD starts after reactivation)

`MSOS-StripeV1-Control-Slice001` is not currently dispatchable from the READY frontier.
