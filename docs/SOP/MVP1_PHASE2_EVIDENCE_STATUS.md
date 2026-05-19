# Phase 2 on `main` — evidence status

**Chapter:** [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) · **Baseline:** `main` @ `566f4f0`+ · **One-pager:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)

**Reconcile report:** [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md)

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **161** passed (2026-05-19, Product-Slice006) |
| Dual smoke | **PASS** | `20260519_155858` + `20260519_160103` (post–Slice006 viz) |

---

## Slice status

| Slice | Status |
|-------|--------|
| Control-Slice001 | **CLOSED** 2026-05-19 |
| Reconcile-Slice002 | **CLOSED** 2026-05-19 |
| Product-Slice003 | **CLOSED** 2026-05-19 — MVP1 UI exclusions alignment |
| Closeout-Slice004 | **CLOSED** 2026-05-19 — checkpoint |
| Product-Slice005 | **CLOSED** 2026-05-19 — decision surface / panel parity |
| Product-Slice006 | **CLOSED** 2026-05-19 — trust strip MVP1 disclosure |
| Chapter-Closeout-Slice007 | **CLOSED** 2026-05-19 — Phase 2 chapter **COMPLETE** |

**Chapter status:** **COMPLETE** 2026-05-19 — [`POST_PHASE2_CHAPTER_SELECTION.md`](POST_PHASE2_CHAPTER_SELECTION.md)

---

## Product-Slice006 — trust strip MVP1 disclosure

**Module:** [`src/viz/implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) — `build_trust_strip_lines` reads `verification["mvp1_decision"]` for `data_quality`, `primary_output_state`, optional `primary_output_reason` (non-advisory).

| Area | Status | Notes |
|------|--------|-------|
| Trust strip MVP1 lines | **shipped** | No `mvp1_benchmark_substrate` import |
| `mvp1_benchmark_substrate` | **defer** | Recovery-only per reconcile |
| Blind `app.py` merge | **defer** | — |

**Tests added:** [`tests/test_mvp1_trust_strip.py`](../../tests/test_mvp1_trust_strip.py)

---

## Product-Slice006 smoke witness

| Run ID | Scenario | Exit | elapsed_s |
|--------|----------|------|-----------|
| 20260519_155858 | MVP1_compact_verification | 0 | 125.5 |
| 20260519_160103 | A_width_target_payoff | 0 | 102.0 |

**Dual smoke total:** ~228.6s.

---

## Product-Slice005 — decision surface parity audit

**Module:** [`src/viz/mvp1_decision_surface.py`](../../src/viz/mvp1_decision_surface.py) · **Panels:** [`src/viz/app_panels.py`](../../src/viz/app_panels.py) · **Payload:** [`src/viz/implied_lab_provenance.py`](../../src/viz/implied_lab_provenance.py) (`mvp1_decision` + mirrored `verification_summary` fields)

| Area | Status | Notes |
|------|--------|-------|
| `primary_output_state` / reason | **matched** | Compact + verification via `_render_mvp1_decision_digest` |
| `data_quality`, `classification_label`, `expression_family` | **matched** | Same three-column layout |
| `materiality` (M_ratio caption) | **fixed** | Was verification-only; compact now uses `format_mvp1_materiality_caption` |
| `verification_summary` mirror fields | **matched** | Set from `build_mvp1_decision_surface` in provenance (no drift) |
| `mvp1_benchmark_substrate` | **defer** | Recovery-only per reconcile |
| Blind `app.py` merge | **defer** | — |

**Tests added:** [`tests/test_mvp1_panel_parity.py`](../../tests/test_mvp1_panel_parity.py)

**Risk register:** [`PPE_RISK_REGISTER.md`](PPE_RISK_REGISTER.md)

---

## Product-Slice003 smoke witness

| Run ID | Scenario | Exit | elapsed_s |
|--------|----------|------|-----------|
| 20260519_144000 | MVP1_compact_verification | 0 | 138.6 |
| 20260519_144350 | A_width_target_payoff | 0 | 99.6 |

**Dual smoke total:** ~346.3s.

---

## Product-Slice005 smoke witness

| Run ID | Scenario | Exit | elapsed_s |
|--------|----------|------|-----------|
| 20260519_150936 | MVP1_compact_verification | 0 | 141.2 |
| 20260519_151210 | A_width_target_payoff | 0 | 89.8 |

**Dual smoke total:** ~253.4s.

---

## Reconcile-Slice002

Full matrix: [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md). Directional strip **already_on_main**; no blind recovery merge.

---

## Steward parallel

- VPS CTA: [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) — pending `.env`
- Paid interest: [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — **N** until live call

---

## Next BUILD

- **SELECTION:** steward pick for next Phase 2 slice or chapter closeout (Slice005 **CLOSED**).
- **Risk register:** [`PPE_RISK_REGISTER.md`](PPE_RISK_REGISTER.md)
