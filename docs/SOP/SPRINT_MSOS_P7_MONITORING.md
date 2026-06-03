# MSOS P7 — monitoring, history, calibration loop

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P7)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) — screens `06_monitor`, `07_history`, `08_updated_command`  
**Acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)  
**SELECTION:** [`POST_MSOS_P7_MONITORING_SELECTION.md`](POST_MSOS_P7_MONITORING_SELECTION.md)

---

## Sprint intent (P7)

Ship monitoring, history, and updated Command Center surfaces with **fixture state** for observed / saved / simulated / executed / reviewed distinctions. No undefined numerical thesis-health metrics.

## Preconditions (at SELECTION)

1. P6 expression planning **COMPLETE**.

## Acceptance

1. Routes for monitor, history, and updated Command Center aligned to storyboard PNGs `06`–`08`.
2. Separate thesis-validity, expression-risk, and data/trust monitoring panels (fixture copy OK).
3. Screenshot witnesses for all three PNGs; deviations logged at closeout.
4. **No** false Live data on deferred lenses.

## Not now

- Live execution monitoring tied to real fills.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P7-Control-Slice001** | EVIDENCE | CONTROL | Charter |
| **MSOS-P7-Product-Slice002** | PRODUCT | MSOS_UI | Three P7 screens + shell updates |
| **MSOS-P7-Witness-Slice004** | EVIDENCE | CONTROL | pytest + triple visual witness |
| **MSOS-P7-Closeout-Slice005** | EVIDENCE | CONTROL | Closeout |
