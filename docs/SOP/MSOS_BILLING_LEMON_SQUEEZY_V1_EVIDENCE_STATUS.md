# MSOS billing Lemon Squeezy v1 — evidence status

**Chapter:** `msos_billing_lemon_squeezy_v1`  
**Status:** **NOT STARTED** — BUILD deferred until usable demo walkable  
**Phase plan:** [`PHASE_PLANS/msos_billing_lemon_squeezy_v1_relay.json`](PHASE_PLANS/msos_billing_lemon_squeezy_v1_relay.json)

## Operator prereq (Stage A — no BUILD)

- [ ] Lemon Squeezy account (test mode first)
- [ ] Subscription product + checkout URL
- [ ] `MSOS_UPGRADE_OFFER_URL` on production VPS
- [ ] Checkout custom field or instructions: use same email as MSOS sign-in
- [ ] One test purchase witnessed

## BUILD evidence (Stage B)

- [ ] Webhook route live on production
- [ ] pytest green with mocks
- [ ] First real or test-mode subscription auto-grants `paid`
- [ ] [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) paid-interest row
