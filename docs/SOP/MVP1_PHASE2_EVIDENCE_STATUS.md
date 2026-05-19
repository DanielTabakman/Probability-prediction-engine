# Phase 2 on `main` — evidence status

**Chapter:** [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) · **Baseline:** `main` @ `03a6835`+

**Reconcile report:** [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md)

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **157** passed (2026-05-19, Product-Slice003) |
| Dual smoke | **PASS** | `20260519_144000` + `20260519_144350` (post–Slice003) |

---

## Slice status

| Slice | Status |
|-------|--------|
| Control-Slice001 | **CLOSED** 2026-05-19 |
| Reconcile-Slice002 | **CLOSED** 2026-05-19 |
| Product-Slice003 | **CLOSED** 2026-05-19 — MVP1 UI exclusions alignment |
| Closeout-Slice004 | **CLOSED** 2026-05-19 — checkpoint |

---

## Product-Slice003 smoke witness

| Run ID | Scenario | Exit | elapsed_s |
|--------|----------|------|-----------|
| 20260519_144000 | MVP1_compact_verification | 0 | 138.6 |
| 20260519_144350 | A_width_target_payoff | 0 | 99.6 |

**Dual smoke total:** ~346.3s.

---

## Reconcile-Slice002

Full matrix: [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md). Directional strip **already_on_main**; no blind recovery merge.

---

## Steward parallel

- VPS CTA: [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) — pending `.env`
- Paid interest: [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — **N** until live call
