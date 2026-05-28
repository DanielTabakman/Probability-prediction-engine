# Phase 3 commercial wrapper (v0) — operator checklist

**Chapter:** Phase 3 commercial wrapper · **Sprint:** [`SPRINT_PHASE3_COMMERCIAL_WRAPPER.md`](SPRINT_PHASE3_COMMERCIAL_WRAPPER.md)

## Scope (v0)

Bounded wrapper around the MVP1 **public demo**: consistent CTA / research-offer copy, in-app operator checklist expander, and automated guardrails against trade-signal language. **No** billing, auth, or paywall automation.

## Demo env

```bash
export PPE_ENABLE_SNAPSHOTS=0
export PPE_PRIVATE_APP_URL=https://app.marketstructureos.com
export PPE_RESEARCH_OFFER_URL="mailto:YOUR_EMAIL?subject=PPE%20research%20beta"
# optional: export PPE_RESEARCH_OFFER_LABEL="Request research beta access"
streamlit run src/viz/app.py
```

Production: same vars on the **demo** Docker service (not the full app with snapshots).

## Session flow (~10 min)

1. Confirm hero **Get full access** + **Research beta (v0)** when env is configured.
2. Show MVP1 output + chart — market-implied read, not a recommendation.
3. Explain candidate / watch / no-trade and trust states without edge claims.
4. Offer one steward-selected path: research beta, weekly brief, or bespoke call.
5. Ask willingness to pay; record exact words for [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) when applicable.

## Commercial boundary (do not say)

- Promised profit, proven alpha, or buy/sell / trade-signal language
- Fully automated trading
- Multi-asset (e.g. NVIDIA LEAPS) product ready today

## In-app checklist

On the public demo path, open **Operator checklist (v0)** in the sidebar area (collapsed by default).

## Related

- Prior offer playbook: [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md)
- VPS deploy witness: [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)
