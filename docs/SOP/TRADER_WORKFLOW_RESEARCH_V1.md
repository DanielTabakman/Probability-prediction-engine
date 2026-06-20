# Trader workflow research v1

**Purpose:** Operational guide for **workflow research and design ingestion** after (or in parallel with late) Minimum Credible Demo work — not generic fintech category validation.

**Prerequisite gate:** [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) (primary focus shifts here when gate **PASSED**; light conversations allowed earlier per [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md))

**Log destination:** [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) · **Session timing:** [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)

---

## What this is (and is not)

| This is | This is not |
|---------|-------------|
| Learning exact **workflow, language, trust layer, disagreement type, decision moment** | Proving “traders care about options” or “fintech tools matter” |
| Ingesting observations into **shippable product changes** | Vanity metrics or generic PMF theater |
| High-signal conversations with BTC options traders | Broad online sentiment scraping |

**Assumption (already held):** Traders care about market disagreement, options-implied information, and useful tools. We are learning **how MSOS/PPE fits their decision loop**.

---

## Research questions (ask every session)

1. **What kind of disagreement is this?** (directional, vol, tail, timing, skew, structure, liquidity/risk-premium, hedge/constraint — see [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md))
2. **When does the trader notice it?** (pre-market, during session, after move, rolling expiry)
3. **What data/tool/content triggers the thought?**
4. **How do they currently express it?** (structure, size, venue, notes)
5. **What would make them trust or distrust the tool?**
6. **What do they check before acting?**
7. **What do they monitor after entry?**
8. **What makes them abandon the thesis?**
9. **Usage mode:** pre-trade, post-trade, research, journal, alert, or expression planner?
10. **Interaction mode:** why did they open MSOS? (disagreement, expression search, hedging, scenario planning, timing, monitoring, learning/review — see [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md))

Tag answers in validation log rows. Prefer **disagreement** language over internal “snapshot” jargon in notes. When logging, include `interaction_mode` and `disagreement_type` where applicable (see interaction modes doc § Research tagging).

---

## Signal ranking (tag every observation)

| Rank | Signal | Example |
|------|--------|---------|
| **Weak** | What traders say they like online | Twitter polls, generic “cool chart” |
| **Medium** | Content/tools they **repeatedly consume** | Same vendor screen daily, bookmarked calc |
| **Strong** | Their **current decision workflow** | Walkthrough of last trade thesis |
| **Very strong** | **Observed use** of our product | Unprompted return, shared screen using MSOS/PPE |
| **Strongest** | **Return, referral, payment** | Comes back without ping, introduces peer, offers to pay |

When logging in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md), include field or note: `signal: weak|medium|strong|very_strong|strongest`.

**Build rule:** Prefer changes backed by **strong+** signals. **Weak** alone does not justify platform expansion.

---

## Ingestion path (learning → shippable)

1. Log session with signal rank + disagreement type.
2. Steward triage: does this map to MCD gap, embed UX, workflow copy, or PPE legibility?
3. If shippable → backlog row with `focusPlaybookTier` and link to observation.
4. If not shippable → note in validation log; do not auto-widen scope.

Autobuilder/control-plane work that ingests workflow learning must cite the observation per [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md).

---

## Allowed before MCD pass

**Light** trader workflow conversations (1–2 sessions/month) are allowed while factory + MCD chapters run — they must not block BUILD throughput or pull forward post-MCD commercial phases.

---

## Session script (compact)

Full script: [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) § Session script.

After demo, spend **≥50% of session time** on research questions above — not feature tour.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v1 — workflow research ops, signal ranking, ingestion path |
| 2026-06-20 | Research Q10 + tagging — interaction modes ontology |
