# MVP1 distribution stats legibility — relay sprint spec

**Controlling canon:** [`docs/SEMANTIC_CONTRACTS.md`](../SEMANTIC_CONTRACTS.md)  
**Prior chapter:** [`SPRINT_MVP1_DISTRIBUTION_EXPORT.md`](SPRINT_MVP1_DISTRIBUTION_EXPORT.md) (CSV Phase 1)  
**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md)  
**SELECTION:** [`POST_MVP1_DISTRIBUTION_STATS_LEGIBILITY_SELECTION.md`](POST_MVP1_DISTRIBUTION_STATS_LEGIBILITY_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Ship a **labeled on-screen Distribution summary** on the BTC implied lab so a research partner can read **mean and quartiles** across expiries during a screen-share — without downloading CSV first. Reuse `build_distribution_export_rows()` data; **no new distribution math**.

**Priority:** HIGH (research demo path).

---

## Label dictionary (canonical)

| Field | User-facing label | Tooltip (short) |
|-------|-------------------|-----------------|
| `mean_usd` | Risk-neutral mean | Expected terminal price under this distribution |
| `q50_usd` | Median terminal price (50th %) | Half of implied outcomes below this price |
| `q25_usd` | Lower quartile | 25th percentile of terminal price |
| `q75_usd` | Upper quartile | 75th percentile of terminal price |
| derived | Implied range width | q75 − q25; wider = more uncertainty |
| `lognormal_reference` | Model bell (lognormal) | Forward + ATM vol baseline |
| `market_implied_bl` | Options chain (B–L) | Shape from live option marks |

---

## Acceptance

1. Implied lab shows **Distribution summary** table when expiries load (anchor id `distribution-summary`).
2. Plain-English column headers + method badges; **How to read this table** expander.
3. CSV download unchanged (`Download distribution stats (CSV)`).
4. BL-skipped rows show honest status (filter or badge per `bl_status`).
5. `python -m pytest -q` green; optional implied-lab smoke note in evidence.

---

## Touch set

- `src/viz/implied_lab_legibility.py` — distribution-table labels and tooltips
- `src/viz/distribution_summary_panel.py` (new) — display-only table builder
- `src/viz/app.py` — wire panel above/beside CSV download
- `tests/test_distribution_summary_legibility.py` (new)

---

## Not now

- New quantile / mean math (reuse Phase 1 export pipeline)
- MSOS Next.js table (MSOS chapter follows)
- Daily historical collector (low-priority chapter)
- Tail quantiles or strike-level P(>K)

---

## Sprint status

**CHARTERED** — blocked in backlog until `mvp1_probability_method_legibility` **COMPLETE**.
