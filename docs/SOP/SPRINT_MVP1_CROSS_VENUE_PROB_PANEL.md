# MVP1 cross-venue probability panel — relay sprint spec

**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) · chapter **3**  
**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · original arb thesis in [`README.md`](../../README.md)  
**SELECTION:** [`POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md`](POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md)  
**Baseline:** **`main`** · **Implementation:** merge **PR #149** before PRODUCT slices

---

## Sprint intent

Export **Polymarket Yes% vs options-implied P(BTC > K)** at matched strike/horizon as a **cross-venue probability panel CSV**. Reuses `prediction_spread_probs.py` and `fetch_deribit_spreads_around_predictions`; adds gap columns, match-quality flags, implied-lab download, and daily snapshot collector.

**Priority:** **MEDIUM · slot 2** (after MSOS storyboard + public demo).

**Next chapter:** [`mvp1_cross_venue_scan_v1`](SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md) — automated ranked report (no CSV-by-hand).

---

## CSV contract

See program doc · primary signal: `gap_bl_minus_pm_pct`.

---

## Acceptance

1. `python -m pytest -q` green before/after each PRODUCT slice.
2. Unit tests for gap math, expiry alignment, CSV header contract.
3. Implied lab **Download cross-venue prob panel (CSV)** when Polymarket + Deribit load.
4. `python scripts/collect_cross_venue_snapshot.py` → `artifacts/cross_venue_snapshots/`.
5. Evidence doc updated on closeout.

---

## Touch set

- `src/viz/cross_venue_export.py`
- `src/viz/app.py`
- `scripts/collect_cross_venue_snapshot.py`
- `tests/test_cross_venue_export.py`
- `docs/SOP/PPE_IDE_NATIVE_OPERATOR_V1.md`

---

## Not now

- Ranked scan / report (**next chapter** — scan v1)
- Backtest scoring (**chapter 5** — backtest v1)
- Auto-trade, ntfy alerts, MSOS REST, multi-asset

---

## Slice map

| Slice | Plane | Goal |
|-------|-------|------|
| MVP1-CrossVenue-Control-Slice001 | CONTROL | Charter + queue wiring |
| MVP1-CrossVenue-Product-Slice002 | PPE_UI | Export module + tests |
| MVP1-CrossVenue-Product-Slice003 | PPE_UI | Implied-lab download |
| MVP1-CrossVenue-Product-Slice004 | CONTROL | Snapshot script + runbook |
| MVP1-CrossVenue-Smoke-Slice005 | EVIDENCE | pytest witness |
| MVP1-CrossVenue-Closeout-Slice006 | EVIDENCE | Closeout + share checklist |
