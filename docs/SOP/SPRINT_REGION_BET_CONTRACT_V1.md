# Region Bet contract v1

## COORDINATION STATUS

READY_TO_BUILD for Autobuilder catalog order 6. Founder-approved product intent backlog item `region_bet_contract_v1`. This charter does not authorize Autobuilder runtime mutation, refill intervention, live execution, or UI redesign beyond the persistence contract.

## Goal

Create one canonical persisted **Region Bet** object. The Region Bet is the durable product object; an option trade/expression is one expression of the market view.

## Already Exists

- Options Horizon region intent (`HorizonRegionIntent`) with MSOS workflow-store persistence (`kind: "horizon_region"`).
- Thesis and expression persistence boundaries.
- Strategy Lab / Monitor / History infrastructure for later bridges.

## Gap

Current main has a region *intent*, not a Region Bet contract that ties together entry snapshot, selected price-time region, target expiry/window, market-implied snapshot at creation, user risk constraints, selected expression reference, and lifecycle/status fields needed by later monitoring.

## Exact Scope

Persist a small Region Bet contract/object with:

- asset
- entry spot / entry timestamp
- selected future price-time region
- target expiry/window
- market snapshot / market-implied information at creation
- user risk constraints
- selected expression reference (nullable until later bridge)
- lifecycle/status fields needed by later monitoring

Reuse `msosWorkflowStore` rather than inventing a second persistence plane. Keep the slice paper/simulation only.

## Allowed Product Paths

- `apps/msos-web/src/lib/regionBet.ts`
- `apps/msos-web/src/lib/msosWorkflowStore.ts`
- `apps/msos-web/src/app/api/theses/region-bet/route.ts`
- `tests/test_msos_web_region_bet_contract.py`

## Forbidden Paths

- Broad Region Bet UI redesign / guided stepper (owned by `region_bet_guided_shell_v1`).
- Options Horizon comparison rebuild (reconcile Autobuilder draft PR #5427 before `region_bet_market_compare_bridge_v1`).
- Expression fit ranking rebuild (reconcile Autobuilder draft PR #5428 before `region_bet_risk_expression_bridge_v1`).
- Live brokerage, order tickets, wallets, custody, or personalized financial advice.
- Autobuilder source redesign, jobs feed mutation beyond this charter, or archive inspection.

## Deterministic Contract

Same Region Bet payload must round-trip through validate → upsert → load with stable schema_version and required fields. Invalid payloads fail closed.

## Acceptance Tests

- Contract schema/type guard covers required fields and rejects malformed payloads.
- Workflow store supports `kind: "region_bet"` (or equivalent) CRUD + current pointer.
- API route supports authenticated GET/PUT with local fail-closed validation.
- Charter regression: no dependency on implementing #5427/#5428 product surfaces in this slice.

## Non-Goals

No guided shell UI, no market-compare bridge, no expression ranking, no monitor P/L teaching surface, no live execution.

## Rollback

Revert only the Region Bet contract module, store extensions, API route, and tests. Existing horizon-region / thesis / expression persistence must remain intact.
