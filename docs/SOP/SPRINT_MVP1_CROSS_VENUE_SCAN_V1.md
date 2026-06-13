# MVP1 cross-venue scan v1 — relay sprint spec

**Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md) · chapter **4**  
**SELECTION:** [`POST_MVP1_CROSS_VENUE_SCAN_V1_SELECTION.md`](POST_MVP1_CROSS_VENUE_SCAN_V1_SELECTION.md)  
**Baseline:** **`main`** · **Requires:** `mvp1_cross_venue_prob_panel` **COMPLETE**

---

## Sprint intent

**One command → ranked cross-venue gaps** — no CSV-by-hand. Filter trustworthy matches, sort by `|gap_bl_minus_pm_pct|`, write human-readable + machine-readable reports.

**Priority:** **MEDIUM · slot 3** (after prob panel).

---

## Deliverables

### `scripts/run_cross_venue_scan.py`

CLI:

```bat
python scripts/run_cross_venue_scan.py
python scripts/run_cross_venue_scan.py --from-snapshot path/to.csv
python scripts/run_cross_venue_scan.py --min-gap 5 --top 10
```

Behavior:

1. Live mode: reuse `build_cross_venue_panel_rows` (same as snapshot collector).
2. Snapshot mode: read existing CSV from `artifacts/cross_venue_snapshots/` (latest or `--from-snapshot`).
3. Filter rows: default `match_status` ∈ `{ok}`; optional include `ok_ln_only`.
4. Rank by `|gap_bl_minus_pm_pct|` descending.
5. Write:
   - `artifacts/cross_venue_reports/latest.json`
   - `artifacts/cross_venue_reports/latest.md` (operator-readable table + one-line summaries)
6. Print top N to stdout.

### `src/viz/cross_venue_scan.py`

Pure functions (no Streamlit):

- `parse_export_row(dict) -> CrossVenueRow`
- `filter_scan_rows(rows, *, min_gap_pp, match_statuses) -> list`
- `rank_scan_rows(rows) -> list`
- `format_scan_report_markdown(rows, *, as_of_utc) -> str`
- `format_scan_report_json(rows, *, as_of_utc) -> dict`

### Optional UI (Product-Slice004)

Implied lab expander **Today's top gaps** — reads `latest.md` if present (read-only; no new math).

---

## Report markdown shape (example)

```markdown
# Cross-venue scan — 2026-06-13T12:00:00Z

| Rank | Strike | Resolution | PM% | BL% | Gap | Tier |
|------|--------|------------|-----|-----|-----|------|
| 1 | $150,000 | 2026-12-31 | 12.5 | 18.0 | +5.5 | before_resolution |

**Summary:** 3 rows passed filters; largest gap +5.5pp on $150k Dec-26 question.
```

---

## Acceptance

1. `python -m pytest -q` green.
2. Unit tests on synthetic rows — no network in CI.
3. `run_cross_venue_scan.py` exits 0 on fixture CSV; writes both report files.
4. Operator runbook note in `PPE_IDE_NATIVE_OPERATOR_V1.md`.

---

## Touch set

- `src/viz/cross_venue_scan.py` (new)
- `scripts/run_cross_venue_scan.py` (new)
- `tests/test_cross_venue_scan.py` (new)
- `src/viz/app.py` (optional expander)
- `docs/SOP/PPE_IDE_NATIVE_OPERATOR_V1.md`

---

## Not now

- Backtest / resolution scoring (**backtest v1**)
- ntfy push on large gap
- MSOS monitor tab
- Auto-trade language

---

## Slice map

| Slice | Plane | Goal |
|-------|-------|------|
| MVP1-CrossVenueScan-Control-Slice001 | CONTROL | Charter witness |
| MVP1-CrossVenueScan-Product-Slice002 | PPE_UI | Scan module + tests |
| MVP1-CrossVenueScan-Product-Slice003 | CONTROL | `run_cross_venue_scan.py` + runbook |
| MVP1-CrossVenueScan-Product-Slice004 | PPE_UI | Optional implied-lab expander |
| MVP1-CrossVenueScan-Smoke-Slice005 | EVIDENCE | pytest + fixture report witness |
| MVP1-CrossVenueScan-Closeout-Slice006 | EVIDENCE | Closeout |
