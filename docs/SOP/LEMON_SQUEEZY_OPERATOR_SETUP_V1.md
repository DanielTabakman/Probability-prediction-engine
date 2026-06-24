# Lemon Squeezy operator setup (MSOS billing v1)

**Provider:** [Lemon Squeezy](https://www.lemonsqueezy.com/) (merchant of record — taxes handled by LS)  
**App integration:** checkout link + webhook auto-grant  
**Charter:** [`SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md`](SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md)

---

## What you get

| Phase | Operator work | Customer experience |
|-------|---------------|---------------------|
| **v0** | Checkout URL in env | Sidebar **Request upgrade** → Lemon Squeezy hosted checkout |
| **v1** | Webhook secret in env | After payment, `paid` tier flips automatically (no manual grant) |

Manual grant remains fallback: `python scripts/msos_grant_entitlement.py --email you@example.com --tier paid`

---

## Step 1 — Lemon Squeezy account

1. Sign up at [lemonsqueezy.com](https://www.lemonsqueezy.com/).
2. Complete store activation (identity + payout bank account).
3. Create a **Subscription** product (e.g. “MSOS Pro — monthly”).

---

## Step 2 — Checkout link (v0 — works immediately after deploy)

1. In Lemon Squeezy → your product → **Share** → copy the **Checkout** URL.  
   Example shape: `https://yourstore.lemonsqueezy.com/checkout/buy/…`
2. On the VPS, add to repo-root `.env`:

```bash
MSOS_UPGRADE_OFFER_URL=https://yourstore.lemonsqueezy.com/checkout/buy/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

3. Recreate `msos_web`:

```bash
cd /opt/marketstructureos
docker compose up -d --force-recreate msos_web
```

4. Sign in on `https://marketstructureos.com` as a **free** user → sidebar shows **Request upgrade** → opens Lemon Squeezy checkout.

**Important:** Customer should pay with the **same email** they use for Cloudflare Access — webhooks match on `user_email`.

---

## Step 3 — Webhook (v1 — auto-grant paid tier)

1. Lemon Squeezy → **Settings → Webhooks → Create webhook**
2. **URL:** `https://marketstructureos.com/api/billing/lemon-squeezy/webhook`
3. **Signing secret:** generate a random string (6–40 chars) — save it.
4. **Events** (minimum):
   - `subscription_created`
   - `subscription_updated`
   - `subscription_expired`
   - `subscription_cancelled`
   - `subscription_payment_failed`
5. Add to VPS `.env`:

```bash
LEMONSQUEEZY_WEBHOOK_SECRET=your-signing-secret-here
```

6. Redeploy `msos_web` (same as step 2.3).

### Verify webhook

- Lemon Squeezy dashboard → webhook → **Send test** (or complete a test subscription in **Test mode**).
- VPS logs: `docker compose logs -f msos_web` — look for `lemon-squeezy webhook applied`.
- Confirm tier: signed-in user sidebar badge shows **Paid**, or call `/api/entitlements/me` behind Access.

---

## Step 4 — First real payment witness

Log in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md):

- Date, payer email, product name, webhook received (Y/N), tier flipped (Y/N).

---

## Env reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `MSOS_UPGRADE_OFFER_URL` | v0+ | Hosted checkout URL for free-tier upgrade CTA |
| `LEMONSQUEEZY_WEBHOOK_SECRET` | v1 | HMAC secret from LS webhook settings |

Both are **runtime** env on `msos_web` (see [`docker-compose.yml`](../../docker-compose.yml)). Never commit secrets.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No upgrade button | User must be `free` tier **and** `MSOS_UPGRADE_OFFER_URL` set |
| Paid but still Free in app | Email mismatch — LS `user_email` ≠ Access email; manual grant or refund/rebuy with correct email |
| Webhook 400 invalid signature | Secret mismatch; ensure raw secret in `.env`, redeploy |
| Webhook 503 | `LEMONSQUEEZY_WEBHOOK_SECRET` not set on container |

---

## Local dev smoke

```bash
# Terminal 1 — msos-web with dev identity + checkout URL
cd apps/msos-web
set MSOS_IDENTITY_DEV_ALLOW_ANON=1
set MSOS_IDENTITY_EMAIL=you@example.com
set MSOS_UPGRADE_OFFER_URL=https://yourstore.lemonsqueezy.com/checkout/buy/...
npm run dev

# Terminal 2 — simulate webhook (replace SECRET and payload file)
python - <<'PY'
import hashlib, hmac, json, urllib.request
secret = "YOUR_SECRET"
body = json.dumps({"meta":{"event_name":"subscription_created"},"data":{"type":"subscriptions","id":"sub_test","attributes":{"user_email":"you@example.com","customer_id":1,"status":"active"}}})
sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
req = urllib.request.Request("http://localhost:3000/api/billing/lemon-squeezy/webhook", data=body.encode(), headers={"Content-Type":"application/json","X-Signature":sig}, method="POST")
print(urllib.request.urlopen(req).read())
PY
```
