# PPE risk register

**As-of:** 2026-05-19 · **Baseline:** `main` (verify `git rev-parse HEAD` before push) · **Audit:** post–smoke regression closeout; **no active BUILD chapter**

Severity: **high** / **medium** / **low**. Status: **open** / **mitigated** / **accepted** / **steward**

---

## Summary

| Severity | Count | Agent-fixed this pass | Steward / accepted |
|----------|-------|----------------------|-------------------|
| High | 0 | — | — |
| Medium | 3 | 2 | 1 |
| Low | 4 | 1 | 3 |

**Smoke regression:** **not blocked** — dual smoke green `20260519_232908` + `233106`; pytest **168**. No open high risks.

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
| **Finding** | Recent green dual smoke: MVP1_compact **~104s** + A_width **~91s** (`20260519_232908` / `233106`, total **~220s**). Historical ~770s / 942s class = slow host or pre–hardening budgets. Current cap: `MVP1_compact_verification` **1200s** (env `PPE_UI_SMOKE_MVP1_COMPACT_TIMEOUT_S`), `A_width_target_payoff` **1500s**. |
| **Action** | Re-run dual smoke before implied-lab merge if harness/app touched. Re-classify **medium** if two consecutive runs exceed budget without kill exit. |

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
| **Finding** | Local checkout may diverge from `origin/main` until push. Steering docs (HANDOFF, MVP1_FRONTIER, PPE_INTEGRATED_STATUS) aligned: smoke regression **COMPLETE**; **await steward SELECTION** only ([`POST_MVP1_SMOKE_REGRESSION_SELECTION.md`](POST_MVP1_SMOKE_REGRESSION_SELECTION.md)). |
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
| **Finding** | `python -m pytest -q` → **168** passed (review enrichment + smoke regression harness tests). |
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
