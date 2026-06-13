# MVP1 cross-venue probability panel — relay sprint spec

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) · original arb thesis in [`README.md`](../../README.md)  
**SELECTION:** [`POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md`](POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Export **Polymarket Yes% vs options-implied P(BTC > K)** at matched strike/horizon as a **cross-venue probability panel CSV** — the shortest quant + arb-candidate wedge. Reuses live math from `prediction_spread_probs.py` and `fetch_deribit_spreads_around_predictions`; adds gap columns, match-quality flags, implied-lab download, and a daily snapshot collector.

**Priority:** **MEDIUM** (queue slot **2** among medium-tier chapters — after MSOS storyboard parity + public demo launch; before LOW dist-quant-v2).

---

## CSV contract (`cross_venue_prob_panel.csv`)

| Column | Notes |
|--------|--------|
| `as_of_utc` | Snapshot time |
| `question` | Polymarket market question text |
| `strike_usd` | Parsed BTC target |
| `resolution_date` | PM resolution (`YYYY-MM-DD`) |
| `matched_expiry_date` | Deribit expiry used for options leg |
| `horizon_days` | Days from as-of to resolution |
| `expiry_alignment` | `before_resolution` \| `after_resolution` \| `same_day` |
| `polymarket_yes_pct` | PM Yes probability (%) |
| `options_ln_p_above_pct` | Lognormal P(S > K) (%) |
| `options_bl_p_above_pct` | BL chain P(S > K) (%) |
| `gap_bl_minus_pm_pct` | Primary signal: BL − PM |
| `gap_ln_minus_pm_pct` | Secondary: lognormal − PM |
| `spread_cost_usd` | Bull-call spread cost (expression proxy) |
| `spread_proxy_prob_pct` | cost/width approx (%) |
| `spot_usd`, `forward_usd`, `atm_iv_annual` | Provenance |
| `call_marks_count` | BL quality (empty if unknown) |
| `match_status` | `ok` \| `ok_ln_only` \| `insufficient_data` |

**Exclude:** auto-trade signals, execution, user belief overlay, MSOS REST surface.

---

## Acceptance

1. `python -m pytest -q` green before/after each PRODUCT slice.
2. Unit tests for gap math, expiry alignment, CSV header contract.
3. Implied lab shows **Download cross-venue prob panel (CSV)** when Polymarket + Deribit data load; file has ≥1 row on a typical live day.
4. `python scripts/collect_cross_venue_snapshot.py` writes dated CSV under `artifacts/cross_venue_snapshots/`.
5. Evidence doc updated on closeout with sample row count.

---

## Touch set

- `src/viz/cross_venue_export.py` (new) — row builder + serializer (no Streamlit)
- `src/viz/app.py` — download button on implied lab
- `scripts/collect_cross_venue_snapshot.py` (new)
- `tests/test_cross_venue_export.py` (new)
- `docs/SOP/PPE_IDE_NATIVE_OPERATOR_V1.md` — snapshot runbook note (Slice004)

---

## Not now

- Auto-trade / arb alerts
- Historical Polymarket backfill automation
- Multi-asset
- MSOS Next.js download chrome
- Full backtest runner (notebook/script OK outside `src/`)

---

## Slice map

### MVP1-CrossVenue-Control-Slice001 — charter (CONTROL)

**Goal:** Accept sprint spec, phase plan, SELECTION record, backlog/queue wiring.

**Layer preset:** `CONTROL`

---

### MVP1-CrossVenue-Product-Slice002 — export module (PRODUCT)

**Goal:** `build_cross_venue_export_rows`, `serialize_cross_venue_export_csv`, gap + match helpers; tests.

**Layer preset:** `PPE_UI` · `workerMode`: `local-agent`

---

### MVP1-CrossVenue-Product-Slice003 — implied-lab download (PRODUCT)

**Goal:** Download button beside distribution stats CSV; caption when Polymarket sidebar off.

**Layer preset:** `PPE_UI` · `workerMode`: `local-agent`

---

### MVP1-CrossVenue-Product-Slice004 — daily collector (PRODUCT)

**Goal:** `scripts/collect_cross_venue_snapshot.py` + operator runbook note.

**Layer preset:** `CONTROL` · `workerMode`: `local-agent`

---

### MVP1-CrossVenue-Smoke-Slice005 — witness (EVIDENCE)

**Goal:** Full pytest witness + sample CSV row count in evidence doc.

---

### MVP1-CrossVenue-Closeout-Slice006 — closeout (EVIDENCE)

**Goal:** Frontier/backlog sync; share checklist for quant contact.

---

## Relationship to dist-quant-v2

Cross-venue PM joint export **moved out** of [`SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md`](SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md). Dist-quant-v2 remains **LOW** for tail quantiles + dist-stats collector extensions only.
