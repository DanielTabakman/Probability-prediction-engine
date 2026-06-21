# MSOS production deploy refresh v1 — evidence status

**Chapter:** `msos_production_deploy_refresh_v1`  
**Priority:** HIGH  
**Status:** **BLOCKED** — awaits `msos_usable_demo_v1` COMPLETE  
**Phase plan:** [`PHASE_PLANS/msos_production_deploy_refresh_v1_relay.json`](PHASE_PLANS/msos_production_deploy_refresh_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_PRODUCTION_DEPLOY_REFRESH_V1.md`](SPRINT_MSOS_PRODUCTION_DEPLOY_REFRESH_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-ProdDeployV1-Control-Slice001 | BLOCKED | Charter — after usable demo |
| MSOS-ProdDeployV1-Platform-Slice002 | BLOCKED | Deploy docs + platform witness |
| MSOS-ProdDeployV1-Witness-Slice003 | BLOCKED | Production HTTP witness |
| MSOS-ProdDeployV1-Closeout-Slice004 | BLOCKED | Chapter COMPLETE |

## Production witness (required at closeout)

| Check | Witness |
|-------|---------|
| All storyboard routes HTTP 200 on apex | [ ] |
| `research_beta_cta` witness PASS | [ ] |
| PPE embed loads on `/strategy-lab` | [ ] |
| VPS image matches post-usable-demo `main` | [ ] |
| Operator sign-off in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) | [ ] |
