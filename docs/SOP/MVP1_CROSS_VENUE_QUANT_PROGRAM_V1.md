# MVP1 cross-venue quant program v1

**Status:** **COMPLETE** — prob panel + scan + backtest operator CLIs on `feat/mvp1-cross-venue-operator-clis`.

## Operator commands

```bat
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
