# Options Made Simple: option horizon comparison v1

## COORDINATION STATUS

READY_TO_BUILD. Founder decision approved this as job A for the msos-autobuilder issue #50 zero-founder-return A -> B witness. Product issue: #5381. Refill remains paused. This charter does not authorize implementation, merge, deploy, feed mutation, or Autobuilder changes.

## Goal

Help a user compare a small deterministic set of listed option expiry windows for one current view. The user supplies direction, time horizon, belief, and risk constraints; this slice explains how the nearest listed expiries differ before the user chooses any expression.

## Already Exists

- Options Horizon has a single-expiry chart payload and MSOS `/options-horizon` surface.
- Horizon region workflow can save a region intent and deep-link into Strategy Lab.
- Existing forward, implied distribution, and trust/data flag primitives can be reused.

## Gap

Current main does not compare standardized horizon candidates such as about 30, 60, 90, 180, and 365 days in one deterministic educational table. It also does not explain the time-window trade-offs before expression selection.

## Exact Scope

- Calculate target buckets of about 30, 60, 90, 180, and 365 days from the current evaluation date.
- Select the nearest listed expiry for each target bucket deterministically.
- Deduplicate when multiple target buckets resolve to the same listed expiry.
- Display rows with expiry, days out, target bucket, forward, ATM IV, one-sigma move, trust/data flags, and educational time-decay language.
- Degrade honestly when quote, IV, forward, or liquidity evidence is missing, stale, or thin.
- Add one bounded presentation surface inside existing Options Horizon or Strategy Lab architecture.

## Allowed Product Paths

- `src/engine/options_horizon_comparison.py`
- `src/viz/options_horizon_comparison_boundary.py`
- `apps/msos-web/src/lib/optionsHorizonComparison.ts`
- `apps/msos-web/src/components/OptionsHorizonComparisonPanel.tsx`
- `apps/msos-web/src/components/OptionsHorizonClient.tsx`
- `tests/test_options_horizon_comparison.py`
- `tests/test_msos_web_options_horizon_comparison.py`

## Forbidden Paths

- Job B owned files.
- `DanielTabakman/msos-autobuilder`.
- Product-main write, publication, deploy, or merge authority.
- Queue/feed mutation, live job submission, refill changes, or Autobuilder implementation changes.
- Brokerage, order tickets, wallets, custody, live execution, or external paid APIs.
- Personalized financial advice, "recommended trade" wording, expected-profit ranking, or hidden discretionary models.
- USO/commodity-proxy acceptance-witness reuse.

## Deterministic Contract

The same listed expiries and evaluation timestamp must produce the same ordered comparison rows. The algorithm must use documented tie-breaks for nearest-expiry selection, deduplication, stale/missing-data flags, and row ordering.

## Acceptance Tests

- Unit tests cover bucket selection, nearest listed expiry tie-breaks, deduplication, missing/stale/thin data degradation, and deterministic row ordering.
- Boundary tests cover payload shape, limitation text, and no-advice copy.
- MSOS tests cover the bounded UI surface and ensure the table remains educational and non-executable.
- Charter regression tests prove this job ranks before job B and does not reuse completed USO work.

## Non-Goals

No expression ranking, no execution, no brokerage integration, no recommendation, no personalized suitability, no model-driven profit forecast, and no dependency on job B.

## Rollback

Revert only the new horizon comparison module, boundary, bounded UI surface, and tests. Existing Options Horizon single-expiry behavior must remain intact.
