## Runbook: VPS + Docker + Caddy + Cloudflare Access + R2 backups

This runbook deploys hostnames on one VPS:

- **`marketstructureos.com`**: public **MSOS Next.js shell** (homepage, Strategy Lab, Command Center — no login)
- **`staging.marketstructureos.com`**: **staging MSOS shell** for experiments (see [`MSOS_STAGING_V1.md`](MSOS_STAGING_V1.md))
- **`app.marketstructureos.com`**: **full** Streamlit lab (Google login via Cloudflare Access, snapshots enabled + persisted + backed up)

### 0) What you need

- A VPS running **Ubuntu 24.04** (recommended) with a public IPv4
- Your domain on Cloudflare (`marketstructureos.com`)
- Ability to SSH into the VPS with a key
- Cloudflare Zero Trust enabled
- A Cloudflare R2 bucket for backups

### 1) VPS baseline setup

On the VPS:

- Create a non-root user (example `ppe`) with sudo
- Disable SSH password auth; use SSH keys only
- Firewall: allow **22**, **80**, **443**
- Enable unattended upgrades

#### Hetzner Cloud firewall (recommended)

If the VPS is on Hetzner Cloud, attach a **Cloud Firewall** to the server instead of relying only on OS-level rules:

- **Inbound allow:** TCP **22** (SSH; restrict source to your home/office IP if practical), TCP **80**, TCP **443**
- **Inbound default:** deny all other ports
- Attach the firewall to the server in the Hetzner console

This reduces exposure if a future service is accidentally bound to a public interface.

#### Optional scheduled reboot

Some teams schedule a low-traffic **weekly reboot** after kernel updates or to clear rare memory leaks. Expect roughly **1–2 minutes** of downtime while the machine and Docker stack come back.

Example (Sundays 04:30 UTC; adjust the window to your traffic):

```cron
30 4 * * 0 /sbin/shutdown -r now
```

Run the cron entry as **root** (or use `sudo crontab -e` for root’s crontab). If you prefer not to automate reboots, reboot **manually** after major kernel upgrades instead.

### 2) Install Docker

Install Docker Engine + Compose plugin (Ubuntu).

Verify:

```bash
docker --version
docker compose version
```

### 3) Put the app on the VPS

Pick an app root on the VPS:

```bash
sudo mkdir -p /opt/marketstructureos
sudo chown -R $USER:$USER /opt/marketstructureos
cd /opt/marketstructureos
```

Copy the repo to the VPS (either `git clone` from GitHub, or `scp`).

You should have at least these files in `/opt/marketstructureos`:

- `Dockerfile`
- `requirements.txt`
- `src/viz/app.py`
- `docker-compose.yml`
- `Caddyfile`

### 4) Cloudflare DNS records

In Cloudflare DNS for `marketstructureos.com`:

- **A** record: `@` → your VPS IPv4 (**Proxied**)
- **A** record: `app` → your VPS IPv4 (**Proxied**)
- **A** record: `staging` → your VPS IPv4 (**Proxied**) — optional; for MSOS staging shell

### 5) Cloudflare TLS mode (pick one)

The Caddy config in this repo uses **`auto_https off`** and serves **HTTP on port 80** at the origin (simple + reliable before DNS). Cloudflare must match that until you add TLS on the origin.

**Phase A — go live quickly (recommended first)**

In Cloudflare → **SSL/TLS** → **Overview**:

- Set mode to **Flexible**  
  - Visitors → Cloudflare: **HTTPS**  
  - Cloudflare → your VPS: **HTTP (port 80)**  
  - Fine for an early launch; encryption is still HTTPS in the browser.

**Phase B — stricter origin encryption (later)**

When you want **Full (strict)** (Cloudflare → origin must be **HTTPS** with a trusted cert):

