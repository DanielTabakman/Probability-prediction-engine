# MSOS session resume v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 12. Depends on terminal `region_bet_payoff_save_v1` (catalog order 10 / PR #5475). Catalog order 11 (`region_bet_monitor_value_v1` / PR #5478) is also terminal. This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, market-moved-since, manage/adjust, learning closeout, or a second workflow store.

## Goal

Resume the current owner's most recent valid Region Bet workflow without guessing or leaking another owner's state.

## Already Exists

- Region Bet payoff/save on main from PR #5475: confirmed paper expression, frozen entry snapshot, owner-scoped persistence.
- Guided Region Bet shell and workflow store used by earlier Region Bet chapters.
- Monitor value on main from PR #5478.

## Gap

A saved Region Bet can be persisted and monitored, but the guided flow does not yet restore the most recent valid owner-scoped Region Bet and last safe step on return.

## Exact Scope

- Resume the most recent valid Region Bet for the authenticated owner and restore its exact asset, window, region, and selected expression reference.
- Restore only a known guided-shell step; fall back to the earliest safe incomplete step when stored navigation state is invalid.
- Ignore malformed, stale, or cross-owner state and present a clean-start path without silently substituting another owner's data.
- Reuse the existing Region Bet API and workflow store rather than introducing a parallel persistence boundary.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBet.ts`
- `apps/msos-web/src/lib/regionBetGuidedShell.ts`
- `apps/msos-web/src/lib/regionBetResume.ts`
- `apps/msos-web/src/lib/msosWorkflowStore.ts`
- `apps/msos-web/src/components/RegionBetGuidedShell.tsx`
- `apps/msos-web/src/components/RegionBetResumeCard.tsx`
- `apps/msos-web/src/app/api/theses/region-bet/route.ts`
- `tests/test_msos_web_session_resume.py`

## Forbidden Paths

- Autobuilder runtime (`DanielTabakman/msos-autobuilder`).
- Cross-owner state.
- A second session or workflow store.
- Live brokerage, order placement, or financial-advice behavior.
- Market-moved-since, manage/adjust, and learning-closeout chapters.

## Deterministic Contract

Given the same owner and the same stored Region Bet, resume must restore the same asset, window, region, expression reference, and safe step. Malformed or foreign state fails closed to a clean start. Do not invent another owner's workflow.

## Acceptance Tests

- Valid resume restores asset, window, region, and selected expression reference.
- Invalid navigation state falls back to the earliest safe incomplete step.
- Malformed, stale, and cross-owner state are ignored.
- Clean-start path is available; no silent substitution.
- Paper-only copy; no execution or advice claims.

## Non-Goals

No live execution, no market-moved-since, no manage/adjust, no rewriting #5475 persistence or #5478 monitor teaching, no second store.

## Rollback

Revert only the session-resume modules, guided-shell wiring, API/store resume paths, and tests. Orders 06–11 must remain intact.
