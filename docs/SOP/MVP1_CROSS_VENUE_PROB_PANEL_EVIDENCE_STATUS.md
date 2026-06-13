# MVP1 cross-venue probability panel — evidence status

**Chapter:** `mvp1_cross_venue_prob_panel`  
**Status:** **CHARTERED** 2026-06-13 — awaits relay after prior MEDIUM + HIGH chapters  
**Phase plan:** [`PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json`](PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-CrossVenue-Control-Slice001 | PENDING | Charter witness |
| MVP1-CrossVenue-Product-Slice002 | PENDING | Export module + tests |
| MVP1-CrossVenue-Product-Slice003 | PENDING | Implied-lab download |
| MVP1-CrossVenue-Product-Slice004 | PENDING | Daily snapshot script |
| MVP1-CrossVenue-Smoke-Slice005 | PENDING | pytest witness |
| MVP1-CrossVenue-Closeout-Slice006 | PENDING | Share checklist |

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after PR merge  
- [ ] Implied lab → **Download cross-venue prob panel (CSV)** with Polymarket enabled  
- [ ] Confirm `gap_bl_minus_pm_pct` populated where BL computes  
- [ ] `python scripts/collect_cross_venue_snapshot.py` writes dated artifact  
- [ ] Send CSV + schema pointer to quant contact  
