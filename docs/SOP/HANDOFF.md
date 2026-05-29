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
- Active MVP1 focus: **none** — mvp1 steering sync evidence **COMPLETE** 2026-05-28
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability, Phase 2 on `main`, operator hardening, review enrichment, smoke regression, friends-first screen
- Next pending execution step: **steward SELECTION** — `docs/SOP/MVP1_FRONTIER.md`
- Steward parallel: VPS `.env` CTA **pending**; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Baseline SHA: verify `git rev-parse origin/main` after push
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `MVP1_MVP1_STEERING_SYNC_EVIDENCE_EVIDENCE_STATUS.md`
```

## Current priority

**MVP1 steering sync evidence COMPLETE** — dual smoke green. Await steward **SELECTION**.


## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **Relay:** closeout applied — see [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md).
2. **Steward:** SELECTION — [`MVP1_FRONTIER.md`](docs/SOP/MVP1_FRONTIER.md).


## Last updated

2026-05-28 — MVP1 steering sync evidence COMPLETE; closeout job `MVP1-Mvp1SteeringSyncEvidence-Closeout-Slice003`.
