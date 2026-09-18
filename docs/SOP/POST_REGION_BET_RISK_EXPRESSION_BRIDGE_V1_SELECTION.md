# Post-selection record: Region Bet risk-to-expression bridge v1

## COORDINATION STATUS

SELECTED as Autobuilder catalog order **9**, immediately after terminal `region_bet_market_compare_bridge_v1` (catalog order 8 / PR #5444) and merged Options Made Simple job B (`options_expression_fit_ranking_v1` / PR #5454).

## Selection Evidence

- Founder-approved product intent backlog: Autobuilder intent order 09.
- **Reuse decision:** [#5454](https://github.com/DanielTabakman/Probability-prediction-engine/pull/5454) shipped expression-fit ranking on `main` (`0e04b102`). This chapter bridges those primitives into the guided Region Bet flow. Do not rebuild or merge stale draft [#5428](https://github.com/DanielTabakman/Probability-prediction-engine/pull/5428).
- Catalog orders 06–08 are terminal on `main`.

## Scope Boundary

This selection authorizes only the risk-to-expression bridge listed in `docs/SOP/PHASE_PLANS/region_bet_risk_expression_bridge_v1_relay.json`. It does not authorize payoff/save, monitor teaching, manage/adjust, live execution, or rewriting expression-fit math.

## Order

Catalog order 9 follows order 8 and is now terminal on `main` (PR #5463). Item 10 is the next JIT packet. Items 11–17 stay intent-only until 10 is terminal.
