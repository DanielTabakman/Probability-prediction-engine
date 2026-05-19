# PPE risk register

**As-of:** 2026-05-19 · **Baseline:** `main` @ `6ba9ec1`+ (product tip `01c89cf`) · **Audit:** Phase 1 worry pass before Slice005 BUILD

Severity: **high** / **medium** / **low**. Status: **open** / **mitigated** / **accepted** / **steward**

---

## Summary

| Severity | Count | Agent-fixed this pass | Steward / accepted |
|----------|-------|----------------------|-------------------|
| High | 0 | — | — |
| Medium | 3 | 2 | 1 |
| Low | 4 | 1 | 3 |

**Slice005:** **not blocked** — no open high risks.

---

## 1. Production — deploy witness CTA pending

| Field | Value |
|-------|--------|
| **Severity** | **medium** |
| **Status** | **steward** |
| **Finding** | Demo **not broken**. `marketstructureos.com` loads (witness PASS 2026-05-19). Research-offer CTA renders only when `PPE_RESEARCH_OFFER_URL` + `PPE_RESEARCH_OFFER_LABEL` are set on VPS (`src/viz/app.py` → `research_offer_cta`). Without `.env`, operators see demo + **Get full access** (when private URL configured) but **no** Research beta banner. |
| **Action** | Steward: VPS `.env` → `docker compose up -d --build` → mark CTA **PASS** in [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md). **Do not** fake PASS without browser evidence. |

---

## 2. Smoke — MVP1 compact ~770s vs ~139s recent

| Field | Value |
|-------|--------|
| **Severity** | **low** |
| **Status** | **accepted** (monitored) |
| **Finding** | Recent green runs: MVP1_compact **138.6s** (`20260519_144000`). ~770s class matches **pre–Reliability-Slice002** wall-clock or **environment kill / hung** scenarios (see [`IMPLIED_LAB_OPERATOR_RUNBOOK.md`](IMPLIED_LAB_OPERATOR_RUNBOOK.md) §6), not current harness defaults. Per-scenario caps on `main`: `MVP1_compact_verification` **900s**, `A_width_target_payoff` **1500s** (`scripts/implied_lab_ui_smoke_harness.py` → `SCENARIO_TIMEOUT_S_BY_SCENARIO`); dual-smoke parent adds **+120s** subprocess grace. |
| **Action** | No harness change this pass. Re-classify **medium** if two consecutive post-cap runs exceed budget without kill exit. |

---

## 3. Test gaps — `test_mvp1_benchmark_substrate` vs `mvp1_decision_surface`

| Field | Value |
|-------|--------|
| **Severity** | **low** |
| **Status** | **accepted** (defer per reconcile) |
| **Finding** | `tests/test_mvp1_benchmark_substrate.py` and `mvp1_benchmark_substrate.py` are **recovery-only** and intentionally absent on `main`. Coverage for decision logic: [`tests/test_mvp1_decision_surface.py`](../../tests/test_mvp1_decision_surface.py), [`tests/test_mvp1_verification_integration.py`](../../tests/test_mvp1_verification_integration.py). Slice005 adds [`tests/test_mvp1_panel_parity.py`](../../tests/test_mvp1_panel_parity.py) for panel copy parity. |
| **Action** | Do not port substrate tests without steward SELECTION ([`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md)). |

---

## 4. Branch / doc drift — HANDOFF vs frontier vs integrated status

| Field | Value |
|-------|--------|
| **Severity** | **medium** |
| **Status** | **mitigated** |
| **Finding** | Local checkout may show branch `build/commercial-validation-v0` while `HEAD` == `origin/main` (`6ba9ec1`). `main` worktree locked at `_worktrees/orchestrator/orch-smoke-09f3`. Doc baseline refs mixed `566f4f0` vs `6ba9ec1` (docs-only witness commits after product `01c89cf`). Steering docs (HANDOFF, MVP1_FRONTIER, PPE_INTEGRATED_STATUS) aligned on Slice005 **NEXT**. |
| **Action** | Agent: verify `git rev-parse HEAD` == `origin/main` before push; update witness SHAs on closeout. Steward: use `main` worktree or `git pull` on VPS. |

---

## 5. Phase 2 defer traps — accidental recovery merge

| Field | Value |
|-------|--------|
| **Severity** | **medium** |
| **Status** | **mitigated** (process) |
| **Finding** | [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md) explicitly **defers** `mvp1_benchmark_substrate.py`, blind `app.py` merge, and recovery harness semantics. Directional strip **already_on_main**. |
| **Action** | BUILD agents: cherry-pick only; no `git merge recovery/...` without new reconcile + SELECTION. |

---

## 6. Engineering gate — pytest

| Field | Value |
|-------|--------|
| **Severity** | — |
| **Status** | **PASS** |
| **Finding** | `python -m pytest -q` → **157** passed @ `6ba9ec1` (pre–Slice005); **159** after Slice005 panel test (verify on closeout). |
| **Action** | Re-run after each product touch. |

---

## 7. Repo hygiene — clean tree

| Field | Value |
|-------|--------|
| **Severity** | **low** |
| **Status** | **PASS** (pre-edit) |
| **Finding** | Working tree clean at audit start; post–Slice005 commits expected. |
| **Action** | — |

---

## 8. Paid-interest outreach

| Field | Value |
|-------|--------|
| **Severity** | **medium** |
| **Status** | **steward** |
| **Finding** | Honest **N** until live conversation ([`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md)). |
| **Action** | Steward script in [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md). **Do not** log **Y** without evidence. |

---

## Changelog

| Date | Event |
|------|--------|
| 2026-05-19 | Initial register; Phase 1 audit; Slice005 BUILD cleared |
