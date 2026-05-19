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
- Active MVP1 focus: **Post-ops SELECTION** — [`POST_COMMERCIAL_OPS_SELECTION.md`](POST_COMMERCIAL_OPS_SELECTION.md)
- Closed chapters: Validation + Commercial Validation — **COMPLETE** 2026-05-19
- Ops agent lane: **DONE** — smoke `20260519_131035` / `131251`; pytest **153**; see [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)
- Current execution focus: steward VPS + `PPE_RESEARCH_OFFER_*` + live paid-interest call
- Next pending execution step: **SELECTION** for next BUILD chapter (after steward outreach optional)
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MVP1_FRONTIER.md`** outranks HANDOFF if they drift
- Legacy `CURRENT_FRONTIER.md` is **historical only**

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`; expect `main`)
- Ahead/behind vs origin: verify
- Working tree: verify CLEAN before BUILD
- Untracked canonical docs: verify NO
- BUILD allowed: NO during ops pass (CONTROL/operator only)

C) AGENT CONTINUITY (required)
- Safe to switch agents: verify after repo-state
- If YES: branch + HEAD SHA + `MVP1_FRONTIER.md` + `COMMERCIAL_OPS_COMPLETION.md`
```

**Steward workflow:** [FRONTIER_STEWARD_PROTOCOL.md](FRONTIER_STEWARD_PROTOCOL.md). **Ops tracker:** [COMMERCIAL_OPS_COMPLETION.md](COMMERCIAL_OPS_COMPLETION.md). **Implied lab:** [IMPLIED_LAB_OPERATOR_RUNBOOK.md](IMPLIED_LAB_OPERATOR_RUNBOOK.md).

## Current priority

**Ops completion** — deploy, smoke evidence, live paid-interest. Chapters Validation + Commercial Validation are **closed** on `main`.

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
