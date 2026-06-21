# MSOS production deploy refresh v1

**Controlling canon:** [`PRODUCTION_DEPLOY_PROTOCOL.md`](PRODUCTION_DEPLOY_PROTOCOL.md) · [`MSOS_PRODUCTION_LIVE_HOOKUP_V1.md`](MSOS_PRODUCTION_LIVE_HOOKUP_V1.md)  
**SELECTION:** [`POST_MSOS_PRODUCTION_DEPLOY_REFRESH_V1_SELECTION.md`](POST_MSOS_PRODUCTION_DEPLOY_REFRESH_V1_SELECTION.md)  
**Priority:** **HIGH** — production URLs match `main` after usable demo BUILD  
**Baseline:** **`main`**

---

## Sprint intent

After [`msos_usable_demo_v1`](SPRINT_MSOS_USABLE_DEMO_V1.md) merges, ensure **marketstructureos.com** runs the latest MSOS + PPE stack — not stale VPS image or missing env.

**Operator goal:** Deploy witness PASS on production URLs; research beta CTA + embed path verified; operator sign-off row in validation log.

**Non-goals:** Stripe billing; apex Cloudflare Access expansion (Track B); new product features.

---

## Preconditions

1. `msos_usable_demo_v1` **COMPLETE** — integration BUILD merged to `main`
2. [`deploy-vps.yml`](../.github/workflows/deploy-vps.yml) or operator SSH deploy path documented

---

## Acceptance

1. **Deploy path documented** — [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md) reflects post-usable-demo operator steps.
2. **Witness PASS** — `msos_production_demo_witness.cmd` (or pytest equivalent) passes on production URLs.
3. **Env checklist** — research CTA, embed URL, sign-in URL documented for VPS `.env`.
4. **Evidence signed** — operator check-in row in evidence doc + optional [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).

---

## Relay slices (summary)

| Slice | Plane | Intent |
|-------|-------|--------|
| `MSOS-ProdDeployV1-Control-Slice001` | EVIDENCE | Charter + queue align |
| `MSOS-ProdDeployV1-Platform-Slice002` | EVIDENCE | Deploy docs + compose/Caddy witness updates |
| `MSOS-ProdDeployV1-Witness-Slice003` | EVIDENCE | Production HTTP witness + validation log |
| `MSOS-ProdDeployV1-Closeout-Slice004` | EVIDENCE | Chapter COMPLETE + steering sync |

---

## Carry docs

- [`PRODUCTION_DEPLOY_PROTOCOL.md`](PRODUCTION_DEPLOY_PROTOCOL.md)
- [`VALIDATION_DEPLOY_WITNESS.md`](VALIDATION_DEPLOY_WITNESS.md)
- [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)
