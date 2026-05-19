# MVP1 Phase 2 — Product-Slice006 (trust strip MVP1 disclosure)

**Parent sprint:** [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md)  
**SELECTION:** [`POST_PHASE2_SLICE005_SELECTION_OUTCOME.md`](POST_PHASE2_SLICE005_SELECTION_OUTCOME.md)  
**Baseline:** **`main`** @ `707610c`+

**Status:** **CLOSED** 2026-05-19 — trust strip MVP1 lines from `verification["mvp1_decision"]`.

---

## Slice ID

`MVP1-Phase2-Product-Slice006`

---

## Intent

Extend [`build_trust_strip_lines`](../../src/viz/implied_lab_provenance.py) so the always-visible trust strip surfaces **MVP1 decision** trust fields (`data_quality`, `primary_output_state`, short reason) from existing `verification["mvp1_decision"]` — **without** importing recovery’s `mvp1_benchmark_substrate` module.

---

## In scope

- [`src/viz/implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) — `build_trust_strip_lines`
- Unit tests (`tests/test_mvp1_trust_strip.py` or panel parity module)
- pytest + dual smoke if `src/viz/**` changes

---

## Out of scope

- `mvp1_benchmark_substrate.py`, blind `app.py` merge, billing, new metrics

---

## Acceptance

1. Trust strip shows MVP1 lines when `mvp1_decision` present; honest placeholders when absent.
2. pytest green; dual smoke PASS if viz touched.
3. Evidence in [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md).
