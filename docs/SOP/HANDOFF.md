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
- SELECTION: [`POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md`](POST_MVP1_RELIABILITY_SELECTION_OUTCOME.md)
- Next pending execution step: **`MVP1-Phase2-Reconcile-Slice002`** (baseline diff vs recovery branch)
- Steward parallel: VPS `.env` CTA PASS; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift
- Legacy `CURRENT_FRONTIER.md` is **historical only**

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Ahead/behind vs origin: verify
- Working tree: verify CLEAN before BUILD
- Untracked canonical docs: verify NO
- BUILD allowed: YES — after Reconcile-Slice002 steward sign-off for Product-Slice003

C) AGENT CONTINUITY (required)
- Safe to switch agents: verify after repo-state
- If YES: branch + HEAD SHA + `MVP1_FRONTIER.md` + `MVP1_PHASE2_EVIDENCE_STATUS.md`
```

**Steward workflow:** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). **Phase 2 evidence:** [MVP1_PHASE2_EVIDENCE_STATUS.md](MVP1_PHASE2_EVIDENCE_STATUS.md). **Implied lab:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Current priority

**Phase 2 on `main`** — Reconcile-Slice002: diff `main` vs `recovery/frontier-steward-v2_1-baseline` before first PRODUCT port. Reliability chapter **closed**; dual smoke `20260519_133606` / `134906`.

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py` (~15–25 min)
- Classify live-data smoke failures per implied-lab runbook §6

## Most relevant checks

1. `python -m pytest -q`
2. `python scripts/run_mvp1_dual_implied_lab_smoke.py` (after PRODUCT slices)
3. Production §5 in [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md)

## Recommended next step

1. **Agent/steward:** complete Reconcile-Slice002 in [MVP1_PHASE2_EVIDENCE_STATUS.md](MVP1_PHASE2_EVIDENCE_STATUS.md).  
2. **Steward:** VPS `.env` + CTA — [VALIDATION_DEPLOY_WITNESS.md](VALIDATION_DEPLOY_WITNESS.md).  
3. **Steward:** paid-interest call — [VALIDATION_REALITY_CHECKS.md](VALIDATION_REALITY_CHECKS.md).

## Last updated

2026-05-19 — integrated finish-line: Reliability **COMPLETE**; Phase 2 chartered on `main`.
