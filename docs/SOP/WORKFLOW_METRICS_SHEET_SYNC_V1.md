# Workflow metrics sheet sync v1

**Plane:** CONTROL-PLANE · **Layer:** `dev-factory`

Ritual for syncing JSONL workflow metrics exports into the operator Google Sheet companion (advisory; ledger remains JSONL under `artifacts/workflow_metrics/`).

## When

- Weekly digest prep (Monday) or after a heavy factory week
- After `workflow_metrics.cmd export-csv`

## Steps

1. `workflow_metrics.cmd export-csv` — writes `sessions_export.csv`, `weekly_summary.csv`, `events_export.csv`, `context_windows_export.csv`
2. Import each CSV into the matching sheet tab (Sessions, Slices, Events, Context closeouts)
3. Do not edit JSONL directly from the sheet; re-export if corrections are needed

## Related

- [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md)
- [`PPE_TRACKING_HUB_V1.md`](PPE_TRACKING_HUB_V1.md)
