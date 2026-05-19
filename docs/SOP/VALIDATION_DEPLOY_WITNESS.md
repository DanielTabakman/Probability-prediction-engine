# Validation / production deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-05-19 |
| **Git SHA on VPS** | Verify `cd /opt/marketstructureos && git rev-parse HEAD` (expect `main` ≥ ops compose + reliability smoke commits) |
| **Deploy path** | GitHub Actions **Deploy VPS** on push to `main` |
| **marketstructureos.com** | PASS — demo loads (agent fetch 2026-05-19) |
| **app.marketstructureos.com** | PASS — Cloudflare Access gate (**App full (snapshots)**) |
| **HTTPS static assets** | PASS |
| **Demo operator script** | PASS |
| **Research offer CTA on demo** | **pending steward `.env`** — `docker-compose.yml` wires `${PPE_RESEARCH_OFFER_URL:-}`; CTA renders only when repo-root `.env` sets URL on VPS |

**Reliability Slice002 (local):** dual smoke green `20260519_133606` + `20260519_134906` — see [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md).

**Steward (Deploy-Slice003):**

```bash
cd /opt/marketstructureos
git pull
# create/edit .env:
#   PPE_RESEARCH_OFFER_URL=mailto:...
#   PPE_RESEARCH_OFFER_LABEL=Request research beta access
docker compose up -d --build
```

Browser: confirm **Research beta (v0)** on [marketstructureos.com](https://marketstructureos.com) → set CTA row **PASS** and record VPS SHA above.

**Tracker:** [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md)
