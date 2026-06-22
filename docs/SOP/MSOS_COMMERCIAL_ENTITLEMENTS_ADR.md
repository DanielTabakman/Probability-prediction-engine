# MSOS commercial entitlements ADR

**Status:** **PROPOSED** — ratified at `msos_entitlements_v1` SELECTION  
**Controlling canon:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

---

## Context

Operator needs **free accounts** to acquire users and a **credible paid path** to test willingness to pay. **Lemon Squeezy** (merchant of record) is the chosen self-serve billing provider (2026-06-21); Stripe is superseded. Architecture reuses nullable external billing columns until webhook BUILD ships.

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
| `paid` | Full product per sprint evidence; no execution unlock | Operator grant, Lemon Squeezy checkout + manual grant (v0), or **webhook auto-grant** (v1) |

Tiers are **orthogonal** to PPE math — gates MSOS surfaces and optional rate limits only.

### 3. Storage

- Table `msos_entitlements` in MSOS workflow DB volume (`msos_web` data dir).
- Columns: `owner_email` (PK), `tier`, `granted_at_utc`, `granted_by`, `notes`, `stripe_customer_id` (nullable), `stripe_subscription_id` (nullable), `subscription_status` (nullable enum: `none` | `active` | `past_due` | `canceled`).

### 4. Lemon Squeezy (phase 7b — operator decision 2026-06-21)

- **Provider:** Lemon Squeezy (MoR) — global tax/VAT handled by platform; operator avoids Stripe compliance overhead.
- **Stage A (v0):** `MSOS_UPGRADE_OFFER_URL` → hosted checkout link; operator manually grants `paid` after purchase email.
- **Stage B (v1 BUILD):** [`msos_billing_lemon_squeezy_v1`](SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md) — webhooks flip `tier` / `subscription_status`.
- **BUILD gate:** `msos_usable_demo_v1` walkable on production.
- **Superseded:** [`msos_billing_stripe_v1`](SPRINT_MSOS_BILLING_STRIPE_V1.md) — do not BUILD Stripe unless operator reverts.
- **Columns:** `stripe_customer_id` / `stripe_subscription_id` store external billing IDs generically until rename slice (LS subscription id in `stripe_subscription_id` is acceptable v1).

### 5. Paid path (v0 until webhook BUILD)

1. User hits “Upgrade” → Lemon Squeezy checkout (env `MSOS_UPGRADE_OFFER_URL`).
2. Operator grants `paid` for purchaser email (must match Cloudflare Access sign-in email).
3. Log paid-interest in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

### 6. Free tier limits (honest v1)

Document in evidence — examples (steward may tune):

- Snapshot freeze count per month (optional soft cap — implement only if scoped)
- Or: no cap v1; free = full research demo

Default v1 recommendation: **no artificial cripple** — free tier is real product; paid tier funds priority/support/future features.

---

## Consequences

**Positive:** MoR tax simplicity; hosted checkout without custom payment UI; single identity key; webhooks drop in after demo.

**Tradeoffs:** Manual upgrade ops until webhook BUILD; higher MoR fees vs raw Stripe; operator must match LS email to Access email.

---

## Non-goals

- Custom auth server
- Claiming revenue in marketing without [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) evidence
