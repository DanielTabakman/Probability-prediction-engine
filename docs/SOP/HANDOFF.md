# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v3.1 (MVP1 control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > PPE_MASTER_MVP1 > MVP1_FRONTIER > HANDOFF > OPERATING_RULES
- Controlling master canon: `docs/VISION/PPE_MASTER_MVP1.md`
- Live frontier (only steering truth): `docs/SOP/MVP1_FRONTIER.md`
- Integrated one-pager: `docs/SOP/PPE_INTEGRATED_STATUS.md`
- Active MVP1 focus: **Phase 2 on `main`** — [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md)
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability — **COMPLETE** 2026-05-19
- Phase 2 progress: Slices001–004 **CLOSED**; Sprint004 strip **already_on_main**
- Next pending execution step: `MVP1-Phase2-Product-Slice005` — [`SPRINT_MVP1_PHASE2_SLICE005.md`](SPRINT_MVP1_PHASE2_SLICE005.md)
- SELECTION: [`POST_PHASE2_PRODUCT_SLICE003_SELECTION.md`](POST_PHASE2_PRODUCT_SLICE003_SELECTION.md)
- Steward parallel: VPS `.env` CTA PASS; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Baseline SHA: `566f4f0`+ (verify `git rev-parse origin/main`)
- BUILD allowed: YES — bounded PRODUCT per Slice005 spec + reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `PHASE2_RECONCILE_REPORT.md` + `MVP1_PHASE2_EVIDENCE_STATUS.md`
```

## Current priority

**Phase 2 on `main`** — Product-Slice003 **shipped** (copy/harness only; directional strip already on `main`). **Next:** Product-Slice005 parity audit. Canon: [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md).

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **BUILD:** `MVP1-Phase2-Product-Slice005` per [`SPRINT_MVP1_PHASE2_SLICE005.md`](SPRINT_MVP1_PHASE2_SLICE005.md).
2. **Steward:** VPS CTA + paid-interest ([`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md), [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)).

## Last updated

2026-05-19 — integrated status + Slice005 SELECTION chartered.
