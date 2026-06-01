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
- Active MVP1 focus: **none** — mvp1 phase 6 trust metrics v1 **COMPLETE** 2026-06-01
- MSOS track: **MSOS P1 stack routing ADR COMPLETE** 2026-06-01; P2 blocked until storyboard v0.6 in-repo
- Closed chapters: Validation, Commercial Validation, MVP1 Reliability, Phase 2 on `main`, operator hardening, review enrichment, smoke regression, friends-first screen
- Next pending execution step: **steward SELECTION** — `docs/SOP/MSOS_FRONTIER.md` (P2 blocked)
- Steward parallel: VPS `.env` CTA **pending**; paid-interest **N** until live call
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Baseline SHA: verify `git rev-parse origin/main` after push
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `MSOS_P1_STACK_ROUTING_ADR.md` + `MSOS_P1_STACK_ROUTING_EVIDENCE_STATUS.md`
```

## Current priority

**MSOS P1 stack routing ADR COMPLETE** — MVP1 Phase 6 trust metrics v1 COMPLETE. Await steward **SELECTION** for MSOS P2 (blocked until storyboard).

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION
- MSOS P2 UI blocked until [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied

## Recommended next step

1. **Relay:** closeout applied — see [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md).
2. **Steward:** import storyboard v0.6, then SELECTION — [`MSOS_FRONTIER.md`](docs/SOP/MSOS_FRONTIER.md).

## Last updated

2026-06-01 — MSOS P1 stack routing ADR COMPLETE; closeout job `MSOS-P1-Closeout-Slice004`. MVP1 Phase 6 trust metrics v1 COMPLETE (PR #73).
