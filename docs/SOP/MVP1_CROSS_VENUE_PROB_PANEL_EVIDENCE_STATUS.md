# MVP1 cross-venue probability panel — evidence status

**Chapter:** `mvp1_cross_venue_prob_panel`  
**Status:** **COMPLETE** 2026-06-13  
**Phase plan:** [`PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json`](PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md)  
**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-CrossVenue-Control-Slice001 | CLOSED | Charter + queue wiring |
| MVP1-CrossVenue-Product-Slice002 | CLOSED | `cross_venue_export.py` + gap/CSV tests |
| MVP1-CrossVenue-Product-Slice003 | CLOSED | Implied-lab **Download cross-venue prob panel (CSV)** |
| MVP1-CrossVenue-Product-Slice004 | CLOSED | `collect_cross_venue_snapshot.py` + operator runbook |
| MVP1-CrossVenue-Smoke-Slice005 | CLOSED | pytest witness |
| MVP1-CrossVenue-Closeout-Slice006 | CLOSED | Frontier COMPLETE + share checklist |

## Deliverables

- CSV export: Polymarket Yes% vs options-implied P(BTC > K) with `gap_bl_minus_pm_pct` and match-quality columns.
- Implied lab download when Polymarket + Deribit are loaded.
- Daily snapshot collector → `artifacts/cross_venue_snapshots/`.

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after PR merge
- [ ] Private implied lab → **Download cross-venue prob panel (CSV)** with Deribit + Polymarket enabled
- [ ] Confirm CSV header matches `CSV_COLUMNS` in `cross_venue_export.py`
- [ ] Optional: `python scripts/collect_cross_venue_snapshot.py` for daily artifact
- [ ] Sort by |gap_bl_minus_pm_pct| for research review — not trade advice

**Next SELECTION:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) — scan v1 chapter.
