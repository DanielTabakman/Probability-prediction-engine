# PPE tracking hub v1

**Plane:** CONTROL-PLANE · **Layer:** `dev-factory`

Unified tracking for factory throughput, validation sessions, steering drift, asset enablement, and trader outcome loops. Advisory only — pairs with `OPERATOR_STATUS`, workflow radar, and weekly digest.

**Related:** [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md) · [`PPE_COST_ACCOUNTING_V1.md`](PPE_COST_ACCOUNTING_V1.md) · [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md)

---

## What we track

| Signal | Source | Auto? |
|--------|--------|-------|
| Slice closes + worker lanes | `artifacts/workflow_metrics/slices.jsonl` | Yes — relay closeout, IDE ready |
| Context closeouts | `context_windows.jsonl` | Yes — context window closeout |
| Tracking events | `events.jsonl` | Yes — witnesses, validation, closeout |
| Validation sessions | `artifacts/validation/demo_sessions.jsonl` | On `log_demo_session.cmd` |
| Steering drift | direction JSON vs manifest | On `ppe_tracking_status.cmd` |
| Asset enablement | `config/assets.yaml` | On status / radar |
| Trader outcomes | SQLite frozen store | On status (when DB exists) |
| Product usage (MSOS) | `ppe_product_usage.jsonl` | On `ppe_product_usage.cmd` / status |
| Cursor billing reconcile | manual JSON + workflow cost | On `ppe_token_reconcile.cmd` |
| Incident slices | `incident_flag` on slice rows | Auto when roundtrips ≥3 or rework >0 |

---

## Commands

```bat
ppe_tracking_status.cmd
ppe_tracking_status.cmd --brief
ppe_tracking_status.cmd --json --days 14
workflow_metrics.cmd summary --days 7 --by-lane --include-validation
```

**Artifacts (gitignored):**

- `artifacts/control_plane/TRACKING_STATUS_LATEST.json`
- `artifacts/control_plane/TRACKING_STATUS_LATEST.md`
- `artifacts/workflow_metrics/events.jsonl`

---

## Emitters (wired)

| Hook | Event type |
|------|------------|
| `log_demo_session.py` | `validation_session` |
| `witness_asset_catalog.py` | `asset_witness` |
| `ppe_context_window_closeout.py` | `context_closeout` |
| `ppe_operator_status.py` | Surfaces tracking lines in `OPERATOR_STATUS.md` |
| `ppe_workflow_radar.py` | Weekly friction from steering / assets / trader backlog |
| `ppe_product_usage.cmd` | MSOS usage JSONL summary for tracking hub |
| `ppe_token_reconcile.cmd` | Monthly Cursor USD vs advisory ledger |

---

## Not in v1 (parked)

- Google Sheets workflow metrics ledger — optional manual companion to JSONL (see [`WORKFLOW_METRICS_SHEET_SYNC_V1.md`](WORKFLOW_METRICS_SHEET_SYNC_V1.md))

---

## Implementation

- [`scripts/ppe_tracking_hub.py`](../../scripts/ppe_tracking_hub.py)
- [`scripts/ppe_tracking_status.py`](../../scripts/ppe_tracking_status.py)
- [`scripts/workflow_metrics_cli.py`](../../scripts/workflow_metrics_cli.py) — `events.jsonl`, enriched slice rows
