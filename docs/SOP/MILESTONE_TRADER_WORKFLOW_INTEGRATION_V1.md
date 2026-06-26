# Milestone: Trader Workflow Integration v1

**Milestone ID:** `trader_workflow_integration_v1`  
**Direction pivot:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — `trader-workflow-integration-v1`  
**As-of:** 2026-06-25

---

## What this milestone is

**Not** a single relay chapter. **Not** “ship ETH” or “finish demo” in isolation.

**Trader Workflow Integration v1** means a BTC options trader can **self-serve** through the MSOS disagreement loop — discover what the market implies, state where they disagree, sketch an expression, save/review, and return — **without operator-led demos**, with enough fidelity that **workflow research produces strong+ signals** that ship back as product changes.

Canon loop (backplane): **thesis → implied probability → disagreement → expression → save/review → monitor/history**.

---

## Foundation (already shipped)

| Piece | Status |
|-------|--------|
| MCD gate | **PASSED** 2026-06-21 |
| Usable demo (`msos_usable_demo_v1`) | **COMPLETE** 2026-06-25 |
| MSOS shell + PPE embed | Production walkable |
| Storyboard routes P1–P8 (engineering) | Shipped |

---

## Workstreams (parallel — milestone completes when all pass)

| # | Workstream | Doc / chapter | Outcome |
|---|------------|---------------|---------|
| **A** | **Self-serve onboarding** | [`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md) | Prospects use public URL + in-app tour; operator demos optional only |
| **B** | **Wedge depth** | `ppe_crypto_multi_asset_v1` relay | ETH + asset registry; same distribution semantics as BTC |
| **C** | **Workflow loop fidelity** | Storyboard P4–P7 surfaces + [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md) | Disagreement → confirm → expression → monitor/history feels coherent end-to-end |
| **D** | **Learning loop** | [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) + [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) | Sessions logged; strong+ signals triaged to shippable backlog |

**Active relay execution** (automation): workstream **B** — `ppe_crypto_multi_asset_v1` is the current `READY` chapter. Workstreams A, C, D run in parallel via product slices and operator/steward activity — not blocked on crypto COMPLETE.

---

## Milestone complete when

1. **Self-serve:** ≥3 external testers complete the loop via public URL + tour **without** a scheduled operator demo (logged in validation).
2. **Workflow signal:** ≥1 **strong+** observation triaged to a shippable backlog row or merged product slice.
3. **Wedge depth:** BTC + ETH selector live in Strategy Lab with witness green (crypto chapter COMPLETE).
4. **Tutorial contract:** `verify_demo_tutorial_contract.py` + production tutorial crawl green after feature changes.
5. **Loop coherence:** Steward sign-off that P4→P7 journey matches storyboard semantics for the **Disagreement** interaction mode (mode 1).

---

## Explicitly not this milestone

- Live execution / order routing
- Stripe billing automation (deferred)
- Equity options / NVDA LEAPS (next milestone after crypto + G-04 signal)
- Interaction modes 2–7 as dedicated surfaces (research-gated)
- Platform sprawl (identity entitlements expansion beyond chartered phases)

---

## How BUILD agents use this

- **Scope test:** Does the slice advance self-serve loop, wedge depth, loop fidelity, or learning ingestion?
- **Relay order:** FRONTIER queue still controls slice automation; this doc controls **why**.
- **Tutorial rule:** Any visitor-visible workflow change → update tour in same PR ([`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md)).

---

## After milestone

Steward SELECTION for next umbrella — candidates: equity wedge (`ppe_equity_options_v1`), distribution scale-up, or commercial pilot — based on validation log signal, not platform completeness.
