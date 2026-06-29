# PPE Exposure menu v1 — sprint

**Controlling canon:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**SELECTION:** [`POST_PPE_EXPOSURE_MENU_V1_SELECTION.md`](POST_PPE_EXPOSURE_MENU_V1_SELECTION.md)  
**Module registry:** [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md)

---

## Sprint intent

Ship **Exposure menu** v0: asset + direction → ranked **ExposurePath** cards. Standalone `/exposure` route. NVDA + BTC proof. Simulation-only copy.

---

## Preconditions (at SELECTION → READY)

1. [`config/exposure_path_catalog.yaml`](../../config/exposure_path_catalog.yaml) merged.
2. NVDA + BTC enabled in registry with live spot/options fetch.

---

## Acceptance

1. CLI + boundary API return consistent JSON for NVDA and BTC.
2. MSOS page renders card grid without PPE math in TypeScript.
3. Sort: simplest paths first (spot before aggressive OTM).
4. Options paths deep-link to `/strategy-lab?asset=`.
5. Pytest with mocked chains; no live network in CI.
6. Gate green.

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **PPE-ExposureMenu-Control-Slice001** | EVIDENCE | CONTROL | Evidence stub, relay wired, program linked |
| **PPE-ExposureMenu-Core-Slice002** | PRODUCT | PPE_CORE | `exposure_paths.py`, `exposure_path_core.py`, catalog loader |
| **PPE-ExposureMenu-CLI-Slice003** | PRODUCT | PPE_CORE | `find_exposure_paths.py` + tests |
| **PPE-ExposureMenu-UI-Slice004** | PRODUCT | PPE_UI | `exposure_menu_boundary.py`, embed route, fixture |
| **PPE-ExposureMenu-Product-Slice005** | PRODUCT | MSOS_UI | `/exposure` page, secondary nav, integration tests |
| **PPE-ExposureMenu-Closeout-Slice006** | EVIDENCE | CONTROL | COMPLETE; registry + module map |

---

## Not now

- Natural language parser
- Workflow persistence
- Perp / ETF proxy live math
- Archive collector

---

## Focus playbook

- **Priority tier:** P1
- **Drift guards:** No execution language; no “recommended trade”; Planned rails labeled honestly
