# PPE forward consistency radar v1 — relay sprint spec

**SELECTION:** [`POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md)  
**Program:** [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**Baseline:** **`main`**

## Sprint intent

Extend the forward-consistency engine with **quality flags** and a **dashboard payload** so MSOS can render a heatmap from one API call.

## Slices

| Slice | Delivers |
|-------|----------|
| PPE-FCR-Control-Slice001 | Charter + evidence stub |
| PPE-FCR-Core-Slice002 | Quality flags, matrix builder |
| PPE-FCR-UI-Slice003 | `dashboard.json` route + fixture + tests |
| PPE-FCR-Closeout-Slice004 | Evidence COMPLETE |

## Contracts

- Extend `ForwardConsistencyCheck` — do not fork parallel types.
- `GET /ppe-display-api/forward-consistency/dashboard.json`
- Fixture: `fixtures/forward_consistency_dashboard_v1.json`
