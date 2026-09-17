# Isolated Options Market Read API staging — bounded plan

This is a plan, not a deployed environment. Isolated API staging is **not live**.

Do not invent a hostname, DNS record, certificate, secret, or deployment authority from this document.

## Current production

- One public API process: Docker service `ppe_display_api` (`python -m src.viz.display_payload_server`).
- Exact Caddy routes on the production host: `GET /ppe-display-api/*` and `GET /v1/options-market-read` → `ppe_display_api:8765`.
- In-process TTL cache plus `ppe_display_cache_refresh`. Compose TTL is 900s with refresh every 300s.
- Production URL: `https://marketstructureos.com/v1/options-market-read`.

## Current staging (MSOS shell only)

Existing staging is the Next.js shell:

- Hostname already in-repo: `staging.marketstructureos.com` → `msos_web_staging:3001`.
- Separate git checkout `/opt/marketstructureos-staging` and compose profile `staging`.
- `msos_web_staging` still points at **production** `ppe_display_api:8765`.
- Caddy `@staging` handles the whole staging host first, so `/v1/options-market-read` on that hostname is **not** the Python API.

That is not isolated API staging. Production traffic is not routed through the staging shell, but the API cache and process are shared.

## Desired design (not implemented)

1. One production API (`ppe_display_api`) serving apex `GET /v1/options-market-read`.
2. One separately deployed staging API running staging code.
3. Separate process/container and cache.
4. No shared mutable snapshot override (`PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH` stays test-only).
5. No production traffic routed through staging.
6. The same Options Market Read contract tests run against staging before promotion.

## Platform requirements a founder must supply before implementation

Until these exist, do not pretend staging is deployed:

| Decision | Why it is required |
|---|---|
| Staging API hostname | Caddy needs an exact host matcher. Do not reuse apex. `staging.marketstructureos.com` currently belongs to the MSOS shell; using it for the API would collide unless routes are re-ordered by the founder. |
| DNS record | Cloudflare (or equivalent) must point that hostname at the existing VPS, or a founder-chosen other target. |
| Certificate | TLS for the new hostname (Cloudflare proxy or origin cert). |
| Deploy authority | Whether **Deploy VPS Staging** may rebuild an API container, or a new workflow/secret is required. Production and staging deploys already share the `deploy-vps` concurrency group. |
| Cache isolation | Separate container, memory, and refresh loop. No shared `PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH`. |
| Promotion gate | Run `tests/test_options_market_read.py` (and display/Caddy tests) against the staging base URL before merging to `main`. |

## Out of scope until those decisions land

- Adding `/v1/*` wildcard routing
- Changing production path `/v1/options-market-read`
- Enabling ETH or a second asset
- Pointing Qatom at a staging URL
- Inventing ntfy/DNS/TLS secrets in this repository

## Suggested implementation order (after platform choices)

1. Add `ppe_display_api_staging` to compose with its own cache env and no production volume/cache sharing.
2. Add an exact-path Caddy host block for the founder-chosen hostname, proxying only `/v1/options-market-read` and `/ppe-display-api/*` to the staging API. Keep apex routes on production `ppe_display_api`.
3. Extend **Deploy VPS Staging** to rebuild the staging API from a specified git ref without recreating production `ppe_display_api`.
4. Point contract tests at the staging base URL in CI before promotion.
5. Keep BTC-only and the informational-only product boundary.
