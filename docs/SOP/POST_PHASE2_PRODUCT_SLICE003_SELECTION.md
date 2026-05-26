# Post–Product-Slice003 — SELECTION outcome (2026-05-19)

**Status:** **SELECTION COMPLETE** — next BUILD slice chartered on **`main`**.

**Inputs:** Reconcile-Slice002 + Product-Slice003 + Closeout-Slice004 **CLOSED**; pytest **157** passed; dual smoke `20260519_144000` + `20260519_144350`; paid-interest **N** (honest).

---

## Historical truth (do not re-build)

| Item | Repo truth |
|------|------------|
| **Sprint004-Slice004 directional candidate strip** | **already_on_main** — `build_directional_candidate_strip_payload`, harness `slice004` witness, [`tests/test_directional_candidate_strip.py`](../../tests/test_directional_candidate_strip.py) |
| **Product-Slice003** | **Copy + harness alignment only** — MVP1 UI exclusions, `decision_ready_review`, `belief_disagreement_hints`, harness gates; **not** a strip rebuild |
| **Recovery branch** | **Do not blind-merge** — matrix in [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md) |

---

## Selected next BUILD slice (steward-default)

| Field | Value |
|-------|--------|
| **Slice ID** | `MVP1-Phase2-Product-Slice005` |
| **Plane** | PRODUCT (bounded audit + doc/tests; no full substrate port) |
| **Sprint spec** | [`SPRINT_MVP1_PHASE2_SLICE005.md`](SPRINT_MVP1_PHASE2_SLICE005.md) |
| **Phase plan** | [`PHASE_PLANS/mvp1_phase2_on_main_relay.json`](PHASE_PLANS/mvp1_phase2_on_main_relay.json) |
| **Goal** | **Decision surface / substrate panel parity audit** on `main` — align labels, trust/materiality copy, and verification-panel surfacing with [`mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py); document gaps vs recovery substrate **without** importing [`mvp1_benchmark_substrate.py`](../../src/viz/mvp1_benchmark_substrate.py) |

---

## Port / defer (from reconcile — binding for Slice005)

| Path | Slice005 stance |
|------|-----------------|
| [`mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py) + panel call sites | **port/audit** — primary scope |
| [`mvp1_benchmark_substrate.py`](../../src/viz/mvp1_benchmark_substrate.py) | **defer** — duplicate layout on recovery only |
| [`implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) substrate wiring | **defer** |
| Blind [`app.py`](../../src/viz/app.py) merge | **defer** |
| [`tests/test_mvp1_benchmark_substrate.py`](../../tests/test_mvp1_benchmark_substrate.py) | **defer** |
| Narrow test port from recovery | **only if** audit finds a single missing assertion (&lt;50 lines); otherwise document defer |

**Alternative rejected for default:** wholesale recovery test port — unjustified while substrate module stays deferred.

---

## Rationale

| Candidate | Decision |
|-----------|----------|
| **Slice005 parity audit** | **Selected** — Slice003 closed UI-exclusion copy; next honest gap is decision-surface **consistency** on `main`, not another strip |
| **Full substrate module port** | **Deferred** — reconcile explicitly defers recovery module |
| **Blind app.py / provenance merge** | **Rejected** |

---

## Steward parallel (non-blocking)

1. VPS `.env` → CTA **PASS** — [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)
2. Paid-interest call → **Y/N** — [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) (**keep N** until live)

---

## Next execution step

Run **`MVP1-Phase2-Product-Slice005`** per [`SPRINT_MVP1_PHASE2_SLICE005.md`](SPRINT_MVP1_PHASE2_SLICE005.md). Update [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md) on closeout.
