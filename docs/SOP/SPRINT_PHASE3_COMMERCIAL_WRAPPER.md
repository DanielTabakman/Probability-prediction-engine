# Phase 3 commercial wrapper (v0) — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (commercial wrapper deferred until core loop is valuable).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_PRODUCT_SHELL_SELECTION_OUTCOME.md`](POST_MVP1_PRODUCT_SHELL_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Add a **bounded commercial wrapper** around the existing MVP1 demo experience: consistent CTA / offer copy, guardrails against “signal” language, and a lightweight operator checklist — without adding billing, auth, or automation.

---

## Sprint-level acceptance

1. `python -m pytest -q` green before/after PRODUCT slice.
2. `python scripts/run_mvp1_dual_implied_lab_smoke.py` exit 0 with run IDs recorded.
3. Closeout updates `MVP1_FRONTIER`, `HANDOFF`, and `PPE_INTEGRATED_STATUS`.

---

## Not now

- Paywall / billing automation
- New backend services
- Multi-asset expansion
- Recovery merges

---

## Slice map

### Phase3-CommercialWrapper-Control-Slice001 — charter (EVIDENCE-PLANE)

Charter witness: sprint spec, phase plan, evidence stub, and queue/manifest/frontier alignment; baseline `main`.

### Phase3-CommercialWrapper-Product-Slice002 — commercial wrapper polish (PRODUCT-PLANE)

Bounded copy/CTA wrapper work (no billing automation).

### Phase3-CommercialWrapper-Smoke-Slice003 — dual smoke witness (EVIDENCE-PLANE)

Dual smoke witness run IDs recorded in evidence doc.

### Phase3-CommercialWrapper-Closeout-Slice004 — chapter close (EVIDENCE-PLANE)

Evidence witness + steward control-closeout (updates `MVP1_FRONTIER`, `HANDOFF`, `PPE_INTEGRATED_STATUS`, continuity brief).

