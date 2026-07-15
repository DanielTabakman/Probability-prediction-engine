---
archived: true
chapter_id: msos_entitlements_v1
closed: 2026-06-19
---


# MSOS entitlements v1 — evidence status

**Chapter:** `msos_entitlements_v1`  
**Status:** **COMPLETE** 2026-06-19  
**ADR:** [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md)

| Slice | Status |
|-------|--------|
| MSOS-EntitleV1-Control-Slice001 | CLOSED |
| MSOS-EntitleV1-Product-Slice002 | CLOSED |
| MSOS-EntitleV1-Platform-Slice003 | CLOSED |
| MSOS-EntitleV1-Witness-Slice004 | CLOSED | automated witness only; no fresh manual runtime check in issue #5374 |
| MSOS-EntitleV1-Closeout-Slice005 | CLOSED | PR #232 / merge `a5aaed8072f931203439bd92a4707e5380370db1` |

## Commercial witness

- [ ] New Access user receives `free` tier automatically
- [ ] Operator can grant `paid` without Stripe
- [ ] Upgrade CTA logs to VALIDATION_REALITY_CHECKS
- [ ] `stripe_customer_id` column exists but unused until billing chapter
