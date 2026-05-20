# MVP1 belief-input UX — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) §15B slice 3.  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_FRIENDS_FIRST_SELECTION_OUTCOME.md`](POST_MVP1_FRIENDS_FIRST_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Make belief inputs feel **human** in MVP1 lab mode: plain-English labels, default **±% move (1σ)** path visible, **σ_ln (advanced)** behind a nested disclosure — no change to belief math or disagreement classification.

## Sprint-level acceptance

1. **`python -m pytest -q`** green.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS with run IDs in evidence status.
3. Post-MVP1 lab UI (`PPE_POST_MVP1_LAB_UI=1`) belief block **unchanged** (regression guard).

## Not now

- Landing/onboarding pages, billing, recovery merge, new decision logic.

---

## Slice map

### MVP1-BeliefInput-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-20.

### MVP1-BeliefInput-Product-Slice002 — belief UX (PRODUCT) — **CLOSED**

**Closed** 2026-05-20.

### MVP1-BeliefInput-Smoke-Slice003 — dual smoke (CONTROL) — **CLOSED**

**Closed** 2026-05-20 — `20260520_024407` + `024438`.

### MVP1-BeliefInput-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-20.

---

## Sprint status

**COMPLETE** 2026-05-20.
