# MVP1 memory & review enrichment — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md).  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md).  
**SELECTION:** [`POST_MVP1_OPERATOR_HARDENING_SELECTION_OUTCOME.md`](POST_MVP1_OPERATOR_HARDENING_SELECTION_OUTCOME.md).  
**Relay baseline:** **`main`**.

---

## Sprint intent

Close MVP1 Phase 5/6 follow-ons on the landed freeze → review → class-summary stack: pending-review UX (expiry filter, sort, optional paper tag), class-summary filters wired to store queries, and rollup/table export — without recovery merge, billing, or execution surfaces.

## Sprint-level acceptance

1. **`python -m pytest -q`** green before/after each PRODUCT slice.
2. **`python scripts/run_mvp1_dual_implied_lab_smoke.py`** PASS with run IDs in [`MVP1_REVIEW_ENRICHMENT_EVIDENCE_STATUS.md`](MVP1_REVIEW_ENRICHMENT_EVIDENCE_STATUS.md).
3. `MVP1_FRONTIER` + `HANDOFF` + [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) updated on chapter closeout.

## Not now

- Phase 3 commercial wrapper (new charter required).
- `mvp1_benchmark_substrate.py` port or blind recovery merge.
- Billing, multi-asset automation, execution / ticket engine.

---

## Slice map

### MVP1-ReviewEnrichment-Control-Slice001 — charter (CONTROL) — **CLOSED**

**Goal:** Accept sprint spec, phase plan, frontier sync, SELECTION record.

**Closed** 2026-05-19.

---

### MVP1-ReviewEnrichment-Product-Slice002 — Phase 5 pending-review UX (PRODUCT) — **CLOSED**

**Goal:** Pending snapshot list: expiry filter (store-backed), sort options, optional **paper tag** on reviews (SQLite column + save/load).

**Closed** 2026-05-19 — `tests/test_frozen_review_store.py`.

---

### MVP1-ReviewEnrichment-Product-Slice003 — Phase 6 store-backed filters (PRODUCT) — **CLOSED**

**Goal:** Class summary uses `list_completed_review_snapshots` **expiry** + date filters in SQL.

**Closed** 2026-05-19.

---

### MVP1-ReviewEnrichment-Product-Slice004 — Phase 6 export (PRODUCT) — **CLOSED**

**Goal:** Download rollup as JSON + CSV; reviewed snapshot table CSV.

**Closed** 2026-05-19 — `serialize_rollup_csv` + UI buttons.

---

### MVP1-ReviewEnrichment-Closeout-Slice005 — chapter close (CONTROL) — **CLOSED**

**Goal:** Chapter **COMPLETE** in frontier; evidence doc; post-chapter SELECTION prep.

**Closed** 2026-05-19 — [`MVP1_REVIEW_ENRICHMENT_EVIDENCE_STATUS.md`](MVP1_REVIEW_ENRICHMENT_EVIDENCE_STATUS.md).

---

## Sprint status

**MVP1 memory & review enrichment:** **COMPLETE** 2026-05-19.
