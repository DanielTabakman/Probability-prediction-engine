# MSOS Website Storyboard v0.6 — in-repo manifest

**Imported:** 2026-06-02  
**Gate:** [`MSOS_STORYBOARD_GATE.md`](../../MSOS_STORYBOARD_GATE.md) — **OPEN**  
**Source package:** `MSOS_ACTIVE_VISUAL_ASSETS_FOR_REPO` (operator zip; lean install)

## Canonical purpose

Approved visual reference for MSOS P2+ (public homepage, Command Center, Strategy Lab shell). Governs **visual intent** only; product/capability truth remains in [`PPE_MASTER_MVP1.md`](../../PPE_MASTER_MVP1.md) and repo steering docs.

**Hierarchy (do not invert):** MSOS (platform) → Command Center → Strategy Lab → PPE (first tool) → BTC options as first enabled PPE surface.

## File inventory

| Path | Role |
|------|------|
| `Market_Structure_OS_Website_Storyboard_v0.6.pdf` | Full journey viewing artifact |
| `Market_Structure_OS_Website_Storyboard_v0.6.pptx` | Editable/render source |
| `MSOS_Website_Storyboard_v0.6_montage.png` | One-image overview |
| `semantics/MSOS_Product_Semantics_State_Model_v0.1.md` | Product semantics + lifecycle + Cursor build rules |
| `prototype/html/*.html`, `prototype/html/style.css` | Static HTML reference (open locally; not production app) |
| `prototype/screens/01_home.png` … `09_conclusion.png` | Per-screen PNG witnesses |

**Omitted from zip (lean):** nested `Market_Structure_OS_Website_Prototype_v0.6.zip`, duplicate `page-N.png` names, per-screen PDFs (covered by full PDF).

## Screen map (P2–P8 alignment)

| Screen | File stem | MSOS program ref |
|--------|-----------|------------------|
| Public homepage | `01_home` | P2 |
| Command Center | `02_command_center` | P3 |
| Strategy Lab / PPE | `03_ppe_lab` | P4 |
| Thesis confirmation | `04_confirmation` | P5 |
| Expression planning | `05_execution` | P6 |
| Monitoring | `06_monitor` | P7 |
| History | `07_history` | P7 |
| Updated Command Center | `08_updated_command` | P7 |
| Conclusion / learn loop | `09_conclusion` | P8 |

## Future lens display rule (post–v0.6 screens)

Screens predate final lens hardening. Implementation must extend the same aesthetic with:

- **Prediction Markets:** muted/disabled — `Coming Soon` or `Planned` only  
- **Perpetual Positioning:** muted/disabled — `Planned` or `Pending` only  
- **BTC options (PPE):** first enabled analytical surface  

Planned surfaces must not imply live data, charts, signals, monitoring, persistence, APIs, or execution.

## Local preview

Open `prototype/html/01_home.html` in a browser (sibling `style.css` must stay in `prototype/html/`).
