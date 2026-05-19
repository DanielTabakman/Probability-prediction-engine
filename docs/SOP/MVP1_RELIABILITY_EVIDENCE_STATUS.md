# MVP1 Reliability — evidence status

**Chapter:** [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md) · **Baseline:** `main`

---

## Engineering gates

| Gate | Status | Notes |
|------|--------|-------|
| `python -m pytest -q` | **PASS** | **156** passed (2026-05-19, Slice002) |
| Dual smoke | **PASS** | Post-Slice002 witness below; subprocess caps + `scenario_timeout_s` in manifest |

---

## Smoke witness (authoritative post–Slice002)

| Run ID | Scenario | Exit | Classification | elapsed_s | Notes |
|--------|----------|------|----------------|-----------|-------|
| 20260519_133606 | MVP1_compact_verification | 0 | deterministic | 769.6 | Pass 1; budget 900s |
| 20260519_134906 | A_width_target_payoff | 0 | deterministic | 88.7 | Pass 2; budget 1500s |
| 20260519_131035 | MVP1_compact | 0 | deterministic | — | Pre-Slice002 (superseded for harness code) |
| 20260519_131251 | A_width_target_payoff | 0 | deterministic | — | Pre-Slice002 |

**Dual smoke total:** ~878.7s (`scripts/run_mvp1_dual_implied_lab_smoke.py`).

**Kill class:** `exit_code=4294967295` or no `scenario done` → environment/process timeout — [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md) §6.

---

## Slice status

| Slice | Status |
|-------|--------|
| Control-Slice001 | **CLOSED** |
| Smoke-Slice002 | **CLOSED** 2026-05-19 |
| Deploy-Slice003 | **OPEN** — steward VPS `.env` + browser CTA |
| Closeout-Slice004 | **OPEN** — after Slice003 |

---

## Deploy (Slice003)

[`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) — compose wired on `main`; **Research beta CTA** pending steward `.env`.