1. Cloudflare → **SSL/TLS** → **Origin Server** → **Create certificate** (15-year origin cert). Include hostnames such as `marketstructureos.com` and `*.marketstructureos.com` (or at least `app.marketstructureos.com`).
2. Save the PEM bundle and private key on the VPS under the repo `certs/` directory: `certs/cloudflare-origin.pem` and `certs/cloudflare-origin-key.pem` (`chmod 600` on the key). See [`certs/README.md`](../../certs/README.md).
3. In repo-root `.env` on the VPS: `PPE_CADDYFILE=./Caddyfile.tls`
4. Reload Caddy: `docker compose up -d caddy` (mounts `./Caddyfile.tls`, terminates TLS on **:443**, adds HSTS + security headers).
5. Cloudflare → **SSL/TLS** → **Overview** → set mode to **Full (strict)**.

Until Phase B is done, **do not** use **Full (strict)** with an HTTP-only origin or the edge will fail to connect.

**Security headers:** both Phase A and B Caddy configs import [`caddy/snippets.caddy`](../../caddy/snippets.caddy) (`X-Content-Type-Options`, `Referrer-Policy`, etc.). MSOS Next routes also get a baseline CSP. HSTS is enabled only on Phase B (`:443`).

**Operator checklist:** one-page post-hardening steps (ntfy, VPS smoke, Phase B TLS) — [`SECURITY_OPERATOR_CHECKLIST_V1.md`](SECURITY_OPERATOR_CHECKLIST_V1.md).

### 6) Bring up the stack (first boot)

From `/opt/marketstructureos`:

```bash
docker compose up -d --build
docker compose ps
```

Expected:

- Caddy listens on ports 80/443.
- `marketstructureos.com` proxies to the demo container.
- `app.marketstructureos.com` proxies to the full container (Access will be added next).

#### Streamlit and HTTPS (Caddy forwarded headers)

With **Cloudflare Flexible**, browsers use **HTTPS** while Cloudflare talks **HTTP** to your origin. Streamlit must still see the **original visitor scheme**; otherwise it emits **`http://…/static/js/…`** URLs for lazy-loaded widgets and the browser blocks them (**mixed content**), with console errors like `Failed to fetch dynamically imported module`.

The repo [`Caddyfile`](../../Caddyfile) fixes this by:

- Computing **`X-Forwarded-Proto`** from the incoming **`X-Forwarded-Proto`** header when set, else **`https`** when **`CF-Ray`** is present (traffic came through Cloudflare), else the request’s own scheme (useful for raw HTTP tests).
- Sending **`X-Forwarded-Host`** from the incoming **`Host`**.

If chunk URLs are still **`http://`** after a deploy: confirm Cloudflare is **proxied** (orange cloud), reload Caddy (`docker compose restart caddy`), and check `docker compose logs caddy` for config errors.

### 7) Cloudflare Access (Google login) for `app.marketstructureos.com`

#### 7.1) Add Google as an identity provider

In Cloudflare Zero Trust:

- Settings → Authentication → Login methods → **Google**

You will be prompted for:

- **Client ID**
- **Client Secret**

Create these in Google Cloud Console:

- APIs & Services → Credentials → Create credentials → **OAuth client ID**
- Type: **Web application**
- Add the **Authorized redirect URI** Cloudflare provides in the Zero Trust UI

Do **not** share your Google password; only Cloudflare’s OAuth client credentials are used.

#### 7.2) Create the Access application

- Access → Applications → Add an application → **Self-hosted**
- Application domain: `app.marketstructureos.com`

Policy (default):

- Allow: your Gmail address (and any others you choose)

Verify:

- `marketstructureos.com` is public (no login)
- `app.marketstructureos.com` prompts for Google login

### 8) Snapshots persistence configuration

The full app is configured by `docker-compose.yml` to:

- Set `PPE_ENABLE_SNAPSHOTS=1`
- Set `PPE_SNAPSHOT_DB_PATH=/data/ppe_frozen_evaluations.sqlite3`
- Mount a named Docker volume `ppe_snapshots` at `/data`

The demo app sets:

- `PPE_ENABLE_SNAPSHOTS=0`
- Optional: `PPE_PRIVATE_APP_URL` (HTTPS URL of the full app) so the public demo shows a **“Sign in to save work”** banner linking users to persistent snapshots on the private hostname.

### 9) Backups to Cloudflare R2 (restic)

#### 9.1) Create R2 bucket + access keys

