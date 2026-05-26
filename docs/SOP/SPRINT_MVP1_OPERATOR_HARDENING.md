# MVP1 operator / demo hardening — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_PHASE2_CHAPTER_SELECTION_OUTCOME.md`](POST_PHASE2_CHAPTER_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Harden operator confidence after Phase 2 closeout: smoke witness for MVP1 trust-strip disclosure (Slice006), deploy witness freshness, and runbook alignment — without recovery merge, billing, or new product surfaces.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after each PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS with run IDs in [`MVP1_OPERATOR_EVIDENCE_STATUS.md`](MVP1_OPERATOR_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on each slice closeout.

## Not now

- Phase 3 commercial wrapper (new charter required).
- `mvp1_benchmark_substrate.py` port or blind recovery merge.
- Billing, multi-asset automation.

---

## Slice map

### MVP1-OperatorHardening-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Goal:** Accept sprint spec, phase plan, frontier sync, SELECTION record.

**Closed** 2026-05-19.

---

### MVP1-OperatorHardening-Smoke-Slice002 — trust-strip smoke witness (PRODUCT) — **CLOSED**

**Goal:** `MVP1_compact_verification` smoke asserts always-visible trust strip includes MVP1 decision markers (`MVP1 data quality`).

**Closed** 2026-05-19 — harness `trust_strip_mvp1_found`; dual smoke `20260519_164110` + `164330`.

---

### MVP1-OperatorHardening-Witness-Slice003 — deploy witness refresh (CONTROL) — **CLOSED**

**Goal:** Refresh [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) target SHA + Phase 2 smoke refs; CTA row stays **pending** until steward `.env`.

**Closed** 2026-05-19 — target SHA `7961c33`+; CTA still **pending**.

---

### MVP1-OperatorHardening-Closeout-Slice004 — chapter close (CONTROL) — **CLOSED**

**Goal:** Chapter **COMPLETE** in frontier; post-chapter SELECTION prep doc.

**Closed** 2026-05-19 — [`POST_MVP1_OPERATOR_HARDENING_SELECTION.md`](POST_MVP1_OPERATOR_HARDENING_SELECTION.md).

---

## Sprint status

**MVP1 operator hardening:** **COMPLETE** 2026-05-19.
