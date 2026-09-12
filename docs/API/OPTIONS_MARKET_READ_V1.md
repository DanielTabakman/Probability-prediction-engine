# Options Market Read API v1

**Product:** ask “What is the options market saying?” and receive a deterministic plain-English read of what options are currently pricing.  
**Future Qatom tool:** `msos.options_market_read`  
**Method / path:** `GET /v1/options-market-read`  
**Host:** existing stdlib WSGI display server (`src/viz/display_payload_server.py`).  
**OpenAPI:** [`options-market-read.openapi.yaml`](options-market-read.openapi.yaml)

Does **not** change `/ppe-display-api/*`. Replaces the earlier `/v1/implied-range` proposal.

## Query

| Parameter | Required | Rules |
|-----------|----------|--------|
| `asset` | no | Case-insensitive. Default **BTC**. V1 enables BTC only. |
| `target_date` | no | ISO `YYYY-MM-DD`. If omitted, target is snapshot `as_of` date **+ 30 calendar days** (not the server clock). |

## Expiry resolution

Exact listed expiry if present; otherwise the first expiry on or after the target. Never an earlier expiry. `resolved_expiry` is always returned. No eligible expiry → **422**. A target before the snapshot `as_of` date → **422**.

## Metrics

Reuse prepared lognormal export fields: spot, implied forward, ATM IV, q25 / median / q75.

- `middle_50_low` = q25, `middle_50_high` = q75, `width` = q75 − q25  
- `median_vs_spot_percent` = ((median / spot) − 1) × 100  
- `atm_iv_percent` = annual ATM IV × 100  

This is risk-neutral options pricing, not a forecast. The `answer` string is a fixed template — no LLM, no bullish/bearish label.

## Data

Prepared PPE snapshot only (`artifacts/distribution_snapshots/**/ppe_btc_distribution_stats_*.csv` or `PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH`). No live fetch. `as_of` is snapshot metadata. Missing or inconsistent identity, currency, expiry, spot, forward, IV, or quartiles → **503**. BTC request with SOL (or other) snapshot data → **503**.

Future assets: add a row to the small registry in `src/viz/options_market_read_assets.py`. The public schema stays asset-neutral.

## Local usage

```bash
set PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH=fixtures/options_market_read/btc_cached_snapshot.json
python -m src.viz.display_payload_server
curl "http://127.0.0.1:8765/v1/options-market-read"
curl "http://127.0.0.1:8765/v1/options-market-read?asset=BTC&target_date=2026-12-25"
```

Production still needs a reverse-proxy path for `/v1/*` (Caddy today maps `/ppe-display-api/*` only). This slice does not deploy that mapping.
