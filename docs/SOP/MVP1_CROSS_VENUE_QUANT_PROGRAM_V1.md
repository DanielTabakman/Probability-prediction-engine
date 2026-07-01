# MVP1 cross-venue quant program v1

**Status:** **COMPLETE** on `main` (prob panel + scan + backtest operator CLIs + VM pipeline)

---

## Agent load bundle

| Role | Path |
|------|------|
| Program (charter / ops) | this file |
| Collector ops | [`CROSS_VENUE_COLLECTOR_OPS_V1.md`](CROSS_VENUE_COLLECTOR_OPS_V1.md) |
| Research pipeline | [`RESEARCH_PIPELINE_V1.md`](RESEARCH_PIPELINE_V1.md) |
| Registry | [`config/research_pipeline_registry.json`](../../config/research_pipeline_registry.json) |
| Resolve | `python scripts/resolve_sop.py --module cross_venue_event_gap --json` |

---

## Operator commands

```bat
run_cross_venue_daily.cmd
REM or:
python scripts/collect_cross_venue_snapshot.py
python scripts/run_cross_venue_scan.py
python scripts/run_cross_venue_backtest.py
```

| Step | Artifact |
|------|----------|
| Snapshot | `artifacts/cross_venue_snapshots/` |
| Scan | `artifacts/cross_venue_reports/latest.md` |
| Backtest | `artifacts/cross_venue_backtest/latest_report.md` |

Implied lab: CSV download + **Cross-venue gap scan** expander when Polymarket + Deribit load.

Backtest needs **≥14 daily snapshots** per question before scores are meaningful.

---

## VM pipeline

Daily **07:15** on loop host: [`CROSS_VENUE_COLLECTOR_OPS_V1.md`](CROSS_VENUE_COLLECTOR_OPS_V1.md) — `install_cross_venue_collector_task.cmd`

Weekly backtest: `weekly_digest_monday.cmd` (non-fatal when history thin)

---

## Chapter status

| Chapter | Status |
|---------|--------|
| `mvp1_cross_venue_prob_panel` | COMPLETE |
| `mvp1_cross_venue_scan_v1` | COMPLETE |
| `mvp1_cross_venue_backtest_v1` | COMPLETE |

Evidence: [`MVP1_CROSS_VENUE_PROB_PANEL_EVIDENCE_STATUS.md`](MVP1_CROSS_VENUE_PROB_PANEL_EVIDENCE_STATUS.md), [`MVP1_CROSS_VENUE_SCAN_V1_EVIDENCE_STATUS.md`](MVP1_CROSS_VENUE_SCAN_V1_EVIDENCE_STATUS.md), [`MVP1_CROSS_VENUE_BACKTEST_V1_EVIDENCE_STATUS.md`](MVP1_CROSS_VENUE_BACKTEST_V1_EVIDENCE_STATUS.md)
