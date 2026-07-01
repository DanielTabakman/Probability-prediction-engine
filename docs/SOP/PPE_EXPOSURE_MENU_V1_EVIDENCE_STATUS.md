---
archived: true
chapter_id: ppe_exposure_menu_v1
closed: 2026-06-29
---

# PPE Exposure menu v1 — evidence status

**Chapter:** `ppe_exposure_menu_v1`  
**Module:** `exposure_menu`  
**Status:** **COMPLETE** 2026-06-29 — relay active (control slice next)  
**SELECTION:** [`POST_PPE_EXPOSURE_MENU_V1_SELECTION.md`](POST_PPE_EXPOSURE_MENU_V1_SELECTION.md)  
**Program:** [`EXPOSURE_MENU_PROGRAM_V1.md`](EXPOSURE_MENU_PROGRAM_V1.md)  
**Phase plan:** [`PHASE_PLANS/ppe_exposure_menu_v1_relay.json`](PHASE_PLANS/ppe_exposure_menu_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| PPE-ExposureMenu-Control-Slice001 | COMPLETE | |
| PPE-ExposureMenu-Core-Slice002 | COMPLETE | |
| PPE-ExposureMenu-CLI-Slice003 | COMPLETE | |
| PPE-ExposureMenu-UI-Slice004 | COMPLETE | |
| PPE-ExposureMenu-Product-Slice005 | COMPLETE | |
| PPE-ExposureMenu-Closeout-Slice006 | COMPLETE | |

## Acceptance checklist (chapter close)

- [ ] CLI NVDA long ≥3 live paths
- [ ] CLI BTC long ≥3 live paths
- [ ] Boundary API contract stable
- [ ] MSOS `/exposure` + secondary nav
- [ ] Planned rails honest
- [ ] Registry + module map updated
