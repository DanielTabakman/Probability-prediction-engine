# Validation / production deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-05-19 (pre–ops re-verify); update after VPS pull |
| **Git SHA on VPS** | `132ac4f` — **re-verify** on VPS after `git pull` (Commercial Validation + smoke logging) |
| **Deploy path** | GitHub Actions on push to `main` / manual §4 |
| **marketstructureos.com** | PASS — demo loads (agent fetch 2026-05-19); re-check after deploy |
| **app.marketstructureos.com** | PASS — Cloudflare Access gate (**App full (snapshots)**) |
| **HTTPS static assets** | PASS — no mixed-content on demo fetch |
| **Demo operator script** | PASS — prep; re-run after offer CTA env on demo service |
| **Research offer CTA on demo** | pending — requires `PPE_RESEARCH_OFFER_URL` on demo container |

**Post–Commercial Validation:** Re-run checklist §5 after VPS aligns to `132ac4f`+ and demo env sets `PPE_RESEARCH_OFFER_URL`. Log result in [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md).
