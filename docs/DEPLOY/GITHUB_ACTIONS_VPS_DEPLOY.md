# GitHub Actions: deploy to VPS on `main`

This repository includes [`.github/workflows/deploy-vps.yml`](../../.github/workflows/deploy-vps.yml), which **SSHs into your VPS** and runs the same deploy commands as [RUNBOOK_VPS_CLOUDFLARE_ACCESS.md](RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) section **10) Deploy updates**:

```bash
cd /opt/marketstructureos
git pull
docker compose up -d --build
```

## Related

- **[PRODUCTION_DEPLOY_PROTOCOL.md](../SOP/PRODUCTION_DEPLOY_PROTOCOL.md)** — canonical rule: production tracks **`main`** on the VPS; when to rely on this Action vs manual SSH.
- **[GITHUB_ZERO_TOUCH_MERGE.md](../SOP/GITHUB_ZERO_TOUCH_MERGE.md)** — PR **auto-merge** when **`CI / pytest`** passes; branch protection so merges to **`main`** always ran CI first. After that merge, **this** workflow is what updates the site (no separate human deploy step).

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

Do **not** commit keys or paste them into the repo.

### Set secrets from your machine (GitHub CLI)

If [GitHub CLI](https://cli.github.com/) is installed and you are logged in (`gh auth login`), you can push the three secrets without pasting them into the browser:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/set_github_deploy_secrets.ps1 `
  -VpsHost "YOUR.VPS.HOSTNAME" `
  -VpsUser "YOUR_SSH_USER" `
  -PrivateKeyPath "C:\path\to\deploy_key.pem"
```

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
