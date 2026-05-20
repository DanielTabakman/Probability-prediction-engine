# MVP1 smoke regression — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_REVIEW_ENRICHMENT_SELECTION_OUTCOME.md`](POST_MVP1_REVIEW_ENRICHMENT_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Restore green **dual implied-lab smoke** after review-enrichment closeout timeout: raise bounded MVP1_compact budget, improve compact marker waits (no Verification expander when above-fold digest is enough), env override for slow hosts, runbook note.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** exit **0** with run IDs in [`MVP1_SMOKE_REGRESSION_EVIDENCE_STATUS.md`](MVP1_SMOKE_REGRESSION_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on closeout.

## Not now

- Phase 2 recovery merge, `mvp1_benchmark_substrate.py` port.
- Phase 3 commercial wrapper, billing, multi-asset automation.
- New implied-lab product surfaces.

---

## Slice map

### MVP1-SmokeRegression-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Closed** 2026-05-19.

---

### MVP1-SmokeRegression-Harness-Slice002 — harness (PRODUCT) — **CLOSED**

**Closed** 2026-05-19 — 1200s budget, σ_ln mode, compact marker waits, runbook §6.

---

### MVP1-SmokeRegression-Witness-Slice003 — dual smoke witness (CONTROL) — **CLOSED**

**Closed** 2026-05-19 — dual smoke `20260519_232908` + `233106`.

---

### MVP1-SmokeRegression-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Closed** 2026-05-19 — [`MVP1_SMOKE_REGRESSION_EVIDENCE_STATUS.md`](MVP1_SMOKE_REGRESSION_EVIDENCE_STATUS.md).

---

## Sprint status

**MVP1 smoke regression:** **COMPLETE** 2026-05-19.
