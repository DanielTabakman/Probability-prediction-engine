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
- Active MVP1 focus: **MVP1 Reliability** — [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md); SELECTION [`POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md`](POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md)
- Closed chapters: Validation + Commercial Validation — **COMPLETE** 2026-05-19
- Ops agent lane: **DONE** — compose offer env; smoke `20260519_131035` / `131251`; pytest **153**; [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)
- Steward parallel: VPS `.env` `PPE_RESEARCH_OFFER_*` + live paid-interest call
- Next pending execution step: **`MVP1-Reliability-Deploy-Slice003`** (steward VPS `.env` + CTA); Smoke-Slice002 **CLOSED** 2026-05-19
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift
- Legacy `CURRENT_FRONTIER.md` is **historical only**

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Ahead/behind vs origin: verify
- Working tree: verify CLEAN before BUILD
- Untracked canonical docs: verify NO
- BUILD allowed: YES — MVP1 Reliability relay after CONTROL-Slice001 accept

C) AGENT CONTINUITY (required)
- Safe to switch agents: verify after repo-state
- If YES: branch + HEAD SHA + `MVP1_FRONTIER.md` + `COMMERCIAL_OPS_COMPLETION.md`
```

**Steward workflow:** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). **Ops tracker:** [COMMERCIAL_OPS_COMPLETION.md](COMMERCIAL_OPS_COMPLETION.md). **Implied lab:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Current priority

**MVP1 Reliability** — Smoke-Slice002 **closed** (dual smoke `20260519_133606` / `134906`). **Next:** steward Deploy-Slice003 (VPS `.env` + CTA). Evidence: [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md).

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py` (~15–20 min)
- Classify live-data smoke failures per implied-lab runbook §6

## Most relevant checks

1. `python -m pytest -q`
2. `python scripts/run_mvp1_dual_implied_lab_smoke.py`
3. Production §5 in [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md)

## Recommended next step

1. Steward: VPS + demo env in [COMMERCIAL_OPS_COMPLETION.md](COMMERCIAL_OPS_COMPLETION.md).  
2. **SELECTION:** [POST_COMMERCIAL_OPS_SELECTION.md](POST_COMMERCIAL_OPS_SELECTION.md).

## Last updated

2026-05-19 — ops agent lane complete; dual smoke green; SELECTION prep posted.
