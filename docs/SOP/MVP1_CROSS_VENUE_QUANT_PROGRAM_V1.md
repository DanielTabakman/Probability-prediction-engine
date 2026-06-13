# MVP1 cross-venue quant program v1

**Purpose:** One canonical map of the Polymarket ↔ options quant wedge — from data to automated results to evidence — so stewards and operators know what runs when the loop is kept alive.

**As-of:** 2026-06-13 · **Controlling playbook:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)

---

## North star

**See cross-venue probability gaps ranked automatically — then learn whether they predicted anything — without reading CSVs by hand.**

Not auto-trade. Not execution. Screening + evidence first.

---

## Chapter sequence (relay order)

| # | Chapter | Priority | Blocked until | Delivers |
|---|---------|----------|---------------|----------|
| 0 | `mvp1_distribution_quant_research_v2` | LOW | — (may run first if READY) | Dist-stats tails, P(S>K) ladders, dist snapshot script |
| 1 | `msos_storyboard_visual_parity_v1` | MEDIUM · 1 | P8 COMPLETE | MSOS visual parity |
| 2 | `msos_public_demo_launch_v1` | MEDIUM · 1 | storyboard COMPLETE | Public demo + research beta CTA |
| 3 | **`mvp1_cross_venue_prob_panel`** | MEDIUM · 2 | public demo COMPLETE | CSV export + daily snapshot (**PR #149** implementation) |
| 4 | **`mvp1_cross_venue_scan_v1`** | MEDIUM · 3 | prob panel COMPLETE | Live scan → ranked report (no manual CSV) |
| 5 | **`mvp1_cross_venue_backtest_v1`** | LOW | scan COMPLETE + snapshot history | Resolution scores, Brier, gap-bucket stats |

Mechanical order: **high → medium → low**; within medium, **backlog file order** (slots 1–3 above).

---

## Operator artifacts (by chapter)

| Chapter | Command / artifact |
|---------|-------------------|
| prob panel | `python scripts/collect_cross_venue_snapshot.py` → `artifacts/cross_venue_snapshots/` |
| scan v1 | `python scripts/run_cross_venue_scan.py` → `artifacts/cross_venue_reports/latest.md` + `latest.json` |
| backtest v1 | `python scripts/run_cross_venue_backtest.py` → `artifacts/cross_venue_backtest/latest_report.md` |

**Daily ritual (after scan + prob panel ship):** snapshot collector on a schedule → scan after each snapshot (or cron both).

---

## What each phase excludes

| Phase | Not now |
|-------|---------|
| prob panel | Ranked scan, backtest, alerts |
| scan v1 | Historical scoring, MSOS tab, ntfy |
| backtest v1 | Auto-trade, full PM backfill, multi-asset |

---

## Source docs

| Chapter | Sprint | SELECTION | Relay plan |
|---------|--------|-----------|------------|
| prob panel | [`SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md`](SPRINT_MVP1_CROSS_VENUE_PROB_PANEL.md) | [`POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md`](POST_MVP1_CROSS_VENUE_PROB_PANEL_SELECTION.md) | [`PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json`](PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json) |
| scan v1 | [`SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md`](SPRINT_MVP1_CROSS_VENUE_SCAN_V1.md) | [`POST_MVP1_CROSS_VENUE_SCAN_V1_SELECTION.md`](POST_MVP1_CROSS_VENUE_SCAN_V1_SELECTION.md) | [`PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json`](PHASE_PLANS/mvp1_cross_venue_scan_v1_relay.json) |
| backtest v1 | [`SPRINT_MVP1_CROSS_VENUE_BACKTEST_V1.md`](SPRINT_MVP1_CROSS_VENUE_BACKTEST_V1.md) | [`POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md`](POST_MVP1_CROSS_VENUE_BACKTEST_V1_SELECTION.md) | [`PHASE_PLANS/mvp1_cross_venue_backtest_v1_relay.json`](PHASE_PLANS/mvp1_cross_venue_backtest_v1_relay.json) |

---

## Implementation note (prob panel)

Product code for chapter 3 lives on branch `charter/msos-launch-and-checkin` (**PR #149**). Merge that PR before or during the prob-panel relay BUILD so slices 002–004 are not greenfield.

---

## Success criteria (program-level)

1. Operator runs **one command** and gets top gaps (scan v1).
2. After **≥14 daily snapshots**, backtest v1 produces a written score memo.
3. No CSV-by-hand workflow required for daily screening.
