# MVP1 guided demo path v1 — SELECTION (pending)

**Chapter:** `mvp1_guided_demo_path_v1`  
**Priority:** **MEDIUM** · **P2 lab legibility** (founder-operator demo friction)  
**Sprint:** [`SPRINT_MVP1_GUIDED_DEMO_PATH_V1.md`](SPRINT_MVP1_GUIDED_DEMO_PATH_V1.md)  
**Relay plan:** [`PHASE_PLANS/mvp1_guided_demo_path_v1_relay.json`](PHASE_PLANS/mvp1_guided_demo_path_v1_relay.json)

## Status

**CHARTERED** — backlog row inserted **after** `mvp1_bl_density_smoothing_v1` via `queueAfterPlanPath`.

## Intent

Screen-share / guided-demo mode on the Streamlit implied lab: collapse reference noise, surface founder crib copy, optional auto Deribit refresh — so the operator can run [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md) without sidebar scroll hunting.

**Operator crib:** [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md)

## Run order (medium queue)

1. `mvp1_distribution_quant_research_v2` — **COMPLETE**
2. `mvp1_bl_density_smoothing_v1` — next READY (slot 1)
3. **`mvp1_guided_demo_path_v1`** — PLANNED after B–L closeout
4. `mvp1_cross_venue_prob_panel` → scan → backtest

## Urgent bump (steward only)

If **`sessions_logged < 3`** in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) **and** solo rehearsal per [`FOUNDER_OPERATOR_CRIB_SHEET_V1.md`](FOUNDER_OPERATOR_CRIB_SHEET_V1.md) still fails after B–L ships:

- Set backlog `urgent: true` with `urgentReason`: `founder solo demo blocked — prioritize guided path before cross-venue`
- Bypasses [`ppe_focus_gate.py`](../../scripts/ppe_focus_gate.py) validation-report gate per playbook

Do **not** mark urgent if the blocker is outreach (no contacts) rather than UI friction.

## First slice at SELECTION

`MVP1-GuidedDemo-Control-Slice001`
