# Commercial ops completion — checklist

**Purpose:** Close operational gaps after Commercial Validation code/docs on `main` (no new product BUILD).

**Baseline:** `main` @ **`132ac4f`** (or merge commit with ops cleanup — verify `git rev-parse HEAD`).

---

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| `git pull` on `main`; clean tree | done | pytest **153 passed** on branch with ops docs |
| `python -m pytest -q` green | done | 2026-05-19 |
| Fresh `run_mvp1_dual_implied_lab_smoke.py` | done | `20260519_131035` + `131251`; exit **0**; deterministic |
| VPS `git pull` + `docker compose up -d --build` | **steward** | `/opt/marketstructureos` — agent cannot SSH |
| VPS SHA matches `main` tip | **steward** | Expect `132ac4f`+ after pull |
| Demo env: `PPE_RESEARCH_OFFER_*` on demo service | **steward** | See env block below |
| Production browser: demo + offer CTA | partial | `marketstructureos.com` loads (2026-05-19 fetch); offer CTA needs env on VPS |
| Update [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) | done | Re-verify row after VPS pull |
| Live paid-interest conversation | **steward** | Log in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md); next outreach scheduled below |
| **Ops completion (agent lane)** | done | Engineering + docs; VPS/outreach = steward |

---

## Demo service env (VPS)

```bash
PPE_ENABLE_SNAPSHOTS=0
PPE_PRIVATE_APP_URL=https://app.marketstructureos.com
PPE_RESEARCH_OFFER_URL=mailto:YOUR_EMAIL?subject=PPE%20research%20beta
# optional: PPE_RESEARCH_OFFER_LABEL=Request research beta access
```

Set in demo container compose/env, then `docker compose up -d --build`.

---

## Outreach log

| Date | Contact | Offer | Y/N | Notes |
|------|---------|-------|-----|-------|
| 2026-05-19 | — | research beta | N | Ops prep complete; **schedule first live call** per [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md) |

**Next outreach target:** steward calendar — one conversation required for paid-interest **Y**.

---

## Smoke record

| Run ID | Exit | Classification | Notes |
|--------|------|----------------|-------|
| 20260519_131035 | 0 | deterministic | MVP1_compact_verification |
| 20260519_131251 | 0 | deterministic | A_width_target_payoff |

---

## Next after steward VPS + outreach

**SELECTION** for next BUILD chapter — see [`POST_COMMERCIAL_OPS_SELECTION.md`](POST_COMMERCIAL_OPS_SELECTION.md).
