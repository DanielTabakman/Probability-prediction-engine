# MVP1 Phase 2 — Product-Slice005 (decision surface parity audit)

**Parent sprint:** [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md)  
**SELECTION:** [`POST_PHASE2_PRODUCT_SLICE003_SELECTION.md`](POST_PHASE2_PRODUCT_SLICE003_SELECTION.md)  
**Reconcile matrix:** [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md)  
**Baseline:** **`main`** @ `f828fb3`+

**Status:** **CHARTERED** (stub) — not started until BUILD agent accepts slice.

---

## Slice ID

`MVP1-Phase2-Product-Slice005`

---

## Intent

Audit and tighten **parity** between MVP1 decision surface logic on `main` ([`src/viz/mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py)) and what operators see in the verification / MVP1 panels — labels, trust/materiality strings, and primary-output state — **without** porting recovery’s [`mvp1_benchmark_substrate.py`](../../src/viz/mvp1_benchmark_substrate.py).

Produce a short **parity notes** section in [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md) (or appendix in reconcile report) listing matched vs deferred gaps.

---

## In scope

- Read-only diff mindset: `main` panel call sites vs decision surface outputs
- Copy/label alignment where mismatch is provable in tests (&lt;50 lines per fix)
- New/extended unit tests under `tests/test_*decision*` or existing MVP1 test modules
- `python -m pytest -q` green; dual smoke if `src/viz/**` changes

---

## Out of scope (defer per reconcile)

- Import or recreate `mvp1_benchmark_substrate.py`
- Blind merge of [`src/viz/app.py`](../../src/viz/app.py)
- [`implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) substrate wiring
- [`tests/test_mvp1_benchmark_substrate.py`](../../tests/test_mvp1_benchmark_substrate.py)

---

## Acceptance

1. Parity audit documented (matched / gap / defer table).
2. Any code delta bounded; no new quantitative metrics without steward SELECTION.
3. Engineering gates: pytest + dual smoke when viz touched.
4. `MVP1_FRONTIER.md`, `HANDOFF.md`, `PPE_INTEGRATED_STATUS.md` updated on **CLOSED**.

---

## Evidence targets

| Gate | Target |
|------|--------|
| pytest | green (baseline **157** @ Slice003 closeout) |
| dual smoke | PASS if `src/viz/**` changed |
