# HANDOFF

Purpose: minimum context needed for the next work session.

## HANDOFF GATE (fill this block; no interpretation)

Copy/paste and fill every field. Do not infer from memory; verify in repo/docs.

```text
HANDOFF GATE — v3.1 (MVP1 control-plane)

A) DOC-STATE SAFETY (alignment)
- Source-of-truth precedence: pushed repo+accepted docs > PPE_MASTER_MVP1 > MVP1_FRONTIER / MSOS_FRONTIER > HANDOFF > OPERATING_RULES
- Controlling master canon: `docs/VISION/PPE_MASTER_MVP1.md`
- Live frontier (MSOS): `docs/SOP/MSOS_FRONTIER.md`
- Live frontier (MVP1 engine): `docs/SOP/MVP1_FRONTIER.md` — idle
- Integrated one-pager: `docs/SOP/PPE_INTEGRATED_STATUS.md`
- Active MSOS focus: **MSOS P1 stack routing** — ADR at `docs/SOP/MSOS_P1_STACK_ROUTING_ADR.md`; relay closeout pending
- Steward parallel: VPS `.env` CTA **pending**; paid-interest **N** until live call; storyboard v0.6 **not in-repo** (blocks P2)
- Reporting posture: SLIM MODE / REPO-SENSOR execution-only
- Drift rule: **`MSOS_FRONTIER.md`** outranks HANDOFF for MSOS queue

B) REPO-STATE SAFETY (reproducibility)
- Branch: verify (`git rev-parse --abbrev-ref HEAD`)
- Baseline SHA: verify `git rev-parse origin/main` after push
- BUILD allowed: MSOS P1 relay after IDE product marker + `run_ppe_local.cmd`

C) AGENT CONTINUITY (required)
- Safe to switch agents: YES after push
- Carry: `MSOS_P1_STACK_ROUTING_ADR.md` + `MSOS_FRONTIER.md` + `PPE_INTEGRATED_STATUS.md`
```

## Current priority

**MSOS P1** — stack/routing ADR committed. Operator: **`mark_ide_product_ready.cmd MSOS-P1-Product-Slice002`** then **`run_ppe_local.cmd`**.

## Hard rule reminders

- Dual smoke: `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py`
- Do not blind-merge `recovery/frontier-steward-v2_1-baseline`
- Do not port `mvp1_benchmark_substrate.py` without steward SELECTION
- MSOS P2 UI blocked until [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied

## Recommended next step

1. **Relay:** `mark_ide_product_ready.cmd MSOS-P1-Product-Slice002` → `run_ppe_local.cmd`
2. **Operator:** drop storyboard v0.6 into `docs/VISION/MSOS/storyboard-v0.6/` when ready for P2
3. **Steward:** VPS CTA `.env` per [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)

## Last updated

2026-06-01 — MSOS P1 ADR accepted; relay closeout pending.
