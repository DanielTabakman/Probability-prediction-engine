# Security operator checklist v1

**Plane:** platform + control-plane. **Audience:** operator (human).  
**Code baseline:** merged in [PR #296](https://github.com/DanielTabakman/Probability-prediction-engine/pull/296) (`platform/security-hardening-v1`).

Use this after security hardening lands on `main`, or when onboarding a new desktop/VPS. Deep VPS setup remains in [`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md). Mobile operator detail: [`PPE_MOBILE_OPERATOR_V1.md`](../SOP/PPE_MOBILE_OPERATOR_V1.md).

---

## A) Desktop — ntfy remote commands (required if phone commands are on)

Remote commands are **enabled by default** when `watch_ntfy_commands` / `ppe_ntfy_listen` runs on the loop host. Security is the **private topic name** (one-time setup in `ppe_operator_notify.local.cmd`), not a per-message prefix.

### One-time

- [ ] Copy `ppe_operator_notify.local.cmd.example` → `ppe_operator_notify.local.cmd` (gitignored), **or** run:
  ```bat
  python scripts\bootstrap_operator_notify_secret.py
  ```
- [ ] Set **`PPE_NTFY_TOPIC`** to a long, unguessable private topic (not the placeholder).
- [ ] Install [ntfy](https://ntfy.sh) on your phone and **subscribe** to that topic.
- [ ] Optional hardening:
  - [ ] `PPE_NTFY_TOKEN` if your ntfy server supports ACL/auth
  - [ ] Self-hosted ntfy behind Tailscale instead of public `ntfy.sh`
  - [ ] `PPE_NTFY_CMD_ENABLED=0` on machines that only need alerts, not commands

### Verify

```bat
python scripts\ppe_notify_push.py --check
python scripts\ppe_notify_push.py --title "PPE test" --body "desktop ready"
```

From the phone (publish to your private topic):

| Message | Expected |
|---------|----------|
| `help` | Command list |
| `status` | Operator snapshot reply |
| `build` | IDE BUILD handoff when verdict allows |

Listener startup should warn if topic/token is unset — check the `ppe_ntfy_listen` console on first run.

---

## B) VPS — after `main` deploy (automatic via GitHub Actions)

Deploy workflow: [`deploy-vps.yml`](../../.github/workflows/deploy-vps.yml) · protocol: [`GITHUB_ACTIONS_VPS_DEPLOY.md`](GITHUB_ACTIONS_VPS_DEPLOY.md).

### Post-deploy smoke (5 min)

- [ ] [Deploy VPS](https://github.com/DanielTabakman/Probability-prediction-engine/actions/workflows/deploy-vps.yml) workflow **green** on latest `main`
- [ ] `https://marketstructureos.com` — loads, no traceback in HTML
- [ ] DevTools → Network → `/static/js/` uses **`https://`** (Streamlit chunks)
- [ ] `https://app.marketstructureos.com` — Cloudflare Access login works; full app loads
- [ ] Public demo: MVP1 **Give feedback** panel should **not** appear (`PPE_ENABLE_SNAPSHOTS=0` on `app_demo`)

### Security headers (optional check)

From a terminal:

```bash
curl -sI https://marketstructureos.com/ | grep -iE 'x-content-type|referrer-policy|permissions-policy|strict-transport'
```

- Phase A (Flexible): expect baseline headers from Caddy; **no HSTS** on origin HTTP yet.
- Phase B (below): expect **`Strict-Transport-Security`** on HTTPS responses.

---

## C) VPS — Phase B TLS (optional, recommended later)

**Current default (Phase A):** Cloudflare **Flexible** + Caddy HTTP on `:80` ([`Caddyfile`](../../Caddyfile)).  
**Upgrade (Phase B):** Cloudflare **Full (strict)** + origin TLS ([`Caddyfile.tls`](../../Caddyfile.tls)).

On the VPS at `/opt/marketstructureos`:

1. [ ] Cloudflare → SSL/TLS → **Origin Server** → create cert (`marketstructureos.com`, `*.marketstructureos.com`)
2. [ ] Save PEMs (do **not** commit):
   - `certs/cloudflare-origin.pem`
   - `certs/cloudflare-origin-key.pem`
   - `chmod 600 certs/cloudflare-origin-key.pem`
3. [ ] Repo-root `.env`:
   ```bash
   PPE_CADDYFILE=./Caddyfile.tls
   ```
4. [ ] `docker compose up -d caddy`
5. [ ] Cloudflare → SSL/TLS → Overview → **Full (strict)**
6. [ ] Re-run smoke in section B

See also [`certs/README.md`](../../certs/README.md) and runbook [§5 TLS](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md).

To revert to Phase A: remove `PPE_CADDYFILE` from `.env` and `docker compose up -d caddy`.

---

## D) GitHub — Google Docs sync (CI only)

CI sync uses minimal scopes (`documents` + `drive.readonly`) — see [`scripts/google_oauth_scopes.py`](../../scripts/google_oauth_scopes.py).

If **Google Docs sync** Actions fail with `insufficientPermissions`:

- [ ] Re-run OAuth consent per [`MCP_GOOGLE_DOCS_SETUP.md`](../SOP/MCP_GOOGLE_DOCS_SETUP.md)
- [ ] Update GitHub secret **`GOOGLE_OAUTH_REFRESH_TOKEN`**

Local Cursor MCP may still use broader scopes; that is separate from CI.

---

## E) Ongoing hygiene (low frequency)

| Cadence | Action |
|---------|--------|
| Weekly | Glance at [Dependency audit](https://github.com/DanielTabakman/Probability-prediction-engine/actions/workflows/dependency-audit.yml) workflow; merge Dependabot PRs when green |
| Monthly | Restic **restore drill** on VPS ([runbook §11](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)) |
| On desktop change | Re-run `bootstrap_operator_notify_secret.py` if `ppe_operator_notify.local.cmd` was lost |
| Quarterly | Review Cloudflare Access policies and SSH key access |

---

## F) Not in this checklist (deferred / separate tracks)

- Self-hosted GitHub runner instead of inbound deploy SSH
- Stripe billing, usable-demo product BUILD, MVP1 math chapters
- Multi-stage Docker image without `build-essential`

---

## Quick reference — env vars

| Variable | Where | Purpose |
|----------|-------|---------|
| `PPE_NTFY_TOPIC` | Desktop `ppe_operator_notify.local.cmd` | Private ntfy topic (one-time setup) |
| `PPE_NTFY_TOKEN` | Same (optional) | ntfy ACL auth |
| `PPE_NTFY_CMD_ENABLED` | Same | `0` = alerts only, no commands |
| `PPE_CADDYFILE` | VPS `.env` | `./Caddyfile.tls` for Phase B |
| `PPE_ENABLE_SNAPSHOTS` | `docker-compose` | `0` demo, `1` full app |
| `PPE_ENABLE_FEEDBACK` | Optional override | Demo feedback panel |
