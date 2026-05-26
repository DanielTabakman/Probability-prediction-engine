# Validation / production deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-05-20 (PR #10 belief-input + relay bundle merged; Deploy VPS re-run) |
| **Git SHA on VPS** | **`aff44c5`**+ (squash merge #10 on `main`); steward verify: `cd /opt/marketstructureos && git rev-parse HEAD` after [Deploy VPS run 26146497234](https://github.com/DanielTabakman/Probability-prediction-engine/actions/runs/26146497234) **success** |
| **Deploy path** | GitHub Actions **Deploy VPS** on push to `main` |
| **marketstructureos.com** | PASS — demo loads (agent fetch 2026-05-20; page title Streamlit) |
| **app.marketstructureos.com** | PASS — Cloudflare Access gate (**App full (snapshots)**) |
| **HTTPS static assets** | PASS |
| **Demo operator script** | PASS |
| **Research offer CTA on demo** | **pending steward `.env`** — compose on `main`; set **PASS** after VPS `.env` + browser confirms **Research beta (v0)** |

**Phase 2 (local):** dual smoke green `20260519_155858` + `20260519_160103` — [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md).

**Operator hardening:** see [`MVP1_OPERATOR_EVIDENCE_STATUS.md`](MVP1_OPERATOR_EVIDENCE_STATUS.md) after Smoke-Slice002 witness.

**Reliability Slice002 (local):** dual smoke green `20260519_133606` + `20260519_134906` — [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md).

**Steward follow-up:** set `.env` below → `docker compose up -d --build` → set CTA row **PASS** after browser confirms **Research beta (v0)**.

```bash
cd /opt/marketstructureos
git pull
# .env (not committed):
#   PPE_RESEARCH_OFFER_URL=mailto:...
#   PPE_RESEARCH_OFFER_LABEL=Request research beta access
docker compose up -d --build
```

**Tracker:** [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) · **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
