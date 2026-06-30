# Trader Learning Spine program v1

**Purpose:** One readable map for **save → review → track accuracy** — the product “backtest” traders actually use. Operators and BUILD agents share this doc; module-registry tiers are implementation detail.

**Status:** **ACTIVE** — chartered 2026-06-29  
**Milestone:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md)  
**SELECTION:** [`POST_TRADER_LEARNING_SPINE_V1_SELECTION.md`](POST_TRADER_LEARNING_SPINE_V1_SELECTION.md)

---

## What the spine is (one sentence)

**Save what you thought, come back after expiry, say if you were right, see your track record.**

Not a quant backtest engine. Not live execution. Paper + saved snapshots only.

---

## The walkthrough (what you should be able to demo)

| Step | User action | Surface |
|------|-------------|---------|
| 1 | Open Strategy Lab, set belief, disagree with market | `/strategy-lab` |
| 2 | Save / freeze the evaluation | Strategy Lab or Streamlit freeze |
| 3 | See saved view on Monitor / History | `/monitor`, `/history` |
| 4 | After horizon, open post-mortem and submit review | `/monitor` → snapshot detail |
| 5 | Command Center shows reviews due + completed counts | `/` calibration strip |

**Gap today (2026-06-30):** step 4 **write** shipped on `main` (`/monitor` snapshot detail + `SnapshotReviewForm` + review API). Streamlit freeze (step 2) still optional. Relay may still run witness/closeout for `msos_trader_review_loop_v1` — **do not re-BUILD product**.

---

## Spine chapters (relay order)

Run **after** exposure menu COMPLETE unless steward re-prioritizes. **Next UX BUILD (steward):** promote `msos_trader_workflow_horizon_nav_v1` per [`UX_EXECUTION_BACKLOG_V1.md`](UX_EXECUTION_BACKLOG_V1.md).

| # | Chapter | Delivers | Priority |
|---|---------|----------|----------|
| 1 | **`msos_trader_review_loop_v1`** | Post-mortem form in MSOS + review API; KPIs update | **P0 spine** — product on `main`; relay closeout only |
| 2 | `msos_strategy_lab_dist_download_v1` | Distribution CSV download on `/strategy-lab` | P1 — product on `main`; relay closeout only |
| 3 | `msos_cross_venue_strategy_lab_v1` | Cross-venue gap + backtest summary card (read-only) | P2 · side |
| 4 | `mvp1_distribution_timeseries_collector_v1` | VM daily dist-stats archive (feeds future charts) | P2 · ops |

**Deferred (not spine):** `horizon_replay_scrubber_v1` until archive ≥30d; full strategy P&L backtest; calibration science dashboards.

---

## Foundations already shipped

| Piece | Location |
|-------|----------|
| Freeze + SQLite persistence | `src/viz/frozen_evaluation_store.py` |
| Review statuses + `upsert_review` | same module |
| Monitor / History read live review state | `apps/msos-web/src/lib/commandCenterSummary.ts` |
| Calibration strip copy | `apps/msos-web/src/lib/monitorHistoryFeed.ts` |
| Cross-venue backtest math | `src/viz/cross_venue_backtest.py` + VM collector |
| Class summary rollups (Streamlit) | `src/viz/reviewed_class_summary.py` |

---

## Non-goals

- Live execution or order routing
- Porting PPE math to TypeScript
- Auto-trading signals from cross-venue gaps
- “Collect everything forever” archives without charter

---

## Success (program-level)

1. A tester completes **save → post-mortem → see KPI** entirely inside MSOS (no Streamlit).
2. Cross-venue credibility card visible on Strategy Lab when VM history allows.
3. Distribution timeseries collector running on loop host (ops witness).

Log demo sessions in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md).
