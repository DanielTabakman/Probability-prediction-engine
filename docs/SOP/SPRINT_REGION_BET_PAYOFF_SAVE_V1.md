# Region Bet payoff and save v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 10. Depends on terminal `region_bet_risk_expression_bridge_v1` (catalog order 9 / PR #5463). This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, monitor teaching, manage/adjust, or rewriting expression-fit math.

## Goal

Explain the selected paper expression with deterministic payoff/scenario copy, require explicit confirmation, and persist an owner-scoped monitorable Region Bet whose entry snapshot is frozen at confirmation.

## Already Exists

- Region Bet guided shell (catalog order 7 / PR #5441) and market-compare bridge (order 8 / PR #5444).
- Risk-to-expression bridge on main from PR #5463: selected expression reference plus stated risk constraints on the Region Bet draft.
- Owner-scoped Region Bet API and workflow store used by earlier Region Bet chapters.

## Gap

The guided flow can choose a paper expression. It does not yet show payoff/scenario explanation, require confirmation, or persist a monitorable Region Bet with an immutable entry snapshot.

## Exact Scope

- Render deterministic payoff and scenario explanations for the selected paper expression.
- Require explicit confirmation before changing a Region Bet from draft to an active monitorable paper object.
- Freeze the entry spot, market observation time, stated constraints, selected region, and selected expression reference at confirmation.
- Persist through the existing owner-scoped Region Bet API and workflow store with no broker or order-ticket behavior.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBet.ts`
- `apps/msos-web/src/lib/regionBetGuidedShell.ts`
- `apps/msos-web/src/lib/regionBetPayoff.ts`
- `apps/msos-web/src/lib/msosWorkflowStore.ts`
- `apps/msos-web/src/components/RegionBetGuidedShell.tsx`
- `apps/msos-web/src/components/RegionBetGuidedShellPanel.tsx`
- `apps/msos-web/src/components/RegionBetPayoffSavePanel.tsx`
- `apps/msos-web/src/app/api/theses/region-bet/route.ts`
- `tests/test_msos_web_region_bet_payoff_save.py`

## Forbidden Paths

- Autobuilder runtime (`DanielTabakman/msos-autobuilder`).
- Live brokerage, order placement, or financial-advice behavior.
- Mutable entry snapshots after confirmation.
- Cross-owner workflow state.
- Monitor teaching, manage/adjust, and learning-closeout chapters.

## Deterministic Contract

Given the same selected expression, stated constraints, and market observation, payoff/scenario copy and the frozen snapshot must be identical. Reject malformed input. Do not invent broker tickets or advice.

## Acceptance Tests

- Payoff mapping is deterministic for a fixed selected expression.
- Confirmation is required before draft → active monitorable persistence.
- Frozen snapshot includes entry spot, observation time, constraints, selected region, and selected expression reference.
- Restore reads the same frozen snapshot; malformed input is rejected.
- Paper-only copy; no execution or advice claims.

## Non-Goals

No live execution, no monitor teaching, no manage/adjust, no rewriting #5454 expression-fit math, no rebuild of #5463.

## Rollback

Revert only the payoff/save modules, guided-shell wiring, API/store persistence for this chapter, and tests. Orders 06–09 must remain intact.
