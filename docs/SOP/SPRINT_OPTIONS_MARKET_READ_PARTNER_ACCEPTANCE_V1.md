# Options Market Read partner acceptance v1

## COORDINATION STATUS

**HIGH / PLANNED — NOT SELECTED.** Keep `msos_market_moved_since_v1` as the sole
READY active chapter. Promote this chapter only after that chapter is terminal
and the Tuesday Qatom meeting records the open partner-control decisions.

## Goal

Turn the working BTC Options Market Read v1.3 primitive into an
integration-ready partner contract: frozen enough to build against, easy to
test, observable in production, and honest about what remains undecided.

## Already exists

- Production `GET /v1/options-market-read`, schema `1.3`, ruleset
  `options-market-read.v1.3`, BTC only.
- Isolated staging API/process/cache and a human date-selection console.
- Deterministic two-sentence `answer`, structured metrics, explicit expiry
  resolution, disclosures, and exact UTC freshness.
- Production uptime agreement check against the source display payload.
- Versioned API/OpenAPI documentation and a one-page Qatom handoff.

## Gap

The primitive works, but partner acceptance is not yet a closed, repeatable
release process. Qatom still needs a witnessed request/response contract,
consumer rendering guidance, explicit decisions on public-access controls, and
a promotion/rollback receipt that does not depend on verbal memory.

## Exact scope

- Freeze v1.3 compatibility and state the additive-change policy.
- Build one deterministic conformance witness that can run against isolated
  staging and production.
- Cover default, exact, nearest-before/after, no-close-expiry, past date,
  unsupported asset, freshness, finite values, width identity, and display
  payload agreement.
- Keep the API doc, OpenAPI document, machine help, human help, and Qatom
  handoff synchronized.
- Record explicit decisions for authentication, rate limits, CORS, alert
  destination, and privacy-safe usage telemetry. An undecided control remains
  explicitly undecided; the worker must not invent one.
- Prove staging-first promotion, production health, and bounded rollback.

## Tuesday decision inputs

1. Where in Qatom will the answer appear, and which fields will be rendered?
2. Will Qatom call from its backend or directly from a browser/client?
3. Is partner authentication required before wider release?
4. What rate limit and service expectation are appropriate for the preview?
5. Where should failed uptime checks alert a human?
6. Which non-identifying usage counters are useful, if any?

## Allowed product paths

- `docs/API/OPTIONS_MARKET_READ_V1.md`
- `docs/API/QATOM_OPTIONS_MARKET_READ_HANDOFF_V1.md`
- `docs/API/options-market-read.openapi.yaml`
- `apps/msos-web/src/app/options-market-read/api-help/route.ts`
- `scripts/options_market_read_partner_acceptance.py`
- `scripts/options_market_read_uptime.py`
- `tests/test_options_market_read_partner_acceptance.py`
- `tests/test_options_market_read_uptime.py`

## Acceptance tests

- The conformance witness passes against staging before production promotion.
- Production remains schema/ruleset v1.3 and agrees with its display payload.
- Same snapshot/request remains deterministic; all required numbers are finite.
- Partner docs and machine help state the same request, resolution, field, and
  error contracts.
- The decision record names each chosen or deliberately deferred public-access
  control; no secret, identity, or Qatom configuration is committed here.
- Rollback changes only the partner-acceptance slice and leaves the base v1.3
  market calculation available.

## Non-goals

No ETH or other asset, historical uncertainty regime, exposure opportunity,
strategy construction, trade recommendation, execution, payment, Qatom source,
or wildcard `/v1/*` route. Those require separately selected chapters.

## Rollback

Revert only partner-acceptance witnesses, documentation, machine help, and any
explicitly approved boundary control. Preserve the v1.3 endpoint, display
payload producer, isolated staging topology, and existing uptime monitor unless
the closeout evidence proves one of those is itself unsafe.
