# Region Bet monitor value v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 11. Depends on terminal `region_bet_payoff_save_v1` (catalog order 10 / PR #5475). This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, manage/adjust, learning closeout, or rewriting payoff/save persistence.

## Goal

Teach the difference between the underlying view being right and the selected paper expression making money, using honest then-versus-now observations on Monitor.

## Already Exists

- Region Bet payoff/save on main from PR #5475: confirmed paper expression, frozen entry snapshot, owner-scoped persistence.
- Existing Monitor feed and Monitor/History surfaces.

## Gap

A saved Region Bet can be monitored, but Monitor does not yet separate underlying then/now from paper-expression then/now, or label observation quality (observed, estimated, stale, unavailable).

## Exact Scope

- Show entry and current underlying observations separately from entry and current paper-expression values.
- Label every value with its observation time and distinguish observed, estimated, stale, and unavailable data.
- Explain deterministic value drivers in plain language without claiming causality or recommending an action.
- Reuse the existing Monitor feed and owner-scoped Region Bet record rather than creating a second store.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBet.ts`
- `apps/msos-web/src/lib/regionBetMonitor.ts`
- `apps/msos-web/src/lib/monitorHistoryFeed.ts`
- `apps/msos-web/src/components/RegionBetMonitorCard.tsx`
- `apps/msos-web/src/components/MonitorContent.tsx`
- `apps/msos-web/src/app/api/monitor/feed/route.ts`
- `tests/test_msos_web_region_bet_monitor_value.py`

## Forbidden Paths

- Autobuilder runtime (`DanielTabakman/msos-autobuilder`).
- Fabricated live marks or timestamps.
- Live brokerage, order placement, or financial-advice behavior.
- Cross-owner workflow state.
- Manage/adjust and learning-closeout chapters.

## Deterministic Contract

Given the same frozen entry snapshot and the same later observation, then/now labels and value drivers must be identical. Missing or stale expression value fails closed. Do not invent broker marks or advice.

## Acceptance Tests

- Entry vs current underlying is shown separately from entry vs current paper-expression value.
- Every value has an observation time and a quality label.
- Stale and missing expression values are labeled; nothing is fabricated.
- Tests cover mapping, labels, timestamps, stale input, and missing expression value.
- Paper-only copy; no execution or advice claims.

## Non-Goals

No live execution, no manage/adjust, no rewriting #5475 payoff/save persistence, no second store.

## Rollback

Revert only the monitor-value modules, Monitor wiring, feed mapping for this chapter, and tests. Orders 06–10 must remain intact.
