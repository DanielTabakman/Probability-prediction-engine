# Region Bet market-compare bridge v1 — evidence status

## Status

CONTROL charter complete. Product Autobuilder slice pending.

## Owns

Guided-flow bridge from a Region Bet snapshot into the existing Options Horizon comparison table (#5427 primitives).

## Does not own

Comparison bucket/tie-break math (owned by `options_horizon_comparison_v1` / PR #5427), expression/risk ranking, monitor teaching, payoff/save, manage/adjust, learning closeout, live execution, or Autobuilder runtime authority.

## Dependency

Requires terminal `region_bet_guided_shell_v1` on product main (PR #5441) and merged #5427 comparison primitives. Satisfied.
