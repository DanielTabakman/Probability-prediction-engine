# MSOS storyboard gate (P2+)

**Purpose:** Block visible MSOS UI BUILD until approved visual reference exists in-repo.

## Requirement (from PPE Master waterfall)

Before **P2 — Design system + public MSOS homepage** or any user-facing visual implementation:

1. Place **Market Structure OS Website Storyboard v0.6** assets in-repo (PDF, montage, or equivalent screen exports).
2. Preferred path: `docs/VISION/MSOS/storyboard-v0.6/` (create when assets arrive).
3. Record asset manifest in this file (filename list + import date).

## Current status

| Field | Value |
|-------|--------|
| **Gate** | **OPEN** |
| **Imported** | 2026-06-02 |
| **Path** | [`docs/VISION/MSOS/storyboard-v0.6/`](MSOS/storyboard-v0.6/) |
| **Manifest** | [`docs/VISION/MSOS/storyboard-v0.6/MANIFEST.md`](MSOS/storyboard-v0.6/MANIFEST.md) |
| **Blocks** | ~~P2 storyboard absence~~ — P2 may proceed after steward SELECTION + relay plan |
| **Still blocked** | P3–P8 until prior MSOS chapters ship (see [`MSOS_FRONTIER.md`](../SOP/MSOS_FRONTIER.md)) |

### Installed files (lean)

- `Market_Structure_OS_Website_Storyboard_v0.6.pdf`
- `Market_Structure_OS_Website_Storyboard_v0.6.pptx`
- `MSOS_Website_Storyboard_v0.6_montage.png`
- `semantics/MSOS_Product_Semantics_State_Model_v0.1.md`
- `prototype/html/` — 9 HTML screens + `style.css`
- `prototype/screens/` — `01_home.png` … `09_conclusion.png`

## Unblock procedure (completed 2026-06-02)

1. ~~Operator drops storyboard files under `docs/VISION/MSOS/storyboard-v0.6/`.~~ **Done**
2. ~~Update this file: set gate **OPEN**, list files, date.~~ **Done**
3. **Next:** Steward SELECTION — `msos_p2_homepage` is `queued` in [`PHASE_CHAPTER_BACKLOG.json`](../SOP/PHASE_CHAPTER_BACKLOG.json); add relay plan / scaffold before `run_ppe.cmd` auto-select.

## Screenshot witness (ongoing)

For each major finished visual surface after P2+, include screenshot witness in chapter evidence doc and note material deviations in closeout.
