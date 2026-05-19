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
- Active MVP1 focus: **none** — operator hardening **COMPLETE** 2026-05-19
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability, Phase 2 on `main`, MVP1 operator hardening
- Next pending execution step: **steward SELECTION** — `docs/SOP/POST_MVP1_OPERATOR_HARDENING_SELECTION.md`
- Steward parallel: VPS `.env` CTA **pending**; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Baseline SHA: verify `git rev-parse origin/main` after Slice006 push
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `PPE_RISK_REGISTER.md` + `POST_PHASE2_CHAPTER_SELECTION.md`
```

## Current priority

**Operator hardening COMPLETE** — trust-strip smoke gate green. Await steward **SELECTION**. Canon: [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md).

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **Steward:** SELECTION + VPS CTA + paid-interest ([`POST_MVP1_OPERATOR_HARDENING_SELECTION.md`](POST_MVP1_OPERATOR_HARDENING_SELECTION.md), [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)).
2. **Agent:** await SELECTION; no recovery blind-merge.

## Last updated

2026-05-19 — Operator hardening chapter COMPLETE (`trust_strip_mvp1_found` smoke gate).
