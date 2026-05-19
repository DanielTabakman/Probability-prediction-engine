# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v3.0 (MVP1 control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > PPE_MASTER_MVP1 > MVP1_FRONTIER > HANDOFF > OPERATING_RULES
- Controlling master canon: `docs/VISION/PPE_MASTER_MVP1.md`
- Live frontier (only steering truth): `docs/SOP/MVP1_FRONTIER.md`
- Active MVP1 focus: **Phase 2 on `main`** — [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md)
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability — **COMPLETE** 2026-05-19
- Phase 2 progress: Reconcile + Product-Slice003 **CLOSED**; Closeout-Slice004 **CLOSED** (checkpoint)
- Next pending execution step: steward **expand PRODUCT scope** or next slice from [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md) defer list
- Steward parallel: VPS `.env` CTA PASS; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- BUILD allowed: YES — bounded PRODUCT slices per reconcile report

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `MVP1_FRONTIER.md` + `PHASE2_RECONCILE_REPORT.md` + `MVP1_PHASE2_EVIDENCE_STATUS.md`
```

## Current priority

**Phase 2 on `main`** — first PRODUCT port (**MVP1 UI exclusions alignment**) **shipped**. Reconcile: [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md). **pytest 157** passed.

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`

## Recommended next step

1. Steward: VPS CTA + paid-interest ([`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md), [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md)).
2. Optional next BUILD: defer items in reconcile report only with steward SELECTION.

## Last updated

2026-05-19 — Phase2 Reconcile-Slice002 + Product-Slice003 closed.
