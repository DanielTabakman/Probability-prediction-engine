# Phase 2 reconcile report — `main` vs `recovery/frontier-steward-v2_1-baseline`

**Date:** 2026-05-19 · **Baseline `main`:** `03a6835`+ · **Reconcile slice:** `MVP1-Phase2-Reconcile-Slice002`

---

## Executive summary

`main` already ships Sprint004-class **directional candidate strip** (`build_directional_candidate_strip_payload`, harness `slice004` witness, [`tests/test_directional_candidate_strip.py`](../../tests/test_directional_candidate_strip.py)). Recovery’s large `app.py` delta mostly reflects **Validation/Commercial/MVP1 banner work on `main`** plus recovery-era **MVP1 substrate module** layout. **Do not blind-merge recovery.** Product-Slice003 ports a **narrow MVP1 UI-alignment bundle**: copy/runtime gates for hidden execution surfaces, decision-ready review MVP1 copy, belief strike-policy alignment, and harness trade-ticket observation logic — while **keeping** Reliability smoke timeout caps on `main`.

---

## Per-file decisions

| Path | Decision | Notes |
|------|----------|-------|
| [`src/viz/app.py`](../../src/viz/app.py) | **defer** | ~951-line diff; `main` is ahead (research offer, MVP1 compact path). Cherry-pick only call-site for `mvp1_exclude_execution_ui` in Slice003. |
| [`src/viz/app_panels.py`](../../src/viz/app_panels.py) | **already_on_main** + **port** (narrow) | Directional/width strips present; port `render_decision_ready_review(..., mvp1_exclude_execution_ui=)`. |
| [`src/viz/mvp1_benchmark_substrate.py`](../../src/viz/mvp1_benchmark_substrate.py) | **defer** | Recovery-only module (+495 lines). `main` uses [`mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py) instead — do not duplicate. |
| [`src/viz/implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) | **defer** | Recovery wires `build_mvp1_benchmark_substrate` into verification; incompatible with `main` decision surface without full substrate port. |
| [`src/viz/belief_disagreement_hints.py`](../../src/viz/belief_disagreement_hints.py) | **port** | `strike_policy_illustrative_for_runtime()` — MVP1 default UI copy alignment. |
| [`src/viz/decision_ready_review.py`](../../src/viz/decision_ready_review.py) | **port** | `mvp1_exclude_execution_ui` parameter + non-ticket linkage copy. |
| [`tests/test_mvp1_benchmark_substrate.py`](../../tests/test_mvp1_benchmark_substrate.py) | **defer** | Tests recovery substrate module not on `main`. |
| [`tests/test_decision_ready_review.py`](../../tests/test_decision_ready_review.py) | **port** | `test_mvp1_excludes_trade_ticket_language`. |
| [`scripts/implied_lab_ui_smoke_harness.py`](../../scripts/implied_lab_ui_smoke_harness.py) | **port** (partial) | `_set_mode_when_advanced_lab_ui_enabled`, loose expander click, `mvp1_execution_surfaces_hidden_by_default` helper — **not** recovery’s inverted `trade_ticket_found` semantics (`main` requires literal absent ticket for `MVP1_compact_verification`). **Preserve** Reliability timeout caps @ `559f908`. |
| Directional strip (Sprint004-Slice004 class) | **already_on_main** | No PRODUCT rebuild of strip; witness in harness. |

**Diff stat (reference):** `git diff --stat main...origin/recovery/frontier-steward-v2_1-baseline -- src/viz/ tests/ scripts/implied_lab_ui_smoke_harness.py` → 9 files, +1480 / -452.

---

## Steward sign-off — Product-Slice003 scope

| Field | Value |
|-------|--------|
| **Slice ID** | `MVP1-Phase2-Product-Slice003` |
| **Scope** | **MVP1 UI exclusions alignment** (copy + harness gates) — **not** full recovery merge |
| **Historical reference** | Sprint004-Slice004 directional strip — **already_on_main** |
| **Agent recommendation** | **Approved for BUILD** per reconcile table above |
| **Steward** | Agent lane sign-off 2026-05-19 (narrow port); steward may veto before merge |

---

## Next after Slice003

- **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **SELECTION:** [`POST_PHASE2_PRODUCT_SLICE003_SELECTION.md`](POST_PHASE2_PRODUCT_SLICE003_SELECTION.md) → **`MVP1-Phase2-Product-Slice005`**
