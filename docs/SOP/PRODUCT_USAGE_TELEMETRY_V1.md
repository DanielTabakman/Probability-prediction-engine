# Product usage telemetry v1 (Q-009)

**Plane:** PRODUCT · **Layer:** `msos-web`

Minimal MSOS web usage telemetry: append-only JSONL (`ppe_product_usage.jsonl`) for operator tracking via `ppe_product_usage.cmd` and the tracking hub.

## Events (v0)

| Event | Emitter |
|-------|---------|
| `page_view` | `ProductUsageBeacon` (pathname changes) |
| `session_start` | `ProductUsageBeacon` (once per browser session) |
| `distribution_export_click` | Strategy Lab CSV download link (client intent) |
| `lab_view` | `StrategyLabClientShell` (pathname + asset) |
| `review_submit` | snapshot review API after successful upsert |
| `distribution_export` | distribution export API after successful CSV fetch |
| `feedback_submit` | feedback API after successful append |
| `streamlit_lab_view` | Streamlit implied lab (once per session) |
| `streamlit_distribution_export` | Streamlit CSV download button click |

## Storage

- Env (web): `PPE_PRODUCT_USAGE_DIR` (docker: `/data` alongside web feedback)
- Env (Streamlit): `PPE_PRODUCT_USAGE_DIR=/telemetry` with shared `msos_web_data` volume
- Server helper: `apps/msos-web/src/lib/webProductUsage.ts`
- Client beacon: `apps/msos-web/src/lib/logProductUsage.ts`
- Streamlit helper: `src/viz/product_usage_telemetry.py`

## Operator

```bat
ppe_product_usage.cmd
ppe_product_usage.cmd --json --days 14
ppe_pull_product_usage.cmd
ppe_tracking_status.cmd --brief
ppe_tracking_rollup.cmd
```

On VPS (after deploy — automatic via `deploy-vps.yml`):

```bash
bash scripts/vps_post_deploy_telemetry.sh
python scripts/ppe_product_usage.py --pull-from-docker msos_web
export PPE_PRODUCT_USAGE_JSONL=$PWD/data/ppe_product_usage.jsonl
python scripts/msos_product_usage_telemetry_witness.py
```

Privacy: no secrets in JSONL; owner email only when authenticated review path fires.

## Related

- [`PPE_TRACKING_HUB_V1.md`](PPE_TRACKING_HUB_V1.md)
- Master MVP1 Q-009
