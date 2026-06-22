# MSOS billing Lemon Squeezy v1 — SELECTION

**Chapter:** `msos_billing_lemon_squeezy_v1`  
**Priority:** MEDIUM · **Playbook:** P4  
**Status:** **SELECTED** 2026-06-21 — **BUILD deferred** until usable demo walkable on production.

**Supersedes:** `msos_billing_stripe_v1` (Stripe deferred indefinitely; operator chose Lemon Squeezy MoR).

**Blocked until** `msos_usable_demo_v1` **COMPLETE** + human backlog `lemon_squeezy_operator_prereq`.

## Scope (in)

- Hosted checkout via `MSOS_UPGRADE_OFFER_URL` (Stage A — operator env)
- Webhook auto-entitlement (Stage B — relay BUILD)
- Lemon Squeezy signing secret discipline

## Scope (out)

- Stripe
- Entitlement model (prior chapter)
- Tax filing (handled by Lemon Squeezy as MoR)

## First slice (when BUILD starts)

`MSOS-LemonV1-Control-Slice001`
