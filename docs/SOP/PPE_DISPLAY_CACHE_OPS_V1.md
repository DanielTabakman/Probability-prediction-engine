# PPE display cache operations v1

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**Chapter:** `ppe_display_cache_ops_v1`  
**Status:** **COMPLETE** 2026-06-28

---

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `PPE_DISPLAY_CACHE_ENABLED` | `1` | Toggle WSGI TTL cache |
| `PPE_DISPLAY_CACHE_TTL_SECONDS` | `120` | Cache max-age |
| `PPE_DISPLAY_CACHE_REFRESH_SECONDS` | `90` | Scheduled warm interval (must stay below TTL) |
| `PPE_DISPLAY_API_BASE_URL` | `http://127.0.0.1:8765` | Target for warm scripts / Windows task |

---

## Deploy warm (display parity + deploy hook)

Post-recreate hook in [`deploy-vps.yml`](../../.github/workflows/deploy-vps.yml) runs one-shot warm inside `ppe_display_api`.

---

## Scheduled warm (compose sidecar — preferred on VPS)

`docker-compose.yml` service **`ppe_display_cache_refresh`** loops:

```bash
python scripts/run_display_cache_refresh.py --loop --base-url http://ppe_display_api:8765
```

Interval from `PPE_DISPLAY_CACHE_REFRESH_SECONDS` (default **90s**, below 120s TTL).

Deploy workflow starts the sidecar with `ppe_display_api`.

---

## Scheduled warm (Windows task — fallback)

When not using the compose sidecar:

```bash
install_display_cache_refresh_task.cmd
```

Runs `run_display_cache_refresh.cmd` every **2 minutes** (Task Scheduler minimum practical cadence). Log: `artifacts/orchestrator/display_cache_refresh.log`.

Unregister: `install_display_cache_refresh_task.cmd --unregister`

---

## Cache health

```bash
curl -s http://127.0.0.1:8765/cache-status.json
```

Returns TTL, refresh interval, per-asset `last_warm_utc`, freshness, and cached depths.

One-shot warm (manual):

```bash
python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765
python scripts/run_display_cache_refresh.py --base-url http://127.0.0.1:8765
```

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| NVDA Sample after 2 min | TTL expired — verify sidecar or scheduled task running |
| First load slow only | Normal cold equity; warm should help repeat loads |
| Wrong asset data | Run cache isolation audit — not a cache ops issue |
| `cache-status.json` missing `last_warm_utc` | No warm since process start — run warm or wait for sidecar |
