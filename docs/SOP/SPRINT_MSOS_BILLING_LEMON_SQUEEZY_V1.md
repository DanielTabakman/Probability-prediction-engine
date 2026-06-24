# MSOS billing Lemon Squeezy v1

**Display name:** Lemon Squeezy checkout + subscription webhooks · **chapterId:** `msos_billing_lemon_squeezy_v1`  
**Controlling canon:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_ENTITLEMENTS_V1.md`](SPRINT_MSOS_ENTITLEMENTS_V1.md)  
**Operator runbook:** [`LEMON_SQUEEZY_OPERATOR_SETUP_V1.md`](LEMON_SQUEEZY_OPERATOR_SETUP_V1.md)  
**Supersedes:** [`SPRINT_MSOS_BILLING_STRIPE_V1.md`](SPRINT_MSOS_BILLING_STRIPE_V1.md) (operator decision 2026-06-21)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Wire **Lemon Squeezy** hosted checkout and **webhooks** so customers can **pay self-serve** — flipping `msos_entitlements` to `paid` / `subscription_status=active`. Lemon Squeezy is **merchant of record** (global tax handled by LS). Manual operator grant remains fallback.

---

## Preconditions

1. `msos_entitlements_v1` product code shipped (`msosEntitlements.ts`, upgrade CTA).
2. Lemon Squeezy store + subscription product (operator).
3. VPS receives webhooks at `/api/billing/lemon-squeezy/webhook` (apex → `msos_web`).

---

## Acceptance

1. **v0:** `MSOS_UPGRADE_OFFER_URL` → sidebar upgrade CTA opens LS checkout.
2. **v1:** Webhook handler verifies `X-Signature`, maps `subscription_*` events → entitlement upsert.
3. Secrets in VPS `.env` only — never committed.
4. Operator runbook + `scripts/msos_grant_entitlement.py` for manual path.
5. pytest witness for webhook lib + grant path.

## Not now

- Usage-based billing
- In-app plan picker (single checkout URL is fine v1)
- Execution unlock via payment

---

## Slice map

| Slice | Plane | Deliverable |
|-------|--------|-------------|
| **MSOS-LemonV1-Product-Slice001** | PRODUCT | Webhook route + `grantEntitlement` |
| **MSOS-LemonV1-Platform-Slice002** | PLATFORM | Operator runbook + compose env |
| **MSOS-LemonV1-Witness-Slice003** | EVIDENCE | pytest + operator payment witness |
