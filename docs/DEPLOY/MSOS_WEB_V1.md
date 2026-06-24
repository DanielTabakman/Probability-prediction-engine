# MSOS web deploy notes (public launch)

**Service:** `msos_web` in [`docker-compose.yml`](../../docker-compose.yml)  
**Route:** Caddy apex (`marketstructureos.com`) → `msos_web:3000`  
**App host:** `app.marketstructureos.com` → Streamlit `app_full` (unchanged)

## Routing (Caddy)

| Host | Backend | Notes |
|------|---------|-------|
| `marketstructureos.com` (apex) | `msos_web:3000` | Next.js MSOS shell (homepage, `/command-center`, `/strategy-lab`, …) |
| `app.marketstructureos.com` | `app_full:8501` | Private Streamlit lab (Cloudflare Access) |

See [`Caddyfile`](../../Caddyfile) — `X-Forwarded-Proto` / `X-Forwarded-Host` forwarded for Cloudflare Flexible.

## Environment (VPS `.env`)

Copy from [`.env.example`](../../.env.example). Keys consumed at **`msos_web` build** (Next.js `NEXT_PUBLIC_*`) and runtime:

| Variable | Service | Purpose |
|----------|---------|---------|
| `PPE_RESEARCH_OFFER_URL` | `msos_web` build + `app_demo` | Maps to `NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL` at build; research-beta CTA on apex |
| `PPE_RESEARCH_OFFER_LABEL` | `msos_web` build + `app_demo` | Maps to `NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL` at build |
| `NEXT_PUBLIC_MSOS_SIGN_IN_URL` | `msos_web` build | Sign-in link target (default `https://app.marketstructureos.com`) |
| `NEXT_PUBLIC_PPE_EMBED_URL` | `msos_web` build | Strategy Lab iframe src (default `/ppe-embed` — Caddy → `app_demo`) |
| `NEXT_PUBLIC_PPE_DISPLAY_API_URL` | `msos_web` build | Native chart JSON (default `/ppe-display-api/display.json` — Caddy → `ppe_display_api`) |
| `MSOS_UPGRADE_OFFER_URL` | `msos_web` runtime | Lemon Squeezy checkout URL for free-tier upgrade CTA |
| `LEMONSQUEEZY_WEBHOOK_SECRET` | `msos_web` runtime | Lemon Squeezy webhook HMAC secret — auto-grant `paid` tier |

When research-offer vars are unset, homepage omits the CTA (honest public shell). When embed URL is unset at build, Strategy Lab shows degraded “Embed pending” state. Billing setup: [`LEMON_SQUEEZY_OPERATOR_SETUP_V1.md`](../SOP/LEMON_SQUEEZY_OPERATOR_SETUP_V1.md).

`PPE_WEB_FEEDBACK_DIR=/data` is set in compose; feedback volume `msos_web_data` is created automatically.

## Command Center snapshot mount (user state v1)

`msos_web` mounts the shared `ppe_snapshots` volume **read-only** at `/ppe-snapshots` and sets `PPE_SNAPSHOT_DB_PATH=/ppe-snapshots/ppe_frozen_evaluations.sqlite3` so the Command Center API can read freezes written by `app_full`. See [`MSOS_USER_STATE_SNAPSHOT_MOUNT.md`](MSOS_USER_STATE_SNAPSHOT_MOUNT.md).

## PPE embed proxy (Caddy)

| Path | Backend | Notes |
|------|---------|-------|
| `/ppe-embed/*` | `app_demo:8501` | Same-origin Streamlit demo for Strategy Lab iframe (`NEXT_PUBLIC_PPE_EMBED_URL=/ppe-embed`) |
| `/ppe-display-api/*` | `ppe_display_api:8765` | Read-only distribution display JSON (`embed_display_boundary`; chromeless fallback uses `/ppe-embed?embed_only=1`) |

Strip prefix `/ppe-embed` before upstream. See [`MSOS_P1_STACK_ROUTING_ADR.md`](../SOP/MSOS_P1_STACK_ROUTING_ADR.md).

## Local build

```bash
cd apps/msos-web
npm ci
npm run build
```

## VPS operator steps

Run on `/opt/marketstructureos` after merge to `main` (or use **Deploy VPS** GitHub Action — see [`GITHUB_ACTIONS_VPS_DEPLOY.md`](GITHUB_ACTIONS_VPS_DEPLOY.md)).

```bash
cd /opt/marketstructureos
git pull

# Repo-root .env (not committed) — research beta CTA on apex + demo:
#   PPE_RESEARCH_OFFER_URL=mailto:you@example.com?subject=PPE%20research%20beta
#   PPE_RESEARCH_OFFER_LABEL=Request research beta access
#   NEXT_PUBLIC_PPE_EMBED_URL=/ppe-embed

docker compose build msos_web
docker compose up -d --build
docker compose up -d --force-recreate caddy msos_web
```

### Verify

1. `https://marketstructureos.com/` — Next.js MSOS homepage (not Streamlit title).
2. `https://marketstructureos.com/command-center` — MSOS shell routes load.
3. `https://app.marketstructureos.com` — Streamlit lab still works behind Access.
4. With `.env` set — research-beta button visible on apex homepage; link opens mailto/URL.
5. `/strategy-lab` — PPE embed iframe loads (not “Embed pending”) when built with `NEXT_PUBLIC_PPE_EMBED_URL=/ppe-embed`.

Record results in [`docs/SOP/VALIDATION_DEPLOY_WITNESS.md`](../SOP/VALIDATION_DEPLOY_WITNESS.md).

**Status:** compose + Caddy wired in-repo; VPS witness **PASS** after steward runs steps above and confirms URLs.
