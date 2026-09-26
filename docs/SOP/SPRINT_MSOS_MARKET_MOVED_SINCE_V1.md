# MSOS market moved since v1

## COORDINATION STATUS

COMPLETE for Autobuilder catalog order 13. Product is on `main` via PR #5483. Depends on terminal `msos_session_resume_v1` (catalog order 12 / PR #5480). Catalog order 11 (`region_bet_monitor_value_v1` / PR #5478) is also terminal. This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, manage/adjust, learning closeout, causal claims, or rewriting session-resume persistence. Do not re-BUILD.

## Goal

Explain what observably changed since the owner last viewed a saved Region Bet, without predicting the next move or recommending a trade.

## Already Exists

- Region Bet session resume on main from PR #5480: owner-scoped restore of the most recent valid workflow and last safe guided-flow step.
- Monitor value on main from PR #5478: honest then-versus-now underlying vs paper-expression context.
- Existing Monitor and History surfaces plus the owner-scoped Region Bet record.

## Gap

A saved Region Bet can be resumed and monitored, but Monitor and History do not yet show a deterministic last-seen versus now summary of what observably changed.

## Exact Scope

- Compare the current observation with the saved or last-seen Region Bet snapshot using deterministic calculations only.
- Show both observation times and label missing, incomparable, or stale inputs explicitly.
- Summarize observable changes without claiming causality, predicting the next move, or recommending a trade.
- Render the same normalized summary in existing Monitor and History surfaces.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBet.ts`
- `apps/msos-web/src/lib/marketMovedSince.ts`
- `apps/msos-web/src/lib/monitorHistoryFeed.ts`
- `apps/msos-web/src/components/MarketMovedSinceCard.tsx`
- `apps/msos-web/src/components/MonitorContent.tsx`
- `apps/msos-web/src/components/HistoryContent.tsx`
- `tests/test_msos_web_market_moved_since.py`

## Forbidden Paths

- Autobuilder runtime (`DanielTabakman/msos-autobuilder`).
- Causal, predictive, or recommendation claims.
- Fabricated market observations.
- Live brokerage or order placement.
- Manage/adjust and learning-closeout chapters.
- Rewriting session-resume persistence from #5480.

## Deterministic Contract

Given the same saved or last-seen snapshot and the same current observation, the summary must produce the same change mapping, timestamps, and missing/stale labels. Do not invent prices, causality, or a next move.

## Acceptance Tests

- Change mapping uses deterministic calculations only.
- Both observation times are shown.
- Missing, incomparable, and stale inputs are labeled explicitly.
- The same normalized summary renders on Monitor and History.
- Paper-only copy; no execution, prediction, or advice claims.

## Non-Goals

No live execution, no manage/adjust, no rewriting #5480 resume or #5478 monitor teaching, no causal or predictive claims.

## Rollback

Revert only the market-moved-since modules, Monitor/History wiring, and tests. Orders 06–12 must remain intact.
