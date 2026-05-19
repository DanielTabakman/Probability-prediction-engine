# Commercial ops completion — checklist

**Purpose:** Close operational gaps after Commercial Validation code/docs on `main` (no new product BUILD).

**Baseline:** `main` @ **`132ac4f`** (verify with `git rev-parse HEAD` after pull).

---

## Checklist

| Step | Status | Notes |
|------|--------|-------|
| `git pull` on `main`; clean tree | pending | |
| `python -m pytest -q` green | pending | |
| Fresh `run_mvp1_dual_implied_lab_smoke.py` (record run_id) | pending | `PYTHONUNBUFFERED=1`; ~15–20 min |
| VPS `git pull` + `docker compose up -d --build` | pending | `/opt/marketstructureos` |
| VPS SHA matches expected `main` tip | pending | |
| Demo env: `PPE_ENABLE_SNAPSHOTS=0`, `PPE_PRIVATE_APP_URL`, `PPE_RESEARCH_OFFER_URL` | pending | See [`COMMERCIAL_VALIDATION_OPERATOR.md`](COMMERCIAL_VALIDATION_OPERATOR.md) |
| Production browser check: demo + offer CTA | pending | [`DEMO_UI_RELEASE_CHECKLIST.md`](DEMO_UI_RELEASE_CHECKLIST.md) §5 |
| Update [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md) | pending | |
| Live paid-interest conversation logged | pending | [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) |
| **Ops completion DONE** | pending | Then HANDOFF → **SELECTION** |

---

## Outreach log

| Date | Contact | Offer | Y/N | Notes |
|------|---------|-------|-----|-------|
| | | research beta | | |

---

## Smoke record

| Run ID | Exit | Classification | Artifact path |
|--------|------|----------------|---------------|
| | | | |

---

## Next after DONE

Steward **SELECTION** for next BUILD chapter — candidates in [`POST_VALIDATION_CHAPTER_SELECTION.md`](POST_VALIDATION_CHAPTER_SELECTION.md) deferred list (MVP1 hardening, Phase 2 on `main`, Sprint 003 evidence-plane).
