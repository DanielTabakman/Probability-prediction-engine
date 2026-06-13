# MVP1 distribution quant research v2 — relay sprint spec

**Controlling canon:** [`POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md`](POST_MVP1_DISTRIBUTION_EXPORT_SELECTION.md) (Phase 2+)  
**SELECTION:** [`POST_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2_SELECTION.md`](POST_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2_SELECTION.md)  
**Baseline:** **`main`**

---

## Sprint intent

Quant depth for **backtest-oriented research**: tail quantiles, strike-level **P(S > K)**, derived export columns, and a **daily snapshot collector MVP**.

**Priority:** LOW (after HIGH legibility + MEDIUM MSOS demo).

---

## Scope

- **PPE_CORE:** tail quantiles (q05/q10/q90/q95); P(S > K) strike ladder helpers
- **PPE_UI:** extended CSV + summary panel columns (IQR, BL−LN gap)
- **scripts:** `collect_distribution_stats_snapshot.py` MVP + runbook note

---

## Not now

- Multi-asset, MSOS REST API, full backfill automation
- **Polymarket joint export** — moved to [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md) (MEDIUM slot 2)

---

## Sprint status

**CHARTERED** — blocked until `msos_strategy_lab_distribution_demo` **COMPLETE**.
