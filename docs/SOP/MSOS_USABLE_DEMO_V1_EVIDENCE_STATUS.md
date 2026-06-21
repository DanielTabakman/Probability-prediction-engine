# MSOS usable demo v1 — evidence status

**Chapter:** `msos_usable_demo_v1`  
**Display name:** MSOS shell + PPE usable demo — storyboard BUILD  
**Priority:** P0  
**Status:** **IN PROGRESS** — SELECTION 2026-06-21 (direction pivot `usable-demo-build-v1`)  
**Phase plan:** [`PHASE_PLANS/msos_usable_demo_v1_relay.json`](PHASE_PLANS/msos_usable_demo_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_USABLE_DEMO_V1.md`](SPRINT_MSOS_USABLE_DEMO_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-UsableDemoV1-Control-Slice001 | **CLOSED** | Charter + direction align |
| MSOS-UsableDemoV1-Product-Slice002 | **DONE** | PPE display boundary + WSGI display API |
| MSOS-UsableDemoV1-Product-Slice003 | **DONE** | MSOS chart shell — storyboard `03_ppe_lab` |
| MSOS-UsableDemoV1-Witness-Slice004 | PENDING | pytest + operator demo walkthrough |
| MSOS-UsableDemoV1-Closeout-Slice005 | PENDING | Chapter COMPLETE |

## Visual witness (required at closeout)

Reference: [`docs/VISION/MSOS/storyboard-v0.6/prototype/html/`](../VISION/MSOS/storyboard-v0.6/prototype/html/)

| Screen | Route | Witness |
|--------|-------|---------|
| `01_home` | `/` | [ ] |
| `02_command_center` | `/command-center` | [ ] |
| `03_ppe_lab` | `/strategy-lab` | [ ] |
| `04_confirmation` | `/strategy-lab/confirm` | [ ] |
| `05_execution` | `/strategy-lab/expression` | [ ] |
| `06_monitor` | `/monitor` | [ ] |
| `07_history` | `/history` | [ ] |
| `09_conclusion` | `/learn` | [ ] |

## PPE integration checks

| Check | Route | Witness |
|-------|-------|---------|
| No full Streamlit app chrome inside MSOS chart panel | `/strategy-lab` | [ ] |
| Chart region layout matches storyboard hierarchy | `/strategy-lab` | [ ] |
| PPE math authoritative from Python | `/strategy-lab` | [ ] |
| Honest Live/degraded labels | `/strategy-lab` | [ ] |

## Operator check-in (required at closeout)

- [ ] Production URL demo walkable per [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)
- [ ] No friends-first cohort gate required before sharing demo URL
- [ ] Log optional validation row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) when ready
