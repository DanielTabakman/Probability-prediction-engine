# MSOS forward consistency radar v1 — relay sprint spec

**SELECTION:** [`POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_MSOS_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md)  
**Program:** [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**Baseline:** **`main`** (after ch.1 merged)

## Sprint intent

Operator-facing **`/forward-consistency`** dashboard — summary, heatmap, detail, debug drawer — consuming PPE `dashboard.json`.

## Slices

| Slice | Delivers |
|-------|----------|
| MSOS-FCR-Control-Slice001 | Charter |
| MSOS-FCR-Product-Slice002 | Page, heatmap, detail panel, nav hook |
| MSOS-FCR-Closeout-Slice003 | Evidence COMPLETE |

## v0 views

- Summary cards (assets checked, watch/possible/bad-data counts)
- Heatmap grid (asset × expiry)
- Selected cell detail + deep-link to Strategy Lab `?asset=&expiry=`
- Raw JSON drawer (ops)
