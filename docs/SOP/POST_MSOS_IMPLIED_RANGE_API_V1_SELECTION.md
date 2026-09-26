# Post-selection — MSOS Implied Range API v1

Selected under Engineering Operating System v1 as the first new API / Distribution primitive after the existing Options Market Read v1.3 path proved the deployment and partner-integration pattern.

## Decision

Build `msos_implied_range_api_v1` as Autobuilder catalog order 18.

## Reuse boundary

Adopt the existing Options Horizon / Options Market Read producer, calculation, cache, staging, and API conventions wherever possible. Do not create a parallel market-data or distribution engine.

## Deferred behind this item

Historical catalog orders 14–17 remain preserved but are not current Engineering OS priorities. Region Bet management/learning expansion is explicitly deferred until Factory/MSOS/API foundations are further along.

## Founder attention

None required to begin implementation. Escalate only for credentials/spend, a material change in financial semantics, or expansion into advice/execution.
