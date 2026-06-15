# MSOS monitor & history live v1

**Display name:** Monitor + History + updated Command Center · **chapterId:** `msos_monitor_history_live_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 5) · storyboard `06_monitor`, `07_history`, `08_updated_command`  
**Prior chapter:** [`SPRINT_MSOS_ACCESS_IDENTITY_V1.md`](SPRINT_MSOS_ACCESS_IDENTITY_V1.md)  
**SELECTION:** [`POST_MSOS_MONITOR_HISTORY_LIVE_V1_SELECTION.md`](POST_MSOS_MONITOR_HISTORY_LIVE_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Replace **fixture** Monitor, History, and calibration strip on Command Center with **live MSOS workflow + PPE review state** — completing P7 intent for real data. Honest observed/saved/simulated/reviewed distinctions per semantics model.

---

## Preconditions

1. `msos_access_identity_v1` **COMPLETE**.
2. P7 routes exist on `main` with fixture components.

---

## Acceptance

1. `/monitor` watch panels and alerts from MSOS + snapshot review metadata (scoped by user).
2. `/history` timeline from combined workflow + review rows; **Executed** empty until live routing exists.
3. Command Center calibration strip reflects real review-due / return hooks.
4. No false Live claims on deferred lenses.
5. Pytest + screenshot witness vs storyboard `06`/`07`/`08` (material deviation rules).

## Not now

- Live execution feed
- Undefined thesis-health metrics

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-MonHistV1-Control-Slice001** | EVIDENCE | CONTROL | Charter |
| **MSOS-MonHistV1-Product-Slice002** | PRODUCT | MSOS_UI | Monitor + History + CC strip live |
| **MSOS-MonHistV1-Witness-Slice003** | EVIDENCE | CONTROL | pytest + visual witness |
| **MSOS-MonHistV1-Closeout-Slice004** | EVIDENCE | CONTROL | Close |
