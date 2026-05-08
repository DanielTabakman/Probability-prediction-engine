## Runbook: VPS + Docker + Caddy + Cloudflare Access + R2 backups

This runbook deploys two hostnames on one VPS:

- **`marketstructureos.com`**: public **demo** (no login, snapshots disabled)
- **`app.marketstructureos.com`**: **full** app (Google login via Cloudflare Access, snapshots enabled + persisted + backed up)

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

### 5) Cloudflare TLS mode

In Cloudflare → SSL/TLS:

- Set mode to **Full (strict)**

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

### 10) Deploy updates

On the VPS:

```bash
cd /opt/marketstructureos
git pull
docker compose up -d --build
```

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
- If Streamlit is slow:
  - Use the app’s **Debug: performance** expander and verify Deribit/Yahoo calls.

