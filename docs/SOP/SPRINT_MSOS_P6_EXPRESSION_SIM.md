# MSOS P6 — expression planning + simulation only

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P6)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) — screen `05_execution`  
**Acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)  
**SELECTION:** [`POST_MSOS_P6_EXPRESSION_SIM_SELECTION.md`](POST_MSOS_P6_EXPRESSION_SIM_SELECTION.md)

---

## Sprint intent (P6)

Expression planning UI aligned to `05_execution`: optimized expression plan as **best fit under constraints**, simulation/save only. Hyperliquid **Pending** unless honestly implemented later.

## Preconditions (at SELECTION)

1. P5 thesis confirmation **COMPLETE** (confirmed thesis can be loaded or mocked).

## Acceptance

1. Compare expression families; show suggested plan with assumptions visible.
2. Distinguish thesis fit, expression fit, edge-estimate status, execution availability.
3. **No live order placement.**
4. Screenshot witness vs `prototype/screens/05_execution.png`.

## Not now

- Live execution rails.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P6-Control-Slice001** | EVIDENCE | CONTROL | Charter |
| **MSOS-P6-Product-Slice002** | PRODUCT | MSOS_UI | Expression planning + sim-only save |
| **MSOS-P6-Witness-Slice004** | EVIDENCE | CONTROL | Witness |
| **MSOS-P6-Closeout-Slice005** | EVIDENCE | CONTROL | Closeout |
