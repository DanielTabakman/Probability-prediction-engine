# Region Bet market-compare bridge v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 8. **Reuse decision:** [#5427](https://github.com/DanielTabakman/Probability-prediction-engine/pull/5427) is already on main (`f7229e831`) as the comparison primitive. Do not supersede it. This chapter only bridges that primitive into the Region Bet guided shell. It does not authorize rewriting comparison math, merging or recreating [#5428](https://github.com/DanielTabakman/Probability-prediction-engine/pull/5428), Autobuilder runtime mutation, refill intervention, or live execution.

## Goal

Add a guided-flow **compare** step that shows the current Region Bet (asset, expiry/window, selected region) against the existing Options Horizon comparison table — same buckets, nearest-listed-expiry tie-breaks, and educational non-advice copy. The user should see how their region sits next to nearby listed windows without leaving the guided shell.

## Already Exists

- Region Bet guided shell (catalog order 7 / PR #5441) with steps asset → window → region → review.
- Options Horizon comparison primitive on main from PR #5427: `options_horizon_comparison.py`, `optionsHorizonComparison.ts`, `OptionsHorizonComparisonPanel`.
- Region Bet contract persistence (order 6 / PR #5436).

## Gap

Comparison exists as a standalone Options Horizon surface. The guided Region Bet flow does not yet present that table in-context using the draft's retained asset / window / region.

## Exact Scope

- Add a guided-shell compare step (or equivalent in-flow panel) after region and before review.
- Adapter/bridge that maps Region Bet snapshot fields into the existing comparison input shape and renders the existing educational table.
- Preserve guided-shell retain behavior: forward/back still keeps asset, expiry/window, and selected region.
- Paper/simulation only; reuse #5427 degradation (missing/stale/thin data fail closed / degrade honestly).

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBetMarketCompare.ts`
- `apps/msos-web/src/components/RegionBetMarketComparePanel.tsx`
- `apps/msos-web/src/lib/regionBetGuidedShell.ts` (add compare step / wire only)
- `apps/msos-web/src/components/RegionBetGuidedShell.tsx`
- `apps/msos-web/src/components/RegionBetGuidedShellPanel.tsx`
- `tests/test_msos_web_region_bet_market_compare.py`

Import/call `optionsHorizonComparison.ts` and embed `OptionsHorizonComparisonPanel` from the new bridge files. Do **not** add those #5427 files to the Autobuilder touch set.

## Forbidden Paths

- `src/engine/options_horizon_comparison.py` and `src/viz/options_horizon_comparison_boundary.py` — already landed by #5427; do not rewrite.
- Recreating a second standalone Options Horizon comparison product surface.
- Expression fit / risk-expression bridge (`region_bet_risk_expression_bridge_v1`) and recreation of PR #5428 surfaces.
- Payoff/save, monitor teaching, manage/adjust, learning closeout, session-resume chapters.
- Live brokerage, order tickets, wallets, custody, personalized advice, or recommended-trade wording.
- Autobuilder source redesign, jobs feed mutation beyond this charter, or Options Horizon live archive inspection.

## Deterministic Contract

Given the same Region Bet snapshot and the same listed-expiry / evaluation inputs, the compare step must show the same ordered #5427 comparison rows. Mapping from Region Bet fields to comparison inputs is pure and documented. Invalid or incomplete drafts do not invent rows.

## Acceptance Tests

- Guided shell exposes a compare step; asset / expiry-window / selected region survive navigation through it.
- Bridge calls existing `optionsHorizonComparison` helpers — tests fail if bucket/tie-break logic is reimplemented in Region Bet modules.
- Educational / non-executable copy is preserved (no advice, no expected-profit ranking).
- Charter regression: no dependency on implementing #5428 product surfaces.

## Non-Goals

No new comparison math, no expression ranking, no monitor teaching, no live execution, no merge of #5428.

## Rollback

Revert only the bridge modules, guided-shell compare-step wiring, and tests. #5427 comparison primitives and order-7 guided shell must remain intact.
