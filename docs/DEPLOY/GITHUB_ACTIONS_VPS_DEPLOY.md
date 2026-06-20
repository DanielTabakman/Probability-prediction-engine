# GitHub Actions: deploy to VPS on `main`

This repository includes [`.github/workflows/deploy-vps.yml`](../../.github/workflows/deploy-vps.yml), which **SSHs into your VPS** and runs the same deploy commands as [RUNBOOK_VPS_CLOUDFLARE_ACCESS.md](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) section **10) Deploy updates**:

```bash
cd /opt/marketstructureos
git pull
bash scripts/vps_sync_production_env.sh
docker compose up -d --build
docker compose up -d --force-recreate caddy msos_web
```

## Actions usage policy (2026-06)

**Public repo:** standard Linux runners are **free** for public repositories.

We only **throttle the hogs** — everything else stays automated:

| Workflow | Trigger |
|----------|---------|
| **CI** | Pull requests + push to `main` |
| **Deploy VPS** | Every push to `main` (+ manual **Run workflow**) |
| **Uptime healthcheck** | **Every 30 minutes** (was every 5 — largest minute drain) |
| **Google Docs sync** / **Dev changelog** | Daily schedule + `main` push (dev changelog) |
| **Weekly digest** / **Codebase health** | Weekly schedule |

Optional **VPS cron** for uptime if you want zero GitHub runner use for probes (see runbook).

## Related

- **[PRODUCTION_DEPLOY_PROTOCOL.md](../SOP/PRODUCTION_DEPLOY_PROTOCOL.md)** — canonical rule: production tracks **`main`** on the VPS; when to rely on this Action vs manual SSH.
- **[GITHUB_ZERO_TOUCH_MERGE.md](../SOP/GITHUB_ZERO_TOUCH_MERGE.md)** — PR **auto-merge** when the **CI** workflow is green (**`CI / pytest`** + **`CI / docker_entrypoint`**). After merge, **Deploy VPS** runs on push to **`main`**.

## When it runs

- **Every push to `main`** (including merges that land on `main`).
- **Manual:** GitHub → **Actions** → **Deploy VPS** → **Run workflow** (`workflow_dispatch`).

Only one deploy runs at a time (`concurrency` cancels an in-flight job if a newer push starts).

## Required repository secrets

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | VPS hostname or public IP |
| `VPS_USER` | SSH login user (must own or access `/opt/marketstructureos` and Docker) |
| `VPS_SSH_PRIVATE_KEY` | Full PEM private key (including `-----BEGIN` / `END-----` lines) whose **public** key is in that user’s `~/.ssh/authorized_keys` on the VPS |
| `PPE_RESEARCH_OFFER_EMAIL` | *(optional)* Contact email for research-beta CTA — synced to VPS `.env` on each deploy |
| `PPE_RESEARCH_OFFER_URL` | *(optional)* Full `mailto:` or `https://` URL; overrides `PPE_RESEARCH_OFFER_EMAIL` when set |
| `PPE_RESEARCH_OFFER_LABEL` | *(optional)* CTA button label (default: `Request research beta access`) |

Deploy runs [`scripts/vps_sync_production_env.sh`](../../scripts/vps_sync_production_env.sh) before `docker compose` so `msos_web` rebuild picks up research CTA build args.

Do **not** commit keys or paste them into the repo.

### Set secrets from your machine (GitHub CLI)

If [GitHub CLI](https://cli.github.com/) is installed and you are logged in (`gh auth login`), you can push the three secrets without pasting them into the browser:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/set_github_deploy_secrets.ps1 `
  -VpsHost "YOUR.VPS.HOSTNAME" `
  -VpsUser "YOUR_SSH_USER" `
  -PrivateKeyPath "C:\path\to\deploy_key.pem"
```

**First-time bootstrap (deploy key + secrets + trigger deploy):** see [scripts/setup_vps_deploy_once.ps1](../../scripts/setup_vps_deploy_once.ps1) — run without flags to generate a key and print VPS steps, then `-SecretsOnly` with host/user after the key is on the server.

## VPS prerequisites

1. **Directory:** `/opt/marketstructureos` exists and is a **git clone** of this repository (or a fork you intend to deploy), with `origin` set so **`git pull`** works **non-interactively** (e.g. deploy key read access to GitHub, or HTTPS credential helper). A failing `git pull` fails the workflow.
2. **Docker:** The SSH user can run `docker compose` in that directory. Prefer adding the user to the **`docker`** group. If you must use `sudo`, edit the workflow script to use passwordless `sudo` for those commands only.
3. **Compose:** `docker compose` v2 is available on the server (same as the runbook).

## Security note (GitHub-hosted runners)

Jobs use **`ubuntu-latest`**: outbound SSH comes from **GitHub-managed IPs that change**. You generally **cannot** permanently firewall SSH to “GitHub Actions only” by IP.

Typical mitigations:

- **SSH keys only** (`PasswordAuthentication no`), disable root login over SSH, keep the OS patched.
- Optional: non-default SSH port, `fail2ban`, or allowlisting your own IPs for interactive SSH while still accepting the deploy key from the internet (design carefully).

For a stricter model (no inbound deploy SSH), use a **self-hosted runner on the VPS** instead of this pattern (not implemented here).

## Troubleshooting

| Symptom | Things to check |
|--------|------------------|
| SSH step fails immediately | `VPS_HOST`, `VPS_USER`, key formatting in secrets; `authorized_keys` on server; firewall allows SSH from the internet to your port |
| `git pull` fails | On the VPS, run `cd /opt/marketstructureos && git pull` manually; fix auth (deploy key, HTTPS credentials, or repo visibility) |
| `docker compose` permission denied | User not in `docker` group or missing `sudo` rule |
| Build timeout | Increase `command_timeout` in the workflow file |
| Workflow missing | File must be on **`main`**; workflows from unmerged branches do not apply to repo default until merged |

## Disable or soften automation

- **Turn off auto-deploy on push:** remove the `push` block under `on:` and keep only `workflow_dispatch`, or delete the workflow file.
- **Pause everything:** disable the workflow in the GitHub Actions UI.

## After you merge this workflow

1. Add the three secrets on GitHub.
2. Push to `main` (or use **Run workflow**) and open the **Actions** tab to confirm success.
3. Re-run [post-deploy smoke](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) (demo URL, `/static/js/` over HTTPS, `app.` + Access).

See also [DEMO_UI_RELEASE_CHECKLIST.md](../SOP/DEMO_UI_RELEASE_CHECKLIST.md) for local checks before merging.
