# Product usage telemetry v1 (Q-009)

**Plane:** PRODUCT · **Layer:** `msos-web`

Minimal MSOS web usage telemetry: append-only JSONL (`ppe_product_usage.jsonl`) for operator tracking via `ppe_product_usage.cmd` and the tracking hub.

## Events (v0)

| Event | Emitter |
|-------|---------|
| `page_view` | `ProductUsageBeacon` (pathname changes) |
| `lab_view` | `StrategyLabClientShell` (pathname + asset) |
| `review_submit` | snapshot review API after successful upsert |

## Storage

- Env: `PPE_PRODUCT_USAGE_DIR` (docker: `/data` alongside web feedback)
- Server helper: `apps/msos-web/src/lib/webProductUsage.ts`
- Client beacon: `apps/msos-web/src/lib/logProductUsage.ts`

## Operator

```bat
ppe_product_usage.cmd
ppe_product_usage.cmd --json --days 14
ppe_tracking_status.cmd --brief
```

Privacy: no secrets in JSONL; owner email only when authenticated review path fires.

## Related

- [`PPE_TRACKING_HUB_V1.md`](PPE_TRACKING_HUB_V1.md)
- Master MVP1 Q-009
