# MSOS billing Lemon Squeezy v1

**Display name:** Lemon Squeezy checkout + subscription webhooks · **chapterId:** `msos_billing_lemon_squeezy_v1`  
**Controlling canon:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_ENTITLEMENTS_V1.md`](SPRINT_MSOS_ENTITLEMENTS_V1.md)  
**SELECTION:** [`POST_MSOS_BILLING_LEMON_SQUEEZY_V1_SELECTION.md`](POST_MSOS_BILLING_LEMON_SQUEEZY_V1_SELECTION.md)  
**Supersedes:** [`SPRINT_MSOS_BILLING_STRIPE_V1.md`](SPRINT_MSOS_BILLING_STRIPE_V1.md) (operator decision 2026-06-21)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Use **Lemon Squeezy** (merchant of record) so the operator avoids global sales-tax/VAT admin. Customers pay via **hosted checkout**; entitlements flip to `paid` via **webhooks** (BUILD) or **manual grant** (v0).

**Operator decision (2026-06-21):** Lemon Squeezy over Stripe — less compliance work; revisit Stripe only if MRR justifies lower fees.

**BUILD gate:** Usable demo walkable on production (`msos_usable_demo_v1` COMPLETE). Until then: charter only + operator may set checkout link when ready.

---

## Two-stage rollout

| Stage | When | Work |
|-------|------|------|
| **A — Checkout link (v0)** | Demo walkable + Lemon Squeezy account | Operator sets `MSOS_UPGRADE_OFFER_URL` to LS checkout URL; manual `paid` grant per sale |
| **B — Webhook BUILD (v1)** | Stage A validated or volume annoys | Relay chapter: webhook route, signature verify, auto `tier=paid` |

Stage A needs **no relay BUILD** — existing Upgrade CTA already reads `MSOS_UPGRADE_OFFER_URL`.

---

## Preconditions

1. `msos_entitlements_v1` **COMPLETE**.
2. `msos_usable_demo_v1` **COMPLETE** (demo walkable on production URLs).
3. Lemon Squeezy store + subscription product + checkout URL (operator).
4. VPS can receive webhook at documented path (Stage B only).

---

## Acceptance (Stage B BUILD)

1. Upgrade CTA uses `MSOS_UPGRADE_OFFER_URL` (Lemon Squeezy checkout link).
2. Webhook handler: `subscription_created`, `subscription_updated`, `subscription_cancelled` → update entitlements + external subscription id.
3. Secrets in VPS `.env` only (`LEMON_SQUEEZY_WEBHOOK_SECRET`, `LEMON_SQUEEZY_API_KEY` if needed) — never committed.
4. pytest with fixture/mocks; operator witness one test subscription in LS test mode.
5. [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) row for first real payment.

## Not now

- Stripe migration
- Usage-based billing
- Execution unlock via payment

---

## Slice map

| Slice | Plane | Deliverable |
|-------|--------|-------------|
| **MSOS-LemonV1-Control-Slice001** | EVIDENCE | Charter + secrets runbook |
| **MSOS-LemonV1-Product-Slice002** | PRODUCT | Webhook route + entitlement updates |
| **MSOS-LemonV1-Platform-Slice003** | PLATFORM | Caddy webhook path + deploy env |
| **MSOS-LemonV1-Witness-Slice004** | EVIDENCE | pytest + operator payment witness |
| **MSOS-LemonV1-Closeout-Slice005** | EVIDENCE | Close |
