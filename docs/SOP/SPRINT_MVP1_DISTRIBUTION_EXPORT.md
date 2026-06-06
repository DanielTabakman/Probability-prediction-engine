# MVP1 distribution export — relay sprint spec (Phase 1)

**Controlling canon:** [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md)  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md)  
**SELECTION:** [`POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md`](POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Ship **BTC implied distribution statistics** as a **CSV download** on the implied options lab: **mean** and **quartiles (q25, q50, q75)** for each listed **options expiry** at the current run snapshot, for both market distributions the lab already computes:

1. **Lognormal reference** (forward + ATM IV) — purple model bell  
2. **Market-implied Breeden–Litzenberger** (options chain) — orange curve when marks gate passes

Research-partner deliverable for external backtest exploration. **Phase 1 only** — instant cross-expiry panel; no daily historical collector.

## CSV contract (canonical columns)

| Column | Notes |
|--------|--------|
| `as_of_utc` | Run snapshot / valuation time from verification |
| `asset` | `BTC` |
| `expiry_date` | Options expiry (`YYYY-MM-DD`) |
| `T_years` | Time to expiry at as-of |
| `distribution` | `lognormal_reference` \| `market_implied_bl` |
| `mean_usd` | Lognormal: risk-neutral forward; BL: ∫ x·f(x) dx on grid |
| `q25_usd` | 25th percentile of terminal price |
| `q50_usd` | Median |
| `q75_usd` | 75th percentile |
| `forward_usd` | Deribit forward for expiry |
| `atm_iv_annual` | ATM IV used for lognormal reference |
| `spot_usd` | BTC spot at fetch |
| `call_marks_count` | Call marks used for BL (empty for lognormal-only rows) |
| `bl_status` | `computed` \| `skipped` + optional skip reason shorthand |

**Exclude:** user belief (subjective overlay), strategy payoff, disagreement categories (separate research export later).

## Acceptance

1. `python -m pytest -q` green before/after each PRODUCT slice.
2. Unit tests for quantile helpers on known lognormal parameters (mean ≈ forward; symmetric sanity).
3. Implied lab shows **Download distribution stats (CSV)** when expiries load; file includes **all** fetched expiries × both distribution types where BL is available.
4. BL-skipped expiries still emit `lognormal_reference` rows; `market_implied_bl` row has `bl_status=skipped` and empty quantiles or honest placeholders per serializer contract (document in evidence).
5. Evidence doc updated on closeout with sample row count and pytest witness.

## Touch set

- `src/engine/implied_distribution.py` — quantile / mean helpers (no viz imports)
- `src/viz/distribution_export.py` (new) — row builder + `serialize_distribution_export_csv` (no Streamlit)
- `src/viz/app.py` — download button on implied lab panel
- `tests/test_implied_distribution.py` (extend or new `tests/test_distribution_export.py`)

## Not now

- Daily/historical time-series collector or SQLite timeseries table  
- ETH, SOL, Hyperliquid  
- User-belief distribution export  
- Full PDF grid export  
- MSOS shell / Next.js download surface (Streamlit private app is sufficient for v1)

---

## Slice map

### MVP1-DistExport-Control-Slice001 — charter (CONTROL)

**Goal:** Accept sprint spec, phase plan, SELECTION record, frontier sync.

**Layer preset:** `CONTROL`

---

### MVP1-DistExport-Product-Slice002 — distribution quantiles (PRODUCT)

**Goal:** `lognormal_distribution_stats()` and `density_distribution_stats()` in `src/engine/implied_distribution.py`; tests.

**Layer preset:** `PPE_CORE` · `workerMode`: `local-agent`

---

### MVP1-DistExport-Product-Slice003 — CSV export + UI download (PRODUCT)

**Goal:** `distribution_export.py` serializer; loop all BTC expiries; **Download distribution stats (CSV)** in implied lab.

**Layer preset:** `PPE_UI` · `workerMode`: `local-agent`

---

### MVP1-DistExport-Smoke-Slice004 — witness (EVIDENCE)

**Goal:** Full pytest green; optional implied-lab smoke note in evidence doc.

**Layer preset:** `CONTROL`

---

### MVP1-DistExport-Closeout-Slice005 — chapter close (CONTROL)

**Goal:** Chapter **COMPLETE** in frontier; evidence doc; post-chapter SELECTION prep.

**Layer preset:** `CONTROL`

---

## Sprint status

**MVP1 distribution export (Phase 1):** **CHARTERED** — await SELECTION after MSOS P4 COMPLETE.
