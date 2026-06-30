# Research pipeline v1 — collect, test, trade (later)

**Purpose:** Edge research as three plug-in layers — **collectors**, **tests**, **strategies** (deferred). Cross-venue PM ↔ options is the reference template.

**SSOT registry:** [`config/research_pipeline_registry.json`](../../config/research_pipeline_registry.json)  
**Visual:** [`assets/msos_module_map.html`](assets/msos_module_map.html) § Research pipeline  
**Archive health:** `python scripts/research_archive_health.py --write`

---

## Operator commands

| Command | Role |
|---------|------|
| `run_research_daily.cmd` | All collectors + eligible tests (registry-driven) |
| `run_cross_venue_daily.cmd` | Cross-venue collect + scan only (legacy daily) |
| `run_cross_venue_collector_dev.cmd --interval 300 --count 12` | Dev high-cadence smoke (not production) |
| `run_cross_venue_tradeability.cmd` | Net gap after spread proxy on latest snapshot |
| `install_distribution_collector_task.cmd` | VM daily distribution stats (07:45) |

Health JSON: `artifacts/control_plane/RESEARCH_ARCHIVE_HEALTH.json`  
Daily summary: `artifacts/control_plane/RESEARCH_DAILY_LAST.json`

---

## Three layers

| Layer | Question | Output |
|-------|----------|--------|
| **Collector** | What did markets say at time T? | `artifacts/<archive>/` |
| **Test** | Does this pattern mean anything? | `artifacts/<report>/latest_*` |
| **Strategy** | What rule would we trade? | **Deferred** — consumes test reports |

Tests declare which collector archive they read. Strategies (future) consume test JSON, not raw CSVs.

---

## Collector registry (summary)

| ID | Archive | Min days | VM task |
|----|---------|----------|---------|
| `cross_venue_event_gap` | `artifacts/cross_venue_snapshots/` | 14 | `install_cross_venue_collector_task.cmd` |
| `options_horizon_surface` | `artifacts/horizon_surface_archive/` | 30 | `install_horizon_surface_collector_task.cmd` |
| `implied_distribution_ts` | `artifacts/distribution_snapshots/` | 7 | `install_distribution_collector_task.cmd` |

Full list: `config/research_pipeline_registry.json`

---

## Test registry (summary)

| ID | Reads | Min days | Report |
|----|-------|----------|--------|
| `cross_venue_scan` | cross-venue | 1 | `artifacts/cross_venue_reports/` |
| `cross_venue_backtest` | cross-venue | 14 | `artifacts/cross_venue_backtest/` |
| `cross_venue_tradeability` | cross-venue | 1 | `artifacts/cross_venue_tradeability/` |

**Backtest** adds `strategy_ready` when resolved questions have Brier scores.  
**Tradeability** adds `strategy_ready` when net gap after spread proxy > 0 on latest snapshot.

---

## Reference template — cross-venue

1. **Collect** — `collect_cross_venue_snapshot.cmd`
2. **Screen** — `run_cross_venue_scan.cmd --latest-snapshot`
3. **Test accuracy** — `run_cross_venue_backtest.cmd`
4. **Test tradeability** — `run_cross_venue_tradeability.cmd`
5. **Trade** — not wired

Program: [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)  
Ops: [`CROSS_VENUE_COLLECTOR_OPS_V1.md`](CROSS_VENUE_COLLECTOR_OPS_V1.md)

---

## Adding collector + test pair

1. Row in `config/research_pipeline_registry.json`
2. `scripts/collect_*.py` + cmd + optional VM install task
3. `scripts/run_*` test reading matching archive only
4. Tests + update this doc and module map

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-30 | v1 — registry JSON, daily runner, archive health, tradeability test, dev collector |
