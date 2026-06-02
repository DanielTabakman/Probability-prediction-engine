# MSOS web deploy notes (P2)

**Service:** `msos_web` in [`docker-compose.yml`](../../docker-compose.yml)  
**Route:** Caddy apex (`marketstructureos.com`) → `msos_web:3000`  
**App host:** `app.marketstructureos.com` → Streamlit `app_full` (unchanged)

## Local build

```bash
cd apps/msos-web
npm ci
npm run build
```

## VPS (when ready)

1. `docker compose build msos_web`
2. `docker compose up -d msos_web caddy`
3. Verify apex serves Next homepage; `app.*` still serves Streamlit lab.

**Status (P2):** wired in-repo; VPS rollout follows merge to `main`.
