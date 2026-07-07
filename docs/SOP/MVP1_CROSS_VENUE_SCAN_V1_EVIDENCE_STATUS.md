---
archived: true
chapter_id: mvp1_cross_venue_scan_v1
closed: unknown
---

# MVP1 cross-venue scan v1 — evidence status

**Chapter:** `mvp1_cross_venue_scan_v1`  
**Status:** **CHARTERED** (side-channel · LOW)  
**Phase plan:** [`PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json`](PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md`](SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md)  
**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-CrossVenueScan-Control-Slice001 | PENDING | Charter + witness wiring |
| MVP1-CrossVenueScan-Product-Slice002 | PENDING | `cross_venue_scan.py` gap ranking + report serialization |
| MVP1-CrossVenueScan-Closeout-Slice004 | PENDING | Frontier COMPLETE + program handoff |

## Deliverables

- Rank Polymarket vs options-implied gaps (`gap_bl_minus_pm_pct`) from cross-venue export rows.
- Markdown + JSON scan report helpers in `src/viz/cross_venue_scan.py`.
- Operator script target: `python scripts/run_cross_venue_scan.py` → `artifacts/cross_venue_reports/` (follow-on slice if not yet wired).

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after relay closeout
- [ ] Unit tests: `pytest tests/test_mvp1_cross_venue_scan.py -q`
- [ ] Reports sort by |gap| — screening only, not trade advice

**Next SELECTION:** [`POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md`](POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md)
