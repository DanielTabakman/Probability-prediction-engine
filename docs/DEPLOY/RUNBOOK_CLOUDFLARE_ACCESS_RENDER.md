# Deploy runbook (early customers)

Goal: publish the Streamlit app with **members-only access** (Google login allowlist) without implementing auth inside the app.

This runbook assumes:
- You are starting without a domain
- You want the simplest path to a working private beta

## 1) Buy a domain

Recommended registrars (simple UI, good pricing):
- Porkbun
- Namecheap
- Cloudflare Registrar (requires moving DNS to Cloudflare; often simplest for Access)

Pick a domain name you can live with for a while (you can move later, but it’s extra work).

## 2) Put DNS on Cloudflare

1. Create a Cloudflare account.
2. Add your domain to Cloudflare.
3. Update your registrar nameservers to the Cloudflare-provided nameservers.
4. Wait for DNS to become “active” in Cloudflare.

## 3) Deploy the app container (Render)

This repo includes:
- `Dockerfile`
- `.dockerignore`

### Create a Render service

1. In Render, create a **New Web Service**.
2. Connect your GitHub repo.
3. Choose **Docker** as the runtime.
4. Confirm the start command is the `Dockerfile` CMD:

```bash
streamlit run src/viz/app.py --server.port $PORT --server.address 0.0.0.0
```

5. Deploy.

### Environment variables (optional)
- `PPE_SNAPSHOT_DB_PATH`: if you later mount a persistent disk and want to point SQLite at it.

## 4) Add a custom domain to Render

1. In Render service settings, add your custom domain (e.g. `app.yourdomain.com`).
2. Render will give you a DNS record (CNAME or A record) to add in Cloudflare.
3. Add the DNS record in Cloudflare.

## 5) Cloudflare Access: Google login allowlist

### Create the Access application

1. In Cloudflare Zero Trust dashboard → **Access** → **Applications** → **Add an application**.
2. Type: **Self-hosted**.
3. Application domain: `app.yourdomain.com` (or whichever subdomain you used).

### Add login method

1. Configure **Google** as an identity provider (Cloudflare docs walk-through).
2. Create an **Access policy**:
   - Include: allowed email addresses (your email + early customers)
   - (Optional) Require MFA

### Verify
- Allowed user: can sign in and see the app
- Non-allowed user: blocked

## 6) Data persistence note (per-user)

For the earliest beta you can run a single instance and keep SQLite on-disk, but on managed platforms it may be ephemeral.

Recommended staging:
- Phase 1: stable single instance (accept that data may reset if the container is recreated)
- Phase 2: move snapshot/review persistence to managed Postgres with `user_id` scoping

## 7) Operational checklist

- Confirm `python -m pytest -q` passes before each deploy.
- Keep `artifacts/` gitignored (already is) so deploys stay small.
- Set a “maintenance email” to contact you if customers can’t log in.

