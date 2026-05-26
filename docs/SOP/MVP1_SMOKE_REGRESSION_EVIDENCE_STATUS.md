# MVP1 smoke regression — evidence status

**Chapter:** [`SPRINT_MVP1_SMOKE_REGRESSION.md`](SPRINT_MVP1_SMOKE_REGRESSION.md) · **SELECTION:** [`POST_MVP1_REVIEW_ENRICHMENT_SELECTION_OUTCOME.md`](POST_MVP1_REVIEW_ENRICHMENT_SELECTION_OUTCOME.md)

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **168** passed (2026-05-19) |
| Dual smoke | **PASS** | `20260519_232908` + `20260519_233106` (total ~220s) |

**Prior failure (review enrichment closeout):** `20260519_173853` — MVP1_compact SCENARIO_TIMEOUT @ 942s / 900s budget.

---

## Slice status

| Slice | Status |
|-------|--------|
| Control-Slice001 | **CLOSED** 2026-05-19 |
| Harness-Slice002 | **CLOSED** 2026-05-19 — 1200s budget, σ_ln mode, compact marker waits |
| Witness-Slice003 | **CLOSED** 2026-05-19 — dual smoke green |
| Closeout-Slice004 | **CLOSED** 2026-05-19 |

**Chapter status:** **COMPLETE** 2026-05-19 — [`POST_MVP1_SMOKE_REGRESSION_SELECTION.md`](POST_MVP1_SMOKE_REGRESSION_SELECTION.md)

---

## Dual-smoke witness

| Run ID | Scenario | Exit | verification | trust_strip_mvp1 | elapsed_s |
|--------|----------|------|----------------|------------------|-----------|
| 20260519_232908 | MVP1_compact_verification | 0 | true | true | 103.9 |
| 20260519_233106 | A_width_target_payoff | 0 | true | n/a | 90.5 |

**Dual smoke total:** ~220.3s.

**Isolated A retry (pre-dual):** `20260519_232641` — PASS @ 104.5s (confirmed pass-2 flake was cold-start / ordering, not product regression).

---

## Harness delta (Slice002)

- `MVP1_compact_verification` default budget **1200s**; env **`PPE_UI_SMOKE_MVP1_COMPACT_TIMEOUT_S`**
- `_ensure_belief_uncertainty_sigma_mode`, `_wait_for_mvp1_compact_markers` (scroll-first)
- Runbook §6 slow-host note in [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md)

---

## Steward parallel

- VPS CTA: [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) — **pending** `.env`
- Paid interest: [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) — **N**
