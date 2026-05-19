# Commercial ops completion — checklist

**Purpose:** Close operational gaps after Commercial Validation code/docs on `main` (no new product BUILD).

**Status:** **Agent lane COMPLETE** (2026-05-19). **SELECTION COMPLETE** → MVP1 Reliability — [`POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md`](POST_COMMERCIAL_OPS_SELECTION_OUTCOME.md).

**Baseline:** `main` after ops compose commit (verify with `git rev-parse HEAD` on VPS after deploy).

---

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| `git pull` on `main`; clean tree | done | pytest **153 passed** |
| `python -m pytest -q` green | done | 2026-05-19 |
| Fresh `run_mvp1_dual_implied_lab_smoke.py` | done | Post–Reliability Slice002: `20260519_133606` + `134906`; prior `131035` + `131251` |
| `docker-compose.yml` `PPE_RESEARCH_OFFER_*` on `app_demo` | done | `${PPE_RESEARCH_OFFER_URL:-}` / `LABEL` wired; [`.env.example`](../../.env.example) |
| Push `main` → GitHub Actions **Deploy VPS** | done | auto `git pull` + `docker compose up -d --build` on push |
| VPS repo-root `.env` with offer URL | **steward** | Required for CTA text on demo; compose passes empty if unset |
| Production browser: **Research beta (v0)** CTA | **steward** | After `.env` set; re-run `docker compose up -d` |
| Update [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) | done | Agent fetch + deploy trigger; CTA row pending steward `.env` |
| Live paid-interest conversation | **steward** | **N** — honest; outreach script below |
| **Ops completion (agent lane)** | done | |
| **SELECTION** | done | MVP1 Reliability chartered |

---

## Demo service env (VPS)

**1. Repo-root `.env` on VPS** (not committed):

```bash
PPE_RESEARCH_OFFER_URL=mailto:YOUR_EMAIL?subject=PPE%20research%20beta
PPE_RESEARCH_OFFER_LABEL=Request research beta access
```

**2. `docker-compose.yml`** — `app_demo.environment` includes:

```yaml
      - PPE_RESEARCH_OFFER_URL=${PPE_RESEARCH_OFFER_URL:-}
      - PPE_RESEARCH_OFFER_LABEL=${PPE_RESEARCH_OFFER_LABEL:-}
```

Then:

```bash
cd /opt/marketstructureos
git pull
docker compose up -d --build
```

---

## Outreach log

| Date | Contact | Offer | Y/N | Notes |
|------|---------|-------|-----|-------|
| 2026-05-19 | — | research beta | N | Ops + compose complete; **steward:** one live call using script below |

### Steward conversation script (paid-interest)

1. Open demo: `https://marketstructureos.com` — walk **MVP1 output** + disagreement readout (~5 min).
2. Offer (pick one): research beta access (`PPE_RESEARCH_OFFER_URL` CTA), weekly BTC brief, or paid discovery call.
3. Ask: willingness to pay for beta/brief/call this quarter; capture objection themes.
4. Log **Y/N** + one-line notes in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) and update the outreach table above.

**Do not log Y without a real conversation.**

---

## Smoke record

| Run ID | Exit | Classification | Notes |
|--------|------|----------------|-------|
| 20260519_133606 | 0 | deterministic | MVP1_compact (Reliability Slice002) |
| 20260519_134906 | 0 | deterministic | A_width_target_payoff (Reliability Slice002) |
| 20260519_131035 | 0 | deterministic | MVP1_compact (pre-Slice002) |
| 20260519_131251 | 0 | deterministic | A_width (pre-Slice002) |

---

## Next

**BUILD:** [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md) — Deploy-Slice003 (steward) then Closeout-Slice004. **SELECTION prep:** [`POST_MVP1_RELIABILITY_SELECTION.md`](POST_MVP1_RELIABILITY_SELECTION.md).

