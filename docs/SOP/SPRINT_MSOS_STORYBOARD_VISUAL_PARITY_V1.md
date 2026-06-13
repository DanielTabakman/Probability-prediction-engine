# MSOS storyboard visual parity v1

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (post-P8 follow-on)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md)  
**Acceleration debt closed:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md) §2.1, P2–P8 deferred pixel witnesses  
**SELECTION:** [`POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md`](POST_MSOS_STORYBOARD_VISUAL_PARITY_V1_SELECTION.md)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Close the gap between **storyboard v0.6 pictures** and **`apps/msos-web/`** as rendered in the browser. P2–P8 shipped narrative + route parity with pixel witnesses **explicitly deferred**; this chapter makes visual parity the acceptance bar.

**Non-widening:** MSOS remains display/proxy only. Streamlit PPE interior unchanged unless embed chrome/frame is part of storyboard shell.

---

## Preconditions

1. MSOS P8 **COMPLETE** (routes exist).
2. Storyboard HTML/CSS in-repo (witness source when PNGs absent from lean zip).
3. `mvp1_distribution_quant_research_v2` **COMPLETE** before auto-select (current LOW chapter finishes first).

---

## Acceptance

1. Each screen `01`–`09` matches storyboard layout within **material deviation** rules (spacing, typography, panel hierarchy, nav/sidebar chrome — not literal pixel diff on responsive breakpoints).
2. Evidence doc screenshot checkboxes **checked** with operator or BUILD captures.
3. Shared tokens in `apps/msos-web/src/app/globals.css` trace to storyboard `style.css` variables; no generic unthemed component library defaults.
4. Deploy checklist completed or honestly marked blocked with reason.
5. `npm run build` + existing MSOS web tests green.

## Hard visual closeout

Per [`OPERATING_RULES.md`](OPERATING_RULES.md): side-by-side witness of **each changed UI region** vs storyboard HTML prototype before slice close. Waiving a screen requires written deviation in evidence doc.

## Not now

- PPE distribution math in TypeScript
- Unified host at `app.*` (ADR keeps Streamlit on `app.*`; document in platform slice)
- Paywall, live execution, or auth server expansion

---

## Screen → route map

| Storyboard | HTML prototype | Next route |
|------------|----------------|------------|
| `01_home` | `01_home.html` | `/` |
| `02_command_center` | `02_command_center.html` | `/command-center` |
| `03_ppe_lab` | `03_ppe_lab.html` | `/strategy-lab` |
| `04_confirmation` | `04_confirmation.html` | `/strategy-lab/confirm` |
| `05_execution` | `05_execution.html` | `/strategy-lab/expression` |
| `06_monitor` | `06_monitor.html` | `/monitor` |
| `07_history` | `07_history.html` | `/history` |
| `08_updated_command` | `08_updated_command.html` | `/command-center` (calibration strip) |
| `09_conclusion` | `09_conclusion.html` | `/learn` |

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-VisParityV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + witness checklist |
| **MSOS-VisParityV1-Product-Slice002** | PRODUCT | MSOS_UI | Homepage parity (`01_home`) |
| **MSOS-VisParityV1-Product-Slice003** | PRODUCT | MSOS_UI | App shell + Command Center (`02`, `08`) |
| **MSOS-VisParityV1-Product-Slice004** | PRODUCT | MSOS_UI | Strategy Lab chrome (`03`) |
| **MSOS-VisParityV1-Product-Slice005** | PRODUCT | MSOS_UI | Thesis + expression (`04`, `05`) |
| **MSOS-VisParityV1-Product-Slice006** | PRODUCT | MSOS_UI | Monitor, history, learn (`06`, `07`, `09`) |
| **MSOS-VisParityV1-Platform-Slice007** | EVIDENCE | PLATFORM | VPS deploy + routing docs |
| **MSOS-VisParityV1-Witness-Slice008** | EVIDENCE | CONTROL | Screenshot witness + pytest |
| **MSOS-VisParityV1-Closeout-Slice009** | EVIDENCE | CONTROL | Chapter close |
