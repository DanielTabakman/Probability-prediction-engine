# Region Bet risk-to-expression bridge v1 — evidence status

## Status

CONTROL charter complete. Product Autobuilder slice pending.

## Owns

Guided-flow bridge from Region Bet risk constraints (max-loss, premium, payoff preference) into the existing expression-fit ranking primitives (#5454).

## Does not own

Expression-fit ranking math (owned by `options_expression_fit_ranking_v1` / PR #5454), market-compare math (#5427), payoff/save, monitor teaching, manage/adjust, learning closeout, live execution, or Autobuilder runtime authority.

## Dependency

Requires terminal `region_bet_market_compare_bridge_v1` on product main (PR #5444) and merged #5454 expression-fit primitives. Satisfied.
