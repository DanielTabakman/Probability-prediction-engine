# Demo UI release checklist (local to production)

Use this for **Streamlit UI / copy / theme** changes that should appear on **`marketstructureos.com`** and **`app.marketstructureos.com`**. Deep VPS setup (TLS, Cloudflare Access, backups) lives in [RUNBOOK_VPS_CLOUDFLARE_ACCESS.md](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md).

**Canonical production protocol:** [PRODUCTION_DEPLOY_PROTOCOL.md](PRODUCTION_DEPLOY_PROTOCOL.md) (branch `main`, VPS alignment, Actions vs manual). This file focuses on local smoke, tests, and the manual deploy block in §4.

**GitHub Actions:** If [GitHub Actions VPS deploy](../DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md) is enabled and repository secrets are set, **merges to `main` redeploy the VPS automatically**. Prefer **PR auto-merge** when checks pass so you are not the merge bottleneck ([GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md)). You can still run **§4** manually for hotfixes or when debugging the server.

**Validation Chapter:** After merging to `main`, confirm deploy then run [DEMO_OPERATOR_SCRIPT.md](DEMO_OPERATOR_SCRIPT.md) against production hostnames.

**Important:** Without that workflow (or if secrets are missing), pushing to GitHub does **not** update the live site until you run **§4** on the VPS. Cursor **autocommit** (see [README](../../README.md) and [`.cursor/rules/auto-commit.mdc`](../../.cursor/rules/auto-commit.mdc)) only updates git, not Docker on the server.

## 1) Local smoke

From the repo root (with venv active if you use one):

```bash
streamlit run src/viz/app.py
```

Confirm at least:

- Browser tab title **Probability Engine** and chart favicon (when running current `src/viz/app.py`).
- Expander **How to use this demo (~2 min)** (first load may open it once per session).
- **Debug: performance** and in-page **Debug …** expanders are **hidden** unless `PPE_SHOW_DEBUG_UI=1`.

Optional demo CTA check (matches production demo service):

```bash
# Windows PowerShell example
$env:PPE_ENABLE_SNAPSHOTS="0"
$env:PPE_PRIVATE_APP_URL="https://app.marketstructureos.com"
streamlit run src/viz/app.py
```

You should see **Get full access** and the short demo banner.

Optional research-offer CTA (Commercial Validation v0):

```bash
$env:PPE_ENABLE_SNAPSHOTS="0"
$env:PPE_PRIVATE_APP_URL="https://app.marketstructureos.com"
$env:PPE_RESEARCH_OFFER_URL="mailto:research@example.com?subject=PPE%20beta"
streamlit run src/viz/app.py
```

You should see the **Research beta (v0)** line and the offer button (honest copy; no guaranteed returns).

## 2) Tests

Per [README](../../README.md) testing policy:

```bash
python -m pytest -q
```

For a narrow UI-only pass, at minimum:

```bash
python -m pytest tests/test_signup_cta.py -q
```

## 3) Git: review, commit, push

```bash
git status
git diff
```

Commit with a clear message. Push to your **feature branch**, open a PR to **`main`**, and enable **auto-merge** when you want zero-touch ship after CI ([GITHUB_ZERO_TOUCH_MERGE.md](GITHUB_ZERO_TOUCH_MERGE.md)). The VPS tracks **`main`** only.

**Do not** commit `.env`, secrets, `artifacts/`, caches, or local DB files.

## 4) Deploy on the VPS

SSH to the server, then (paths match the runbook):

```bash
cd /opt/marketstructureos
git pull
docker compose up -d --build
```

This rebuilds images so the `Dockerfile` **`COPY . /app`** layer includes your latest code.

**Caddy-only** config edits: after `git pull`, `docker compose restart caddy` is often enough; a full rebuild is optional unless app code changed (see runbook §10).

## 5) Post-deploy smoke

In the browser (incognito or hard refresh helps):

1. **`https://marketstructureos.com`** — demo loads; optional **Get full access** / private-app CTA if `PPE_PRIVATE_APP_URL` is set on `app_demo`.
2. **DevTools → Network** — requests under **`/static/js/`** use **`https://`**, not `http://` (no failed dynamic imports in the console).
3. **`https://app.marketstructureos.com`** — Cloudflare Access works; after login, full app loads with snapshots as configured.

## 6) Rollback mindset

If something is wrong after deploy: `git log -1` on the VPS, revert to a known-good commit, `git pull` / checkout that ref, then `docker compose up -d --build` again. Restic backup flow is in the main runbook if data volumes are involved.
