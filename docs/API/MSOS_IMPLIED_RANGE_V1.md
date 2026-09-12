# MSOS Market-Implied BTC Range API v1

**Product:** answer “What BTC price range is the options market implying by a requested date?”  
**Method / path:** `GET /v1/implied-range`  
**Host:** the existing stdlib WSGI display server (`src/viz/display_payload_server.py`).  
**OpenAPI:** [`implied-range.openapi.yaml`](implied-range.openapi.yaml)

This route does **not** change `/ppe-display-api/*`.

## Query

| Parameter | Required | Rules |
|-----------|----------|--------|
| `asset` | yes | Case-insensitive. V1 accepts **BTC** only. |
| `target_date` | yes | ISO date `YYYY-MM-DD`. |

Do not send forward, volatility, `T`, or custom bounds.

## Expiry resolution

1. Use the exact listed options expiry when it matches `target_date`.
2. Otherwise use the first expiry **on or after** `target_date`.
3. Never resolve to an earlier expiry.
4. Response always includes `requested_target_date` and `resolved_expiry`.
5. No expiry on or after the request → **422**.

A `target_date` before the snapshot `as_of` calendar date is a past date → **422**. “Now” is the snapshot timestamp, not the server clock.

## Statistics

V1 is the options-implied **interquartile range** (q25–q75) from the existing **lognormal** export (`lognormal_distribution_stats` / `lognormal_reference` rows).

- `low_usd` = q25, `median_usd` = q50, `high_usd` = q75  
- `width_usd` = q75 − q25  
- Breeden–Litzenberger results are not exposed.

## Data

Uses a **prepared** PPE distribution snapshot (latest `artifacts/distribution_snapshots/**/ppe_btc_distribution_stats_*.csv`, or `PPE_IMPLIED_RANGE_SNAPSHOT_PATH` for a JSON/CSV fixture). No live market fetch on this route.

- `data_status` is always `"cached"` on success.  
- `as_of` is snapshot metadata, normalized to UTC `Z`.  
- Missing/inconsistent `as_of`, BTC identity, expiry, or quartiles → **503**.  
- BTC/SOL (or any non-BTC) snapshot identity → **503**.

## Success

```json
{
  "schema_version": "1.0",
  "asset": "BTC",
  "currency": "USD",
  "requested_target_date": "2026-12-25",
  "resolved_expiry": "2026-12-25",
  "as_of": "2026-06-06T12:00:00Z",
  "distribution_method": "lognormal_iqr",
  "implied_range": {
    "low_usd": 65000.0,
    "median_usd": 85000.0,
    "high_usd": 105000.0,
    "width_usd": 40000.0,
    "percentile_low": 25,
    "percentile_high": 75
  },
  "data_status": "cached"
}
```

## Errors

```json
{
  "error": {
    "code": "unsupported_asset",
    "message": "V1 supports BTC only.",
    "details": { "asset": "ETH" }
  }
}
```

| Status | When |
|--------|------|
| 400 | Missing `asset` / `target_date`, or malformed date |
| 422 | Unsupported asset, past `target_date`, or no later expiry |
| 503 | No valid snapshot / inconsistent metadata or quartiles |
| 500 | Unexpected internal error |

## Local usage

```bash
set PPE_IMPLIED_RANGE_SNAPSHOT_PATH=fixtures/implied_range/btc_cached_snapshot.json
python -m src.viz.display_payload_server
curl "http://127.0.0.1:8765/v1/implied-range?asset=BTC&target_date=2026-12-25"
```

Production publish still needs a reverse-proxy path for `/v1/*` (today Caddy only maps `/ppe-display-api/*`). This slice does not deploy that mapping.
