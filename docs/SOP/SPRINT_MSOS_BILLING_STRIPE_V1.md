# MSOS billing Stripe v1

> **SUPERSEDED 2026-06-21** — Operator chose **Lemon Squeezy** (MoR). See [`SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md`](SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md). Do not BUILD this chapter unless operator reverts.

**Display name:** Stripe Checkout + subscription webhooks · **chapterId:** `msos_billing_stripe_v1`  
**Controlling canon:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_ENTITLEMENTS_V1.md`](SPRINT_MSOS_ENTITLEMENTS_V1.md)  
**SELECTION:** [`POST_MSOS_BILLING_STRIPE_V1_SELECTION.md`](POST_MSOS_BILLING_STRIPE_V1_SELECTION.md)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Wire **Stripe Checkout** (or Payment Link) and **webhooks** so customers can **pay self-serve** — flipping `msos_entitlements` to `paid` / `subscription_status=active`. Replaces manual operator grant for new conversions; manual path remains fallback.

**Operator note:** Charter now, BUILD when Stripe account + operator bandwidth ready — no implementation required in current sprint wave.

---

## Preconditions

1. `msos_entitlements_v1` **COMPLETE**.
2. Stripe account + products/prices created (operator).
3. VPS can receive webhook at documented path (Caddy route).

---

## Acceptance

1. Checkout session or Payment Link from “Upgrade” CTA (env `STRIPE_PRICE_ID` / `MSOS_STRIPE_CHECKOUT_URL`).
2. Webhook handler: `checkout.session.completed`, `customer.subscription.updated|deleted` → update entitlements row + `stripe_customer_id`.
3. Secrets in VPS `.env` only — never committed.
4. pytest with Stripe fixture/mocks; operator witness one test payment in staging.
5. [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) row for first real payment.

## Not now

- Usage-based billing
- Tax automation (Stripe Tax optional follow-on)
- Execution unlock via payment

---

## Slice map

| Slice | Plane | Deliverable |
|-------|--------|-------------|
| **MSOS-StripeV1-Control-Slice001** | EVIDENCE | Charter + secrets runbook |
| **MSOS-StripeV1-Product-Slice002** | PRODUCT | Checkout CTA + webhook route |
| **MSOS-StripeV1-Platform-Slice003** | PLATFORM | Caddy webhook path + deploy |
| **MSOS-StripeV1-Witness-Slice004** | EVIDENCE | pytest + operator payment witness |
| **MSOS-StripeV1-Closeout-Slice005** | EVIDENCE | Close |
