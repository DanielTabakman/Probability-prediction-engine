# PPE forward consistency radar v1 — relay sprint spec

**Program:** [`FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md`](FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md`](POST_PPE_FORWARD_CONSISTENCY_RADAR_V1_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Aggregated **forward consistency dashboard** boundary — quality flags, heatmap payload, fixture — building on existing per-cell engine and API.

---

## Slice acceptance

### PPE-FCR-Control-Slice001 (CONTROL)

- SELECTION wired; evidence stub; phase plan registered

### PPE-FCR-Core-Slice002 (PPE_CORE)

- `quality_flags` on `ForwardConsistencyCheck`
- Matrix builder for enabled assets × expiries

### PPE-FCR-UI-Slice003 (PPE_UI)

- `GET /ppe-display-api/forward-consistency/dashboard.json`
- Fixture + boundary pytest

### PPE-FCR-Closeout-Slice004 (CONTROL)

- Evidence COMPLETE
- Update `PPE_MODULE_REGISTRY.json` tier → T1 complete; re-render HTML map

---

## Non-goals

- MSOS page (next chapter)
- Collector / archive (chapter 3 — requires archive charter)
