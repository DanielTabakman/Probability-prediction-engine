# PPE display cache operations v1

**Program:** [`PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md`](PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md)  
**Chapter:** `ppe_display_cache_ops_v1`

---

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `PPE_DISPLAY_CACHE_ENABLED` | `1` | Toggle WSGI TTL cache |
| `PPE_DISPLAY_CACHE_TTL_SECONDS` | `120` | Cache max-age |
| `PPE_DISPLAY_CACHE_REFRESH_SECONDS` | `90` | Scheduled warm interval (target) |

---

## Operations (target — implemented by cache ops chapter)

### Deploy warm (already in display parity)

Post-recreate hook in Deploy VPS runs `warm_display_payload_cache.py` inside `ppe_display_api`.

### Scheduled warm (this chapter)

Run warm more frequently than TTL so users rarely hit cold builds:

```bash
# Example: every 90s inside container
python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765
```

### Cache health (this chapter)

```bash
curl -s http://127.0.0.1:8765/cache-status.json
```

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| NVDA Sample after 2 min | TTL expired — verify scheduled warm |
| First load slow only | Normal cold equity; warm should help repeat loads |
| Wrong asset data | Run cache isolation audit — not a cache ops issue |
