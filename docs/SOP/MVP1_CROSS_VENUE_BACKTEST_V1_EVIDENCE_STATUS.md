---
archived: true
chapter_id: mvp1_cross_venue_backtest_v1
closed: 2026-07-09
---

# MVP1 cross-venue backtest v1 — evidence status

**Chapter:** `mvp1_cross_venue_backtest_v1`  
**Status:** **COMPLETE** 2026-07-09  
**Phase plan:** [`PHASE_PLANS/mvp1_cross_venue_backtest_v1_relay.json`](PHASE_PLANS/mvp1_cross_venue_backtest_v1_relay.json)  
**Sprint:** [`SPRINT_MVP1_CROSS_VENUE_BACKTEST_V1.md`](SPRINT_MVP1_CROSS_VENUE_BACKTEST_V1.md)  
**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-CrossVenueBacktest-Control-Slice001 | **CLOSED** | Evidence stub + queue wiring (#417) |
| MVP1-CrossVenueBacktest-Product-Slice002 | **CLOSED** | `cross_venue_backtest.py` Brier + gap buckets (#415) |
| MVP1-CrossVenueBacktest-Closeout-Slice004 | COMPLETE | Chapter closeout + run script follow-on |

## Deliverables

- Brier scores for PM vs options BL from snapshot CSV history
- Gap-bucket calibration stats in `src/viz/cross_venue_backtest.py`
- Operator script target: `python scripts/run_cross_venue_backtest.py` → `artifacts/cross_venue_backtest/latest_report.md`

## Witness checklist

- [x] `pytest tests/test_mvp1_cross_venue_backtest.py -q`
- [ ] Closeout COMPLETE on `main`
