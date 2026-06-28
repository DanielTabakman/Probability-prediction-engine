# Milestone: Trader Workflow Integration v1

**Milestone ID:** `trader_workflow_integration_v1`  
**Direction pivot:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — `trader-workflow-integration-v1`  
**As-of:** 2026-06-25

---

## What this milestone is

**Goal:** A trader **uses MSOS as part of their trading process** — not a one-off demo tour.

**Not** a single relay chapter. **Not** “ship ETH” or “finish demo” in isolation.

**Trader Workflow Integration v1** means the product fits a real decision loop: before or during a trade idea, the trader opens MSOS to see what options imply, where they disagree, what expression fits, and they **come back** to check or review — self-serve, without operator hand-holding. Workflow research confirms *where* in the process it lands and ships fixes from **strong+** signals.

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
| **E** | **Forward consistency** | [`FORWARD_CONSISTENCY_PROGRAM_V1.md`](FORWARD_CONSISTENCY_PROGRAM_V1.md) | Option-implied vs futures/perp parity in Strategy Lab (research-only) |

**Active relay execution** (automation): workstream **B** — `ppe_crypto_multi_asset_v1` is the current `READY` chapter. Workstreams A, C, D run in parallel via product slices and operator/steward activity — not blocked on crypto COMPLETE. Workstream **E** (`forward_consistency_*` chapters) runs on **side channel** when main track idle.

---

## Milestone complete when

1. **Process fit:** ≥3 external traders report using MSOS **during** their trading process (pre-trade research, structure selection, or post-entry review) — not just “completed the tour” (logged in validation with `signal: strong+` or `very_strong`).
2. **Return without prompt:** ≥2 of those return within 7 days **without** a scheduled follow-up (strongest process-integration signal).
3. **Wedge depth:** BTC + ETH selector live in Strategy Lab with witness green (crypto chapter COMPLETE).
4. **Loop coherence:** P4→P7 journey matches storyboard semantics for **Disagreement** mode; tutorial contract green on production.
5. **Learning shipped:** ≥1 **strong+** observation from (1)–(2) triaged to merged product work or backlog row.

---

## Explicitly not this milestone

- Live execution / order routing
- Stripe billing automation (deferred)
- Equity options / NVDA LEAPS (next milestone after crypto + G-04 signal)
- Interaction modes 2–7 as dedicated surfaces (research-gated)
- Platform sprawl (identity entitlements expansion beyond chartered phases)

---

## How BUILD agents use this

- **Scope test:** Does the slice help a trader **use MSOS in their process** (onboarding, wedge depth, loop fidelity, or learning ingestion)?
- **Relay order:** FRONTIER queue still controls slice automation; this doc controls **why**.
- **Tutorial rule:** Any visitor-visible workflow change → update tour in same PR ([`CLIENT_SELF_SERVE_DEMO_V1.md`](CLIENT_SELF_SERVE_DEMO_V1.md)).

---

## After milestone

Steward SELECTION for next umbrella — candidates: equity wedge (`ppe_equity_options_v1`), distribution scale-up, or commercial pilot — based on validation log signal, not platform completeness.
