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

Copy from [`.env.example`](../../.env.example). Keys consumed by **`msos_web`** (same pattern as `app_demo` Streamlit):

| Variable | Service | Purpose |
|----------|---------|---------|
| `PPE_RESEARCH_OFFER_URL` | `msos_web`, `app_demo` | `https://` or `mailto:` link for research-beta CTA on apex homepage |
| `PPE_RESEARCH_OFFER_LABEL` | `msos_web`, `app_demo` | Optional button label (default in app: `Request research beta access`) |

When unset, homepage omits the CTA (honest public shell). Set both on VPS so apex and demo stay aligned.

`PPE_WEB_FEEDBACK_DIR=/data` is set in compose; feedback volume `msos_web_data` is created automatically.

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

docker compose build msos_web
docker compose up -d --build
docker compose up -d --force-recreate caddy msos_web
```

### Verify

1. `https://marketstructureos.com/` — Next.js MSOS homepage (not Streamlit title).
2. `https://marketstructureos.com/command-center` — MSOS shell routes load.
3. `https://app.marketstructureos.com` — Streamlit lab still works behind Access.
4. With `.env` set — research-beta button visible on apex homepage; link opens mailto/URL.

Record results in [`docs/SOP/VALIDATION_DEPLOY_WITNESS.md`](../SOP/VALIDATION_DEPLOY_WITNESS.md).

**Status:** compose + Caddy wired in-repo; VPS witness **PASS** after steward runs steps above and confirms URLs.
