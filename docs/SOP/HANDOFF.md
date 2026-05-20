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
- Active MVP1 focus: **MVP1 onboarding / How it works (v0)** — **CHARTERED** (SELECTION 2026-05-20); belief-input UX **COMPLETE** 2026-05-20
- Closed chapters: … friends-first screen, belief-input UX (see `MVP1_FRONTIER.md`)
- Next pending execution step: **PREFLIGHT** → **`MVP1-OnboardingHowItWorks-Control-Slice001`** — see `docs/SOP/SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md` + `docs/SOP/POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md`
- Steward parallel: VPS `.env` CTA **pending**; verify VPS @ **`47816a6`**+ after deploy; paid-interest **N**
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main` after pull)
- Baseline SHA: **`47816a6`**+ (`git rev-parse origin/main`)
- BUILD allowed: chartered chapter active; honor reconcile defer list

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `PPE_INTEGRATED_STATUS.md` + `MVP1_FRONTIER.md` + `SPRINT_MVP1_ONBOARDING_HOW_IT_WORKS.md` + `MVP1_ONBOARDING_HOW_IT_WORKS_EVIDENCE_STATUS.md`
```

## Current priority

**`main` @ `47816a6`** — **SELECTION COMPLETE:** MVP1 **onboarding / How it works** chartered ([`POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md`](POST_MVP1_BELIEF_INPUT_SELECTION_OUTCOME.md)). **Next:** PREFLIGHT → `MVP1-OnboardingHowItWorks-Control-Slice001`.

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION

## Recommended next step

1. **One-time Cursor:** paste [`.cursor/USER_RULES_GIT_SNIPPET.md`](../../.cursor/USER_RULES_GIT_SNIPPET.md) into **Cursor Settings → Rules → User rules** (see snippet file for exact navigation).
2. **Steward:** VPS `.env` CTA + browser verify → [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md); confirm `git rev-parse HEAD` ≥ `47816a6`.
3. **Optional:** §15F friends-first spot-check — template in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
4. **Local:** if you had WIP, `git stash list` — e.g. `stash@{0}: local wip unrelated` — apply when ready.

## Last updated

2026-05-20 — Post–belief-input **SELECTION** complete; MVP1 onboarding / How it works chartered; handoff synced.
