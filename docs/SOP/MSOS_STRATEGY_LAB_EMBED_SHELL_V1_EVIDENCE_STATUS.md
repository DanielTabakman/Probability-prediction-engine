# MSOS Strategy Lab embed shell v1 — evidence status

**Chapter:** `msos_strategy_lab_embed_shell_v1`  
**Display name:** Strategy Lab PPE embed shell — storyboard chart region  
**Priority:** MEDIUM  
**Status:** **CHARTERED** 2026-06-18 — blocked until `msos_workflow_persistence_v1` COMPLETE  
**Phase plan:** [`PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json`](PHASE_PLANS/msos_strategy_lab_embed_shell_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-EmbedShellV1-Control-Slice001 | PENDING | Charter + queue align |
| MSOS-EmbedShellV1-Product-Slice002 | PENDING | PPE read-only display boundary |
| MSOS-EmbedShellV1-Product-Slice003 | PENDING | MSOS chart shell (`03_ppe_lab`) |
| MSOS-EmbedShellV1-Platform-Slice004 | PENDING | Caddy/compose/deploy docs |
| MSOS-EmbedShellV1-Witness-Slice005 | PENDING | pytest + visual witness |
| MSOS-EmbedShellV1-Closeout-Slice006 | PENDING | Chapter COMPLETE |

## Visual witness (required at closeout)

Reference: [`docs/VISION/MSOS/storyboard-v0.6/prototype/html/03_ppe_lab.html`](../VISION/MSOS/storyboard-v0.6/prototype/html/03_ppe_lab.html)

| Check | Route | Witness |
|-------|-------|---------|
| No full Streamlit app chrome inside MSOS chart panel | `/strategy-lab` | [ ] |
| Chart region layout matches storyboard hierarchy | `/strategy-lab` | [ ] |
| Belief builder + outcome panel remain MSOS-native | `/strategy-lab` | [ ] |
| Honest Live/degraded labels when PPE upstream unavailable | `/strategy-lab` | [ ] |

Material deviations (e.g. API-rendered SVG vs static storyboard SVG) must be listed here before closeout.

## Operator check-in (required at closeout)

- [ ] `/strategy-lab` — single cohesive MSOS surface; no nested “old site” sidebar inside chart panel
- [ ] Distribution data still authoritative from Python (witness schema or embed-only path in evidence)
- [ ] `app.marketstructureos.com` full Streamlit lab unchanged
- [ ] Log row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) if demo-ready
