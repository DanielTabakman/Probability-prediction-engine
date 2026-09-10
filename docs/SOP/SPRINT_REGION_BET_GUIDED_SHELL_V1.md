# Region Bet guided shell v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 7. Founder-approved product intent backlog item `region_bet_guided_shell_v1`. Depends on terminal `region_bet_contract_v1` (catalog order 6 / PR #5436). This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, market-compare math, or expression-ranking surfaces.

## Goal

Add a guided Region Bet workflow shell/stepper that walks the user through creating and editing a Region Bet while **retaining** asset, expiry/window, and selected region across forward/back navigation. Reuse existing Strategy Lab workflow stepper patterns and the Region Bet contract persistence — do not invent a second persistence plane.

## Already Exists

- Region Bet contract (`regionBet.ts`, workflow-store `kind: "region_bet"`, API route) from catalog order 6.
- `WorkflowStepper` / Strategy Lab step href helpers.
- Options Horizon region intent (separate; do not recreate #5427/#5428 product surfaces).

## Gap

Contract persistence exists without a guided multi-step UI that keeps Region Bet context stable across steps.

## Exact Scope

- Guided shell/stepper UI for Region Bet create/edit flow.
- Forward/back must retain: asset identity, expiry/window, selected price-time region.
- Wire to existing Region Bet contract load/upsert helpers.
- Paper/simulation only; no brokerage.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBetGuidedShell.ts`
- `apps/msos-web/src/components/RegionBetGuidedShell.tsx`
- `apps/msos-web/src/components/RegionBetGuidedShellPanel.tsx`
- `apps/msos-web/src/lib/regionBet.ts` (read/extend contract helpers only; do not redesign persistence schema)
- `apps/msos-web/src/lib/msosWorkflowStore.ts` (wire only; no second store)
- `tests/test_msos_web_region_bet_guided_shell.py`

## Forbidden Paths

- Market-compare bridge (`region_bet_market_compare_bridge_v1`) and recreation of PR #5427 surfaces.
- Expression fit / risk-expression bridge (`region_bet_risk_expression_bridge_v1`) and recreation of PR #5428 surfaces.
- Monitor P/L teaching, payoff/save closeout, manage/adjust, learning closeout chapters.
- Live brokerage, order tickets, wallets, custody, or personalized financial advice.
- Autobuilder source redesign, jobs feed mutation beyond this charter, or Options Horizon live archive inspection.
- Broad Strategy Lab redesign unrelated to Region Bet guided shell.

## Deterministic Contract

Given the same Region Bet draft fields, navigating forward then back returns the same asset, expiry/window, and selected region values without loss. Invalid drafts fail closed before persistence.

## Acceptance Tests

- Guided shell renders stepper steps and preserves asset / expiry-window / selected region across forward/back.
- Persistence round-trip uses Region Bet contract helpers (no parallel schema).
- Charter regression: no dependency on implementing #5427/#5428 product surfaces in this slice.

## Non-Goals

No market-compare math, no expression ranking, no monitor teaching, no session-resume chapter, no live execution.

## Rollback

Revert only the guided-shell modules, any minimal contract/store wiring, and tests. Region Bet contract persistence from order 6 must remain intact.
