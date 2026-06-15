# MSOS entitlements & commercial beta v1

**Display name:** Free accounts + paid-ready entitlements · **chapterId:** `msos_entitlements_v1`  
**Controlling canon:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) · [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) (P4)  
**Prior chapter:** [`SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md`](SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md) (or parallel after phase 4 if operator urgent — default blocked until E2E)  
**SELECTION:** [`POST_MSOS_ENTITLEMENTS_V1_SELECTION.md`](POST_MSOS_ENTITLEMENTS_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Enable **customer acquisition** with a **free tier account** and a path to **charge for access** without Stripe in this chapter. Entitlement model + operator tools to upgrade users; UI surfaces tier honestly; hooks reserved for Stripe (`stripe_customer_id`, `subscription_status` nullable).

**Operator goal:** Sign up free users via Access; manually or semi-manually mark paid/research-beta; product gates premium surfaces by entitlement — test willingness to pay via invoice/manual link before Stripe automation.

---

## Preconditions

1. `msos_access_identity_v1` **COMPLETE** (identity on MSOS routes).
2. [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md) research-offer pattern understood.

---

## Acceptance

1. **ADR merged:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md) — tiers, data model, Stripe-deferred hooks.
2. **Entitlement store:** per `owner_email` row: `tier` (`free` | `research_beta` | `paid`), `granted_at`, optional `notes`, nullable `stripe_customer_id`.
3. **Free tier:** new Access users get `free` — full core loop (lab embed, thesis save, Command Center) per ADR limits documented honestly.
4. **Upgrade path (no Stripe):** operator CLI or documented API to set `research_beta` / `paid`; optional “Request upgrade” CTA → mailto or Typeform (env-driven).
5. **UI:** tier badge in app shell; gated features show honest “Upgrade” — not broken buttons.
6. **Paid-interest logging:** upgrade requests → [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
7. Pytest for entitlement read + gate middleware.

## Not now

- Stripe Checkout / webhooks ([`SPRINT_MSOS_BILLING_STRIPE_V1.md`](SPRINT_MSOS_BILLING_STRIPE_V1.md))
- Automated dunning, tax, invoices
- Live execution unlock via payment

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-EntitleV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + ADR |
| **MSOS-EntitleV1-Product-Slice002** | PRODUCT | MSOS_UI | Tier UI + gate middleware |
| **MSOS-EntitleV1-Platform-Slice003** | EVIDENCE | PLATFORM | Operator upgrade script + deploy env |
| **MSOS-EntitleV1-Witness-Slice004** | EVIDENCE | CONTROL | pytest + commercial witness |
| **MSOS-EntitleV1-Closeout-Slice005** | EVIDENCE | CONTROL | Close |
