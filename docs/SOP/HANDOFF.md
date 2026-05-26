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
- Active MVP1 focus: **MVP1 disagreement / candidate strip polish (v0)** — **IN PROGRESS**; Control-Slice001 **CLOSED** 2026-05-26; onboarding / How it works **COMPLETE** 2026-05-20
- Closed chapters: … friends-first screen, belief-input UX, onboarding / How it works (see `MVP1_FRONTIER.md`)
- Next pending execution step: **`MVP1-DisagreementStrip-Product-Slice002`** (PRODUCT) — see `docs/SOP/SPRINT_MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH.md` + `docs/SOP/MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`
- Steward parallel: VPS `.env` CTA **pending**; verify VPS after pull of closeout merge; paid-interest **N**
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main` after pull)
- Baseline SHA: verify `git rev-parse origin/main` after merge of onboarding closeout slice
- BUILD allowed: only after steward SELECTION; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `POST_MVP1_ONBOARDING_DISAGREEMENT_SELECTION_OUTCOME.md` + `MVP1_DISAGREEMENT_CANDIDATE_STRIP_POLISH_EVIDENCE_STATUS.md`
```

## Current priority

**`origin/main`** (after merge) — MVP1 **disagreement / candidate strip polish**: **Control-Slice001** closed 2026-05-26. **Next:** `MVP1-DisagreementStrip-Product-Slice002` (strip polish).

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **Next BUILD chapter (agents):** SELECTION → set [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) to `READY` → operator runs **`run_ppe.cmd`** only ([`ACTIVE_PHASE_MANIFEST.md`](ACTIVE_PHASE_MANIFEST.md)).
2. **Steward parallel (human/VPS):** `.env` CTA + browser verify → [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md); paid-interest per [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
3. **Optional:** §15F friends-first spot-check — template in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

## Last updated

2026-05-26 — `MVP1-DisagreementStrip-Control-Slice001` closed (charter witness); **next** Product-Slice002; handoff synced.
