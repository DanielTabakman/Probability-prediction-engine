# MSOS staging environment

**Goal:** Try big MSOS shell changes on **staging** while **production** (`marketstructureos.com`) stays stable for demos.

| URL | Backend | Purpose |
|-----|---------|---------|
| `https://marketstructureos.com` | `msos_web:3000` | **Production demo** — only `main` deploys here |
| `https://staging.marketstructureos.com` | `msos_web_staging:3001` | **Staging** — feature branches / experiments |
| `https://app.marketstructureos.com` | `app_full:8501` | Private Streamlit lab (unchanged) |

Shared PPE services (`app_demo`, `ppe_display_api`, snapshots) are the same stack — only the Next.js shell differs.

## One-time VPS setup

1. **DNS** (Cloudflare): **CNAME** `staging` → `marketstructureos.com` (**Proxied**). Same VPS as production; Caddy routes by hostname. Automated when `CLOUDFLARE_API_TOKEN` is set in GitHub Actions secrets (see workflow **Deploy VPS Staging**).
2. **Second checkout** on the VPS (automated by `scripts/vps_bootstrap_staging.sh` on first staging deploy):

```bash
sudo mkdir -p /opt/marketstructureos-staging
sudo chown -R $USER:$USER /opt/marketstructureos-staging
git clone https://github.com/<org>/Probability-prediction-engine.git /opt/marketstructureos-staging
cd /opt/marketstructureos-staging
git checkout -b staging origin/main   # or track your staging branch
cp /opt/marketstructureos/.env .env     # optional — research CTA, etc.
```

3. Ensure production Caddy is current (`git pull` on `/opt/marketstructureos`) so `staging.marketstructureos.com` routes exist in `caddy/snippets.caddy`.

## Deploy staging (operator)

**GitHub Actions (recommended):** Actions → **Deploy VPS Staging** → Run workflow → optional `git_ref` (default `main`).

**SSH on VPS:**

```bash
bash /opt/marketstructureos-staging/scripts/vps_deploy_staging.sh origin/my-feature-branch
```

This rebuilds **only** `msos_web_staging`. Production `msos_web` is not recreated.

## Deploy production (unchanged)

Every push to `main` runs **Deploy VPS** — rebuilds `msos_web` only. Staging container is untouched.

```bash
python scripts/ensure_production_deploy.py --trigger --wait
```

## Guards against Streamlit on apex

Deploy and uptime workflows fail when the apex homepage serves Streamlit (`stApp`, etc.) instead of Next.js (`_next/static`). See [`scripts/verify_msos_web_ship.py`](../../scripts/verify_msos_web_ship.py).

`app.marketstructureos.com` is **supposed** to be Streamlit — that is the private lab, not the public demo.

## Local workflow

1. Branch off `main`, push changes.
2. Run **Deploy VPS Staging** with your branch name.
3. Test at `https://staging.marketstructureos.com`.
4. Merge to `main` when ready — production auto-deploys; demo URL stays safe during step 2–3.

## Verify

```bash
python scripts/verify_msos_web_ship.py --apex-only --base-url https://staging.marketstructureos.com
python scripts/verify_msos_web_ship.py --base-url https://marketstructureos.com
```
