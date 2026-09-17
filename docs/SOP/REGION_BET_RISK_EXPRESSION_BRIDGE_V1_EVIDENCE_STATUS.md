# Region Bet risk-to-expression bridge v1 — evidence status

## Status

CHARTERED. Product is on `main` via PR #5463. Remaining work is closeout only — do not re-BUILD product.

## COORDINATION STATUS

| Slice | Status | Evidence |
| --- | --- | --- |
| `RegionBet-RiskExpression-Control-Slice001` | COMPLETE | Founder-approved charter, queue entry, phase plan, and selection record for Autobuilder catalog order 09. |
| `RegionBet-RiskExpression-Product-Slice002` | COMPLETE | Region Bet risk-to-expression bridge shipped in #5463 (`ca8a8285`). |
| `RegionBet-RiskExpression-Closeout-Slice003` | PENDING | Awaiting closeout. |

## Owns

Guided-flow bridge from Region Bet risk constraints (max-loss, premium, payoff preference) into the existing expression-fit ranking primitives (#5454).

## Does not own

Expression-fit ranking math (owned by `options_expression_fit_ranking_v1` / PR #5454), market-compare math (#5427), payoff/save, monitor teaching, manage/adjust, learning closeout, live execution, or Autobuilder runtime authority.

## Dependency

Requires terminal `region_bet_market_compare_bridge_v1` on product main (PR #5444) and merged #5454 expression-fit primitives. Satisfied.

## Notes

Product paths stay bounded to `docs/SOP/PHASE_PLANS/region_bet_risk_expression_bridge_v1_relay.json`. This update only records that Slice002 is already on `main`.
