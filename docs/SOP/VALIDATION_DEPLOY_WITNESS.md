# Validation / production deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-05-19 |
| **Git SHA on VPS** | Expect tip after **Deploy VPS** on `main` push (compose `PPE_RESEARCH_OFFER_*`); verify: `cd /opt/marketstructureos && git rev-parse HEAD` |
| **Deploy path** | GitHub Actions **Deploy VPS** on push to `main` + manual SSH per runbook §4 |
| **marketstructureos.com** | PASS — demo loads (agent fetch 2026-05-19 post-push) |
| **app.marketstructureos.com** | PASS — Cloudflare Access gate (**App full (snapshots)**) |
| **HTTPS static assets** | PASS — no mixed-content on demo fetch |
| **Demo operator script** | PASS — prep |
| **Research offer CTA on demo** | **pending steward `.env`** — compose wires `${PPE_RESEARCH_OFFER_URL:-}`; CTA appears only when repo-root `.env` sets URL on VPS |

**Agent lane (2026-05-19):** `docker-compose.yml` offer env merged to `main`; auto-deploy runs `git pull` + `docker compose up -d --build`. **Steward:** set `.env` on VPS, confirm **Research beta (v0)** in browser, update SHA in this table.

**Post–Commercial Validation:** See [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md).
