# Options Horizon region workflow v1 — relay sprint spec

**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**SELECTION:** [`POST_OPTIONS_HORIZON_REGION_WORKFLOW_V1_SELECTION.md`](POST_OPTIONS_HORIZON_REGION_WORKFLOW_V1_SELECTION.md)  
**Prior chapter:** [`SPRINT_OPTIONS_HORIZON_CHART_POLISH_V1.md`](SPRINT_OPTIONS_HORIZON_CHART_POLISH_V1.md) (must be COMPLETE)  
**Baseline:** **`main`**

---

## Sprint intent

Persist **RegionIntent** to MSOS user workflow store (`kind: "horizon_region"`) instead of browser `localStorage` only.

**Priority:** LOW / P2 — after chart polish.

---

## Slice acceptance

### Horizon-RegionWf-Control-Slice001 (CONTROL)

- Evidence stub + relay plan reference

### Horizon-RegionWf-Product-Slice002 (MSOS_UI)

- API route or extend `/api/theses` for horizon region CRUD
- Client `horizonRegion.ts` → server round-trip with localStorage fallback
- Deep-link `region_id` support on Strategy Lab entry

### Horizon-RegionWf-Closeout-Slice003 (CONTROL)

- Evidence COMPLETE

---

## Witness (chapter close)

- [ ] Save region → reload page → region restored for signed-in user
- [ ] Anonymous / offline still works via localStorage fallback
- [ ] No execution copy introduced