In Cloudflare R2:

- Create a bucket (example `marketstructureos-backups`)
- Create R2 API credentials (access key + secret)
- Note your account’s R2 S3 endpoint hostname

#### 9.2) Install restic on the VPS

Install `restic` and `awscli` (optional) via apt or vendor instructions.

#### 9.3) Configure restic env

On the VPS:

```bash
mkdir -p /opt/marketstructureos/ops/restic
cp ops/restic/env.example ops/restic/env.local
chmod 600 ops/restic/env.local
```

Edit `ops/restic/env.local`:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `RESTIC_REPOSITORY` (R2 endpoint + bucket)
- `RESTIC_PASSWORD`

Initialize repository once:

```bash
cd /opt/marketstructureos
ENV_FILE=/opt/marketstructureos/ops/restic/env.local ./ops/restic/backup.sh
```

If this is the first run and the repo doesn’t exist yet, run:

```bash
source /opt/marketstructureos/ops/restic/env.local
restic init
```

Then rerun `backup.sh`.

#### 9.4) Schedule backups

Simplest initial schedule is cron (example: nightly 03:15 UTC):

```bash
crontab -e
```

Add:

```cron
15 3 * * * cd /opt/marketstructureos && ENV_FILE=/opt/marketstructureos/ops/restic/env.local APP_ROOT=/opt/marketstructureos ./ops/restic/backup.sh >> /var/log/marketstructureos-backup.log 2>&1
```

**Restore drill:** At least **monthly**, practice a restore on a staging path using [section 11](#11-restore-drill-when-needed) so you are not learning `restic` under incident pressure. The scripts live under `ops/restic/` (`backup.sh`, `restore.sh`).

### 10) Deploy updates

For a **short end-to-end order** (local smoke → tests → git → these commands → browser checks), use **[DEMO_UI_RELEASE_CHECKLIST.md](../SOP/DEMO_UI_RELEASE_CHECKLIST.md)**. Optional **GitHub Actions** auto-deploy on `main` is documented in **[GITHUB_ACTIONS_VPS_DEPLOY.md](GITHUB_ACTIONS_VPS_DEPLOY.md)**.

On the VPS:

```bash
cd /opt/marketstructureos
git pull
docker compose up -d --build
```

Smoke checks after a deploy:

- **`https://marketstructureos.com`**: public demo loads; if `PPE_PRIVATE_APP_URL` is set on `app_demo`, you should see the **Get full access** (or equivalent) banner and link to the private app.
- **Streamlit assets (both hostnames):** in browser DevTools → Network, requests under **`/static/js/`** must use **`https://`** (not `http://`). The console should not show `Failed to fetch dynamically imported module` for those paths.
- **`https://app.marketstructureos.com`**: Cloudflare Access login still works; after sign-in, the full app loads with snapshots enabled.

After changing only [`Caddyfile`](../../Caddyfile), `git pull` and `docker compose restart caddy` (or `docker compose up -d`) is enough; a full image rebuild is optional unless app code changed.

### 11) Restore drill (when needed)

List snapshots:

```bash
source /opt/marketstructureos/ops/restic/env.local
restic snapshots
```

Restore to a staging directory:

```bash
cd /opt/marketstructureos
ENV_FILE=/opt/marketstructureos/ops/restic/env.local ./ops/restic/restore.sh latest
```

Then follow the printed instructions to copy restored data into the `ppe_snapshots` volume.

### 12) Troubleshooting

- Check running containers:
  - `docker compose ps`
  - `docker compose logs -n 200 caddy`
  - `docker compose logs -n 200 app_full`
- If Access blocks you unexpectedly:
  - Zero Trust → Access → Logs
- If Streamlit loads but **widgets fail** with **`http://…/static/js/`** in the console, re-check [Streamlit and HTTPS (Caddy forwarded headers)](#streamlit-and-https-caddy-forwarded-headers) and Caddy’s `header_up` / `map` block in [`Caddyfile`](../../Caddyfile).
- If Streamlit is slow:
  - Use the app’s **Debug: performance** expander and verify Deribit/Yahoo calls.
