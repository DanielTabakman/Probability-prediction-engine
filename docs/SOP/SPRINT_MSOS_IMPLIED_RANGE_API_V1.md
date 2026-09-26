# Sprint — MSOS Implied Range API v1

Parent: #5501  
Engineering OS lane: API / Distribution  
Backlog class: Committed

## Objective

Ship one narrow, production-quality read-only API primitive:

`GET /v1/implied-range`

The implementation must reuse the existing Options Horizon / Options Market Read calculation, market-data producer, and deployment pattern. The purpose is composability for agents and external clients, not a second options-analysis stack.

## Inputs

- `asset`: BTC or ETH
- `expiry`: explicit supported listed expiry
- optional `strike`: positive threshold

## Output

Return deterministic machine-readable fields for snapshot time, spot, forward, ATM IV, implied distribution quartiles/one-sigma range, quality, and optional strike probability.

## Quality

Never invent data. Distinguish good, degraded, and unavailable results with stable flags/errors. Preserve UTC timestamps and explicit units.

## Implementation rules

1. Inspect and reuse the existing Options Market Read and Options Horizon code before adding logic.
2. Prefer a thin wrapper/new response contract over changes to shared financial math.
3. If a shared helper must change, cover both old and new consumers with regression tests.
4. Keep Qatom/payment/catalog details outside the financial core.
5. No execution, custody, recommendation, or portfolio behavior.

## Verification

- BTC fixture
- ETH fixture
- degraded-data fixture
- unavailable-source fixture
- invalid inputs rejected before calculation
- probability and distribution invariants
- OpenAPI example validates
- direct HTTP path works without Qatom
- existing Options Market Read tests remain green
