# Cross-venue collector — ops v1

**Plane:** CONTROL-PLANE · **Program:** [`MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md`](MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md)

---

## Purpose

Run **daily Polymarket ↔ Deribit BTC gap snapshots** and a **ranked scan report** without opening CSVs by hand. Backtest scoring runs **weekly** (Monday digest pipeline) once snapshot history is deep enough.

---

## Manual run (any machine with Deribit + Polymarket network)

```bat
run_cross_venue_daily.cmd
```

Or step-by-step:

```bat
collect_cross_venue_snapshot.cmd
run_cross_venue_scan.cmd --latest-snapshot
run_cross_venue_backtest.cmd
```

| Step | Artifact |
|------|----------|
| Snapshot | `artifacts/cross_venue_snapshots/YYYY-MM-DD/*.csv` |
| Scan | `artifacts/cross_venue_reports/latest.md` + `latest.json` |
| Backtest | `artifacts/cross_venue_backtest/latest_report.md` |

Backtest needs **≥14 daily snapshots** per question; warns when history is still thin.

---

## VM daily schedule (canonical)

On **Hyper-V loop host** (`ppeloop`), from repo root after `git pull`:

```bat
install_cross_venue_collector_task.cmd
```

| Item | Value |
|------|--------|
| Task name | `PPE Cross-Venue Daily` |
| Schedule | Daily **07:15** local (45 min after horizon surface 06:30) |
| Runner | `run_cross_venue_daily.cmd` |
| Log | `artifacts/orchestrator/cross_venue_collector.log` |

Remove: `install_cross_venue_collector_task.cmd --unregister`

**Remote from desktop:**

```bat
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && git pull origin main && install_cross_venue_collector_task.cmd"
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && run_cross_venue_daily.cmd"
```

---

## Weekly backtest (Monday pipeline)

`weekly_digest_monday.cmd` runs `run_cross_venue_backtest.cmd` after the workflow radar — non-fatal when history is thin. Does not block relay chapters.

---

## Relay note

Cross-venue **relay chapters** are COMPLETE and `sideChannel: true` in the queue. This ops doc covers **headless data + screening** only — not auto-trade.
