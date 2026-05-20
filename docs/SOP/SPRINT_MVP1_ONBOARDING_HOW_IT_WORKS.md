# MVP1 onboarding / How it works — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 5.  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md`](POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Ship a bounded **“How it works”** education surface in the MVP1 implied lab context so early users can understand: **market-implied distribution**, **belief overlay**, **disagreement**, **strategy families (fit, not recommendation)**, and the **no-advice** boundary — without changing belief math, disagreement classification, or data paths.

---

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs recorded in [`MVP1_ONBOARDING_HOW_IT_WORKS_EVIDENCE_STATUS.md`](MVP1_ONBOARDING_HOW_IT_WORKS_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

---

## Not now

- Billing, paywall, or Phase 3 commercial wrapper.
- Execution engine, live trading, or ticket automation.
- Multi-asset scope beyond current MVP1 lab.
- Recovery merge of `mvp1_benchmark_substrate.py` or blind `app.py` merge.
- Changes to disagreement **classification** rules or core derivation math (copy/explain only in scope).

---

## Slice map

### MVP1-OnboardingHowItWorks-Control-Slice001 — charter (CONTROL) — **OPEN**

Charter relay: align sprint links, frontier table, evidence stub; no product code unless slice spec explicitly expands (default: docs-only charter).

### MVP1-OnboardingHowItWorks-Product-Slice002 — How it works UX (PRODUCT) — **OPEN**

Bounded onboarding / explainer UI (e.g. expander, tutorial section, or dedicated panel) using plain language; may reuse or extend `src/viz/tutorial.py` (`render_tutorial_section`).

### MVP1-OnboardingHowItWorks-Smoke-Slice003 — dual smoke (CONTROL) — **OPEN**

Dual smoke witness with run IDs in evidence status.

### MVP1-OnboardingHowItWorks-Closeout-Slice004 — chapter close (CONTROL) — **OPEN**

Chapter close: integrated status + handoff + SELECTION prep for the following chapter (steward).

---

## Sprint status

**CHARTERED** — SELECTION complete 2026-05-20.
