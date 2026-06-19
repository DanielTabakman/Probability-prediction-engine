# MSOS billing Stripe v1 — SELECTION

**Chapter:** `msos_billing_stripe_v1`  
**Priority:** MEDIUM · **Playbook:** P4  
**Status:** **SELECTED** 2026-06-14 — **BUILD deferred** until operator enables Stripe.

**Blocked until:**

1. `msos_entitlements_v1` **COMPLETE** (done)
2. `msos_e2e_product_witness_v1` **COMPLETE**
3. Operator marks [`stripe_operator_prereq`](HUMAN_STEWARD_BACKLOG.json) done (Stripe account, keys, webhook secrets on VPS)

**Steward note (2026-06-19):** Not ready for Stripe BUILD — accounts and deploy secrets still pending.

## Scope (in)

- Self-serve pay → entitlement upgrade
- Webhooks + secrets discipline

## Scope (out)

- Entitlement model (prior chapter)

## First slice (when BUILD starts)

`MSOS-StripeV1-Control-Slice001`
