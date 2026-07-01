# PPE tracking hub v1

**Plane:** CONTROL-PLANE · **Layer:** `dev-factory`

Unified tracking for factory throughput, validation sessions, steering drift, asset enablement, and trader outcome loops. Advisory only — pairs with `OPERATOR_STATUS`, workflow radar, and weekly digest.

**Related:** [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md) · [`PPE_COST_ACCOUNTING_V1.md`](PPE_COST_ACCOUNTING_V1.md) · [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md) · [`PRODUCT_USAGE_TELEMETRY_V1.md`](PRODUCT_USAGE_TELEMETRY_V1.md)

---

## What we track

| Signal | Source | Auto? |
|--------|--------|-------|
| Slice closes + worker lanes | `artifacts/workflow_metrics/slices.jsonl` | Yes — relay closeout, IDE ready |
| Thread pulses (cognitive load) | `sessions.jsonl` (`thread_pulse`) | Optional — closeout or `workflow_metrics pulse` |
| Context closeouts | `context_windows.jsonl` | Yes — context window closeout |
| Tracking events | `events.jsonl` | Yes — witnesses, validation, closeout |
| Validation sessions | `artifacts/validation/demo_sessions.jsonl` | On `log_demo_session.cmd` |
| Steering drift | direction JSON vs manifest | On `ppe_tracking_status.cmd` |
| Asset enablement | `config/assets.yaml` | On status / radar |
| Trader outcomes | SQLite frozen store | On status (when DB exists) |
| Product usage (MSOS + Streamlit) | `ppe_product_usage.jsonl` | Beacons, lab view, export clicks |
| Cursor billing reconcile | manual JSON + workflow cost | On `ppe_token_reconcile.cmd` |
| Incident slices | `incident_flag` on slice rows | Auto when roundtrips ≥3 or rework >0 |
| Zero-activity post-deploy | `data/last_vps_deploy.utc` + usage JSONL | Watch when deploy &lt;14d and events=0 |

---

## Commands

```bat
ppe_tracking_status.cmd
ppe_tracking_status.cmd --brief
ppe_tracking_status.cmd --json --days 14
ppe_tracking_rollup.cmd
workflow_metrics.cmd aggregate --days 7
workflow_metrics.cmd pulse
workflow_metrics.cmd summary --days 7 --by-lane --include-validation
python scripts/ppe_jsonl_retention.py --apply
python scripts/ppe_feedback_steward_hook.py
python scripts/msos_product_usage_telemetry_witness.py
```

**Artifacts (gitignored):**

- `artifacts/control_plane/TRACKING_STATUS_LATEST.json`
- `artifacts/control_plane/TRACKING_STATUS_LATEST.md`
- `artifacts/control_plane/TRACKING_ROLLUP.html` — **in-house rollup** (replaces Google Sheets ritual)
- `artifacts/workflow_metrics/events.jsonl`
- `artifacts/health/msos_product_usage_telemetry_witness.json`

---

## In-house rollup (v4)

External spreadsheet sync is optional and skipped by default. Instead:

1. Run `ppe_tracking_rollup.cmd` (or `ppe_tracking_status.cmd`).
2. Open `artifacts/control_plane/TRACKING_ROLLUP.html` in a browser — summary table + event breakdown + raw JSON snapshot.

Monday digest runs JSONL retention and the feedback steward hook automatically.

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
| `product_usage_telemetry.py` | `streamlit_lab_view`, `streamlit_distribution_export` |
| `vps_post_deploy_telemetry.sh` | Deploy marker + pull + retention on VPS |

---

## Parked / lower priority

- Google Sheets workflow metrics ledger — optional manual companion (see [`WORKFLOW_METRICS_SHEET_SYNC_V1.md`](WORKFLOW_METRICS_SHEET_SYNC_V1.md))
- Grafana / Cursor billing API automation

---

## Implementation

- [`scripts/ppe_tracking_hub.py`](../../scripts/ppe_tracking_hub.py)
- [`scripts/ppe_tracking_status.py`](../../scripts/ppe_tracking_status.py)
- [`scripts/workflow_metrics_cli.py`](../../scripts/workflow_metrics_cli.py) — `events.jsonl`, enriched slice rows
