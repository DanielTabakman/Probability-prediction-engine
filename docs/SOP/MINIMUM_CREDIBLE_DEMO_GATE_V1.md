# Minimum Credible Demo gate v1

**Purpose:** Operational pass/fail checklist for the **Minimum Credible Demo (MCD)** — the product milestone before broad platform or commercial expansion. Passing shifts primary focus to [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md).

**Strategic context:** [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md)

**Status:** **NOT PASSED** (as-of 2026-06-20) — steward marks **PASSED** in § Status when all required criteria are witness-verified.

---

## What MCD is

A demo where a BTC options trader can use MSOS as **one coherent product** — not a fixture walkthrough, not a nested Streamlit app, not a 20-minute guided tour.

**North star timing:** A new tester grasps market-implied vs their belief in **under 15 minutes** without hand-holding ([`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)).

---

## Required criteria (all must pass)

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | **MSOS opens cleanly** | Production or research-beta URL loads; auth path works per [`MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md`](MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md) |
| 2 | **Platform-shaped shell** | Homepage + authenticated shell match storyboard intent; not “dev fixture” chrome — see visual parity evidence |
| 3 | **PPE inside MSOS** | Strategy Lab shows PPE via **native integration surface** (display API + MSOS chart shell) or honest chromeless embed — not default box-in-box full Streamlit chrome ([`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md)) |
| 4 | **Market-implied distribution legible** | User can see what the market implies (chart or summary) without leaving MSOS workflow |
| 5 | **Belief / disagreement compare** | User can set or view belief and compare to market-implied view |
| 6 | **Disagreement kind visible** | Product names or exposes **what kind of disagreement** (even if primitive label — see charter disagreement types) |
| 7 | **One expression path** | User sees one plausible **sim-only** expression / action path (thesis → expression planning) |
| 8 | **Save / review / history visible** | Concept is visible in UX — server-side preferred ([`msos_workflow_persistence_v1`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md)); primitive/local preview acceptable only with honest labels |
| 9 | **No 20-minute explanation** | Operator session: tester reaches comprehension per session script without extended narration |

---

## BUILD mapping (chapters that deliver MCD)

MCD is **not** the full live product sequence through phase 7b. Required engineering path:

| Track | chapterId | Role for MCD |
|-------|-----------|--------------|
| **Required** | `msos_production_wiring_v1` | Sign-in, nav, live paths — **COMPLETE** |
| **Required** | `msos_user_state_v1` | Command Center reads PPE evaluation activity |
| **Required** | `msos_workflow_persistence_v1` | Server thesis/expression store |
| **Required** | `msos_strategy_lab_embed_shell_v1` | Seamless PPE-in-MSOS integration surface |
| **Already shipped (UI)** | MSOS P2–P8 storyboard chapters | Workflow routes exist; wire to live data where MCD criteria need it |

**Post-MCD (deferred unless SELECTION'd):** phases 4a–7b in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) — multi-user identity, live monitor/history, E2E witness, entitlements, Stripe.

---

## Relationship to other gates

| Gate | Role |
|------|------|
| **MCD (this doc)** | **Scope authority** — what we build before workflow research |
| **P8 validation report** | **Evidence rollup** during/after workflow research — not a blocker to *starting* light trader conversations |
| **Wedge proof / cohort metrics** | Tracked in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — strengthen signal ranking in workflow research |

MCD **supersedes** “interim engineering authorization” from [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) for **scope expansion** decisions.

---

## Status

| Field | Value |
|-------|--------|
| **Gate** | NOT PASSED |
| **Last reviewed** | 2026-06-20 |
| **Blockers** | `msos_user_state_v1` Platform-Slice003 in flight; then `msos_workflow_persistence_v1`; then `msos_strategy_lab_embed_shell_v1` |
| **After pass** | Steward updates status to **PASSED**; primary focus → [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) |

---

## Operator sign-off (when ready)

1. Walk session script ([`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) § Session script) on production URL.
2. Check all nine criteria above.
3. Log at least one **strong** or **very strong** signal row per [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) (optional before pass; required for sustained research phase).
4. Update **Status** table + note in [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v1 — MCD criteria, BUILD mapping, precedence vs P8 |
