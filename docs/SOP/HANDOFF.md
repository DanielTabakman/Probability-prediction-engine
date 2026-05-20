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
- Active MVP1 focus: **none** — belief-input UX **COMPLETE** 2026-05-20
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability, Phase 2 on `main`, operator hardening, review enrichment, smoke regression, friends-first screen, belief-input UX
- Next pending execution step: **steward SELECTION** — `docs/SOP/POST_MVP1_BELIEF_INPUT_SELECTION.md`
- Steward parallel: VPS `.env` CTA **pending** (verify VPS @ `542cd4c`+ after Deploy VPS); paid-interest **N**
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main` after merge)
- Baseline SHA: verify `git rev-parse origin/main` after push
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `MVP1_BELIEF_INPUT_EVIDENCE_STATUS.md`
```

## Current priority

**MVP1 belief-input UX COMPLETE** — dual smoke (`20260520_024407` + `024438`). Friends-first on `main` @ `542cd4c`. Deploy VPS run [26146010358](https://github.com/DanielTabakman/Probability-prediction-engine/actions/runs/26146010358) **success**. Await steward **SELECTION**.

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **Steward:** paste [`.cursor/USER_RULES_GIT_SNIPPET.md`](../.cursor/USER_RULES_GIT_SNIPPET.md) into Cursor user rules (one-time).
2. **Steward:** VPS `.env` CTA + browser verify → [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md).
3. **Steward:** SELECTION — [`POST_MVP1_BELIEF_INPUT_SELECTION.md`](POST_MVP1_BELIEF_INPUT_SELECTION.md).

## Last updated

2026-05-20 — belief-input UX COMPLETE; friends-first merged PR #9.
