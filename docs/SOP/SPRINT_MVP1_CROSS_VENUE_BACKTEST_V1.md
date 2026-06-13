# MVP1 cross-venue backtest v1 — relay sprint spec

**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) · chapter **5**  
**SELECTION:** [`POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md`](POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md)  
**Baseline:** **`main`** · **Requires:** `mvp1_cross_venue_scan_v1` **COMPLETE** + snapshot history

---

## Sprint intent

Score whether cross-venue gaps and probability forecasts **predicted resolved outcomes**. Join daily snapshots to settled Polymarket BTC price questions; emit a written evidence report — not trades.

**Priority:** **LOW** (after scan v1).

**Operator precondition:** recommend **≥14 daily snapshots** in `artifacts/cross_venue_snapshots/` before expecting meaningful output (script warns if fewer).

---

## Deliverables

### `scripts/run_cross_venue_backtest.py`

```bat
python scripts/run_cross_venue_backtest.py
python scripts/run_cross_venue_backtest.py --snapshots-root artifacts/cross_venue_snapshots
python scripts/run_cross_venue_backtest.py --min-snapshots 14
```

Behavior:

1. Load all prob-panel CSVs under snapshots root.
2. Fetch **closed** Polymarket markets for matching `(strike, resolution_date)`; label outcome 0/1 (BTC above strike at resolution).
3. For each resolved question with ≥1 snapshot before resolution:
   - **Brier score** for PM Yes% and BL P(>K)
   - **Gap buckets:** mean outcome when `gap_bl_minus_pm_pct` ∈ thresholds (e.g. PM rich / options rich / neutral)
4. Write `artifacts/cross_venue_backtest/latest_report.md` + `latest_summary.json`.
5. Exit 0 with warning (not error) if insufficient snapshots or unresolved markets.

### `src/viz/cross_venue_backtest.py`

Pure functions:

- `load_snapshot_rows(root) -> list[dict]`
- `join_resolved_outcomes(rows, resolved_markets) -> list[dict]`
- `brier_score(predictions, outcomes) -> float`
- `gap_bucket_summary(rows) -> list[dict]`
- `format_backtest_report_markdown(summary) -> str`

### Tests

- Fixture CSVs under `tests/fixtures/cross_venue_backtest/` (synthetic; no network).
- Assert Brier math, bucket counts, report header.

---

## Metrics (v1 scope)

| Metric | Notes |
|--------|--------|
| Brier (PM) | Lower is better |
| Brier (BL) | Lower is better |
| n resolved | Count of questions with outcome |
| Gap bucket hit rate | Did high positive gap correlate with BTC > K? |

---

## Acceptance

1. `python -m pytest -q` green.
2. Fixture-only tests pass without Polymarket network.
3. Script runs on empty/minimal snapshot dir with clear warning text.
4. Evidence doc includes sample fixture run output.

---

## Touch set

- `src/viz/cross_venue_backtest.py` (new)
- `scripts/run_cross_venue_backtest.py` (new)
- `tests/test_cross_venue_backtest.py` (new)
- `tests/fixtures/cross_venue_backtest/` (new)
- `docs/SOP/PPE_IDE_NATIVE_OPERATOR_V1.md`

---

## Not now

- Full historical PM backfill automation
- Paper PnL / spread trade simulation
- MSOS calibration tab wiring
- Multi-asset

---

## Slice map

| Slice | Plane | Goal |
|-------|-------|------|
| MVP1-CrossVenueBt-Control-Slice001 | CONTROL | Charter |
| MVP1-CrossVenueBt-Product-Slice002 | PPE_UI | Backtest module + fixtures + tests |
| MVP1-CrossVenueBt-Product-Slice003 | CONTROL | CLI + runbook |
| MVP1-CrossVenueBt-Smoke-Slice004 | EVIDENCE | pytest witness |
| MVP1-CrossVenueBt-Closeout-Slice005 | EVIDENCE | Closeout + score memo template |
