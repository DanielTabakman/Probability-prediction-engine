# Commercial Validation — operator playbook

**Chapter:** Commercial Validation · **Sprint:** [`SPRINT_POST_VALIDATION_COMMERCIAL.md`](SPRINT_POST_VALIDATION_COMMERCIAL.md)

## v0 offer (selected)

**Private demo + paid research beta** — BTC options market-structure readouts, anomaly inspection, freeze/review discipline on the full app. **Not** guaranteed alpha, execution, or multi-asset automation.

## Demo setup

```bash
# Public demo (no snapshots)
export PPE_ENABLE_SNAPSHOTS=0
export PPE_PRIVATE_APP_URL=https://app.marketstructureos.com
export PPE_RESEARCH_OFFER_URL="mailto:YOUR_EMAIL?subject=PPE%20research%20beta"
# optional: export PPE_RESEARCH_OFFER_LABEL="Book a 20-min demo"
streamlit run src/viz/app.py
```

Production: set the same env vars on the **demo** Docker service (not the full app).

## Conversation script (~10 min)

1. **Open** on `marketstructureos.com` (or local demo env).
2. **Show** MVP1 output line + chart — “what the market implies at this expiry.”
3. **Explain** candidate / watch / no-trade and trust/degraded states (no edge claims).
4. **Offer** one of:
   - Paid research beta (limited seats, weekly readout + async Q&A)
   - Weekly BTC volatility / anomaly brief (subscription-style, manual delivery)
   - Bespoke 45-min research call (highest touch)
5. **Ask:** “Would you pay $X/month or $Y per brief for this discipline?” Record exact words.
6. **Close:** If interest, send mailto/Calendly link from `PPE_RESEARCH_OFFER_URL`.

## What counts as paid-interest **Y**

| Signal | Example |
|--------|---------|
| **Y** | Verbal willingness to pay, waitlist signup, invoice request, pilot deposit |
| **N** | “Cool demo” only, no price discussion, no follow-up consent |
| **Prep** | Offer surface + this playbook shipped; no live buyer yet — log **N** with next outreach date |

## Objection themes (log verbatim)

- Price too high / unclear ROI
- Needs multi-asset (NVIDIA, equities) — point to [`briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md`](briefs/NVIDIA_LEAPS_VALIDATION_BRIEF.md) as separate experiment
- Wants auto-trading — out of scope; paper track only on MVP1
- Data trust / “is this real edge?” — emphasize protocol + freeze/review, not returns

## Outreach log (copy row per attempt)

| Date | Contact | Offer variant | Y/N | Notes |
|------|---------|---------------|-----|-------|
| | | research beta | | |

Also update [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) **Paid interest** row when a real conversation completes.

## Commercial boundary (do not say)

- Guaranteed profit or proven alpha
- Fully automated trading
- NVIDIA/LEAPS product ready today (brief only)
