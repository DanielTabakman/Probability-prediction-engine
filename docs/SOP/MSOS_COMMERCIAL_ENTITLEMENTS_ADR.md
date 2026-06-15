# MSOS commercial entitlements ADR

**Status:** **PROPOSED** — ratified at `msos_entitlements_v1` SELECTION  
**Controlling canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

---

## Context

Operator needs **free accounts** to acquire users and a **credible paid path** to test willingness to pay. Full Stripe integration is deferred (operator bandwidth); architecture must not require rework when Stripe ships.

---

## Decision

### 1. Identity source

| Field | Source |
|-------|--------|
| `owner_email` | Cloudflare Access (`CF-Access-Authenticated-User-Email`) — canonical user key |

No separate username/password system.

### 2. Entitlement tiers (v1)

| Tier | Access | How granted |
|------|--------|-------------|
| `free` | Core loop: Strategy Lab embed, thesis save, Command Center, monitor/history read | Default on first authenticated visit |
| `research_beta` | Same + steward-invited cohort features (document in sprint evidence) | Operator grant or research CTA workflow |
| `paid` | Full product per sprint evidence; no execution unlock | Operator grant, manual invoice, or **later** Stripe |

Tiers are **orthogonal** to PPE math — gates MSOS surfaces and optional rate limits only.

### 3. Storage

- Table `msos_entitlements` in MSOS workflow DB volume (`msos_web` data dir).
- Columns: `owner_email` (PK), `tier`, `granted_at_utc`, `granted_by`, `notes`, `stripe_customer_id` (nullable), `stripe_subscription_id` (nullable), `subscription_status` (nullable enum: `none` | `active` | `past_due` | `canceled`).

### 4. Stripe (deferred chapter)

- **Phase 7b:** [`msos_billing_stripe_v1`](SPRINT_MSOS_BILLING_STRIPE_V1.md) wires Checkout + webhooks to flip `tier` / `subscription_status`.
- **This ADR:** nullable Stripe columns + webhook route stub path documented; **no** Stripe SDK in entitlements chapter.

### 5. Manual paid path (until Stripe)

1. User hits “Upgrade” → mailto / Calendly / invoice link (env `MSOS_UPGRADE_OFFER_URL`).
2. Operator runs `scripts/msos_grant_entitlement.py --email … --tier paid` (or equivalent).
3. Log paid-interest in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

### 6. Free tier limits (honest v1)

Document in evidence — examples (steward may tune):

- Snapshot freeze count per month (optional soft cap — implement only if scoped)
- Or: no cap v1; free = full research demo

Default v1 recommendation: **no artificial cripple** — free tier is real product; paid tier funds priority/support/future features.

---

## Consequences

**Positive:** Test payment intent without Stripe; single identity key; Stripe drops in later.

**Tradeoffs:** Manual upgrade ops until Stripe; operator must run grant script.

---

## Non-goals

- Custom auth server
- Claiming revenue in marketing without [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) evidence
