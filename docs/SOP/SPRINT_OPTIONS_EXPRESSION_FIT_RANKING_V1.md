# Options Made Simple: best-fit expression ranking v1

## COORDINATION STATUS

READY_TO_BUILD. Founder decision approved this as job B for the msos-autobuilder issue #50 zero-founder-return A -> B witness. Product issue: #5382. It is product-sequenced after job A but technically independent from job A. No technical prerequisite on `options_horizon_comparison_v1` exists for this job. Refill remains paused. This charter does not authorize implementation, merge, deploy, feed mutation, or Autobuilder changes.

## Goal

Rank existing current-main options exposure or strategy candidates against a user's direction, belief, target horizon, maximum loss, and payoff preference, then explain why the top fit is most aligned for education only.

## Already Exists

- Exposure Menu has deterministic current-main exposure path primitives and horizon chips.
- Strategy Lab has a paper-only suggested structure boundary for a selected expiry.
- MSOS expression planning already presents educational, non-executable option strategy context.

## Gap

Current main does not rank available horizon/expression candidates against user constraints, explain why alternatives score lower, or surface a deterministic top-fit explanation with limitations.

## Exact Scope

- Consume existing current-main exposure-menu, strategy-suggestion, and horizon-chip/equivalent primitives.
- Score candidates using direction/belief fit, target-horizon fit, max-loss compatibility, payoff preference, and data/trust limitations.
- Produce stable scores, deterministic ordering, top-fit explanation, why alternatives rank lower, and limitation text.
- Keep the result paper-only and educational.

## Allowed Product Paths

- `src/engine/options_expression_fit_ranking.py`
- `src/viz/options_expression_fit_ranking_boundary.py`
- `scripts/rank_options_expression_fit.py`
- `apps/msos-web/src/lib/optionsExpressionFitRanking.ts`
- `apps/msos-web/src/components/OptionsExpressionFitRankingPanel.tsx`
- `apps/msos-web/src/components/ExpressionPlanningPanel.tsx`
- `tests/test_options_expression_fit_ranking.py`
- `tests/test_msos_web_options_expression_fit_ranking.py`

## Forbidden Paths

- Job A owned files.
- Imports from `options_horizon_comparison` or any job A schema/module.
- Assumptions that job A has merged.
- Manual merge, rebase, registry mutation, or founder command between job A and job B.
- `DanielTabakman/msos-autobuilder`.
- Product-main write, publication, deploy, or merge authority.
- Queue/feed mutation, live job submission, refill changes, or Autobuilder implementation changes.
- Brokerage, order tickets, wallets, custody, live execution, or external paid APIs.
- Personalized financial advice, "recommended trade" wording, expected-profit ranking, or hidden discretionary models.
- USO/commodity-proxy acceptance-witness reuse.

## Deterministic Contract

The same current-main candidate set and user constraints must produce the same scores, order, top-fit explanation, lower-ranked explanations, and limitation text. All weights and tie-breaks must be explicit and tested.

## Acceptance Tests

- Unit tests cover score components, deterministic ordering, tie-breaks, max-loss compatibility, payoff preference handling, and limitation propagation.
- Boundary tests prove the payload consumes current-main exposure/strategy primitives without importing job A.
- MSOS tests cover the bounded ranking surface and no-advice copy.
- Charter regression tests prove job B stays dispatchable when job A is unmerged and that the writable paths are disjoint.

## Non-Goals

No horizon comparison implementation, no execution, no brokerage integration, no personalized suitability, no expected-profit optimization, no paid data dependency, and no technical prerequisite on `options_horizon_comparison_v1`.

## Rollback

Revert only the ranking module, boundary, CLI helper, bounded UI surface, and tests. Existing Exposure Menu and Strategy Lab behavior must remain intact.
