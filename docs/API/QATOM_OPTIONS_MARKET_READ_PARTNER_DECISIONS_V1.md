# Qatom / Options Market Read partner decisions v1

**Recorded:** 2026-09-30  
**Authority:** founder delegation for API / Distribution lane routine integration controls.  
**Applies to:** Options Market Read v1.3 partner acceptance.  
**Product semantics:** unchanged.

These decisions close the old “Tuesday meeting” integration-control gate unless fresh external evidence from Qatom requires a non-product adjustment.

| Control | Decision |
|---|---|
| **Call shape** | Default to **server-to-server HTTPS GET** from Qatom/partner infrastructure to the production API. Do not require browser/client execution. |
| **Authentication** | Keep the current read-only preview **unauthenticated**. Do not add partner secrets or a new auth system unless an external integration requirement proves it necessary. |
| **Rate limit / service expectation** | Do not promise a new SLA or contractual rate limit for the preview. Reuse existing infrastructure safeguards. If abuse protection becomes technically necessary, choose a conservative reversible edge limit, return normal HTTP semantics, document it, and continue. |
| **CORS** | Do **not** widen CORS for the preview. Server-to-server integration does not require browser CORS. Add a specific origin only if a verified browser integration later requires it. |
| **Alert destination** | Keep the existing failed GitHub Actions uptime run as the canonical alert signal. Do not add a new alert vendor or secret as part of partner acceptance. |
| **Usage telemetry** | Add no user-level or identity telemetry for this chapter. Aggregate operational counters such as request count, status class, latency and freshness may be used when already available or easily added without collecting identifiers. |
| **Rendering** | Qatom should render the deterministic `answer` first, expose the resolved expiry and freshness, use structured metrics for supporting detail, and retain disclosures/method limitations. |
| **Compatibility** | Preserve schema `1.3` / ruleset `options-market-read.v1.3`; additive unknown fields are allowed only when documented/tested. |

## Delegated adjustment rule

If direct Qatom integration evidence contradicts one of the operational assumptions above, the API lane may make the smallest reversible **non-product** adjustment and record it in GitHub without asking the founder.

Founder input is still required for:
- changing the financial meaning of the product;
- adding execution, individualized recommendations, payments or custody;
- consuming a new reserved Qatom product slot;
- secrets/commercial terms that require the founder to provide or approve external credentials/commitments.
