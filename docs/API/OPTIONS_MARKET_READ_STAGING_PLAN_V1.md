# Isolated Options Market Read API staging v1

This document defines the implemented staging topology. The environment is
considered live only when the **Deploy VPS Staging** workflow and both contract
checks pass for the deployed revision.

## URLs

| Environment | Options Market Read | Source display payload |
|---|---|---|
| Production | `https://marketstructureos.com/v1/options-market-read` | `https://marketstructureos.com/ppe-display-api/display.json?asset=BTC&depth=full` |
| Staging | `https://staging.marketstructureos.com/v1/options-market-read` | `https://staging.marketstructureos.com/ppe-display-api/display.json?asset=BTC&depth=full` |

Qatom and other consumers use production. Staging is an unstable engineering
surface and may run feature-branch code.

## Isolation guarantees

- Production runs `ppe_display_api:8765` plus `ppe_display_cache_refresh`.
- Staging runs `ppe_display_api_staging:8766` plus
  `ppe_display_cache_refresh_staging`.
- Staging is built from the separate `/opt/marketstructureos-staging` checkout.
- Each API process owns its own in-memory TTL cache. No snapshot file or mutable
  cache is shared.
- `PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH` remains test-only and is not set in
  compose.
- The staging Next.js shell reads from `ppe_display_api_staging`, not production.
- Caddy routes only the two documented staging API path families to the staging
  process, before the staging-shell catch-all. Production routes remain pointed
  at `ppe_display_api`.
- Staging deploys do not rebuild or recreate `ppe_display_api`, `msos_web`,
  `app_demo`, or `app_full`.

The two environments intentionally use the same public market-data sources and
PPE calculation code. Isolation means code, process, and cache separation; it
does not mean a synthetic or private market-data feed.

## Deployment and promotion

1. Push a feature branch under `staging/**` to deploy it automatically, or
   manually dispatch **Deploy VPS Staging** with `git_ref` set to another branch.
2. The workflow deploys only the staging shell/API/cache-refresh services.
3. It validates the staging shell and runs the full Options Market Read/display
   agreement check against staging.
4. It then verifies production is still healthy.
5. Merge only after staging passes. The normal production workflow remains the
   production promotion path.

The production and staging deployment jobs share the existing `deploy-vps`
concurrency group, so they cannot change the shared Caddy container
simultaneously. The optional production witness runs after the production job
releases that lock and cannot delay staging.

## Product boundary

Staging stays BTC-only and informational-only. It does not add wildcard `/v1/*`
routing, trade recommendations, execution, payment handling, or Qatom
configuration.

## Rollback

Redeploy `main` through **Deploy VPS Staging** to replace feature-branch code. If
the staging API itself must be removed, stop only
`ppe_display_api_staging` and `ppe_display_cache_refresh_staging`; do not touch
the production API containers.
