# Validation / production deploy witness (steward fill)

Record post-deploy smoke after **`main`** merge per [DEMO_UI_RELEASE_CHECKLIST.md](DEMO_UI_RELEASE_CHECKLIST.md) §5.

| Field | Value |
|-------|--------|
| **Date (UTC)** | 2026-07-06 (MSOS storyboard visual parity deploy witness refresh) |
| **Git SHA on VPS** | steward verify: `cd /opt/marketstructureos && git rev-parse HEAD` after latest **Deploy VPS** |
| **Deploy path** | GitHub Actions **Deploy VPS** on push to `main` |
| **marketstructureos.com (apex)** | **PASS** — Next.js MSOS homepage; storyboard routes `/`, `/command-center`, `/strategy-lab`, `/strategy-lab/confirm`, `/strategy-lab/expression`, `/monitor`, `/history`, and `/learn` HTTP 200 via `Invoke-WebRequest`; apex includes `_next/static` and no Streamlit markers |
| **app.marketstructureos.com** | PASS — Cloudflare Access gate (**App full (snapshots)**); HTTP 200 with Access signals |
| **HTTPS static assets** | PASS |
| **Demo operator script** | PASS |
| **Research offer CTA on demo (`app_demo`)** | **pending steward `.env`** — Streamlit demo banner |
| **Research offer CTA on apex (`msos_web`)** | **pending** — run `bash scripts/vps_enable_research_cta.sh <email>` on VPS after `git pull` |
| **PPE embed on Strategy Lab (`msos_web`)** | **PASS** — `/strategy-lab` HTTP 200 and `/ppe-display-api/display.json` HTTP 200 with `spot_usd` |

**2026-07-06 tooling warning:** local Python HTTPS witnesses (`verify_msos_web_ship.py`, `msos_production_demo_witness.py`) failed with `CERTIFICATE_VERIFY_FAILED: certificate has expired`. Windows HTTPS requests succeeded for apex routes and `app.*`; treat this as a local Python certificate-path follow-up, not a deploy-route failure.

**Phase 2 (local):** dual smoke green `20260519_155858` + `20260519_160103` — [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md).

**Operator hardening:** see [`MVP1_OPERATOR_EVIDENCE_STATUS.md`](MVP1_OPERATOR_EVIDENCE_STATUS.md) after Smoke-Slice002 witness.

**Reliability Slice002 (local):** dual smoke green `20260519_133606` + `20260519_134906` — [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md).

**Steward follow-up:** enable apex research CTA on VPS:

```bash
cd /opt/marketstructureos
git pull
bash scripts/vps_enable_research_cta.sh YOUR_EMAIL@example.com
```

Or manual `.env` + rebuild per [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md). Re-run `msos_production_demo_witness.cmd` until `research_beta_cta` passes.

**Tracker:** [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md) · **Integrated status:** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
