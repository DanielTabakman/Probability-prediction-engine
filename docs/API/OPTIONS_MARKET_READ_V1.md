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

`effective_target_date` is the explicit `target_date`, or snapshot `as_of` date + 30 calendar days.

Contracts already expired relative to snapshot `as_of` are ignored. Exact listed expiry wins. Otherwise the nearest live expiry by absolute calendar-day distance is used; equal distance prefers the later expiry. Earlier or later expiries are allowed. BTC permits a maximum gap of **14** calendar days (`max_expiry_gap_days` on the BTC registry row). Beyond that → **422** `expiry_not_close_enough`.

Success responses include `effective_target_date`, signed `expiry_offset_days` (`resolved_expiry − effective_target_date`), `expiry_resolution` (`exact` / `nearest_before` / `nearest_after`), and `max_expiry_gap_days`. A target before the snapshot `as_of` date → **422** `past_target_date`.

Non-exact answers prepend a deterministic sentence naming the target, the chosen expiry, and the absolute day offset. That sentence does not imply bullish or bearish.

## Metrics

Reuse prepared lognormal export fields: spot, implied forward, ATM IV, q25 / median / q75.

- `middle_50_low` = q25, `middle_50_high` = q75, `width` = q75 − q25  
- `median_vs_spot_percent` = ((median / spot) − 1) × 100  
- `atm_iv_percent` = annual ATM IV × 100  

Public JSON rounds **after** those calculations. PPE math and `display.json` stay full precision. The human-readable `answer` still uses whole-unit prices, 1-decimal percents, and 1-decimal ATM IV.

| Public field | Precision |
|---|---|
| `spot_price`, `implied_forward_price`, `median_terminal_price`, `middle_50_range.low_price`, `middle_50_range.high_price` | 2 decimal places |
| `middle_50_range.width` | 2 decimal places; equals rounded high minus rounded low |
| `atm_iv_percent` | 2 decimal places |
| `median_vs_spot_percent` | 4 decimal places |

NaN and Infinity are rejected (**503**), never serialized.

This is risk-neutral options pricing, not a forecast. The `answer` string is a fixed template — no LLM, no bullish/bearish label.

## Data

Same producer as `GET /ppe-display-api/display.json`: `_load_export_rows` → `build_distribution_export_rows` → in-process TTL cache (`build_cached_live_distribution_display_payload`). Options Market Read maps that payload; it does not keep a second CSV archive.

`as_of` is the display payload’s `as_of_utc` (cache build time). Missing or inconsistent identity, currency, expiry, spot, forward, IV, or quartiles → **503**. BTC request with SOL (or other) snapshot data → **503**.

`PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH` is a **test override** only (fixture or a saved display.json). Production compose must not set it.

Future assets: add a row to the small registry in `src/viz/options_market_read_assets.py`. The public schema stays asset-neutral.

## Local usage

```bash
python -m src.viz.display_payload_server
curl "http://127.0.0.1:8765/display.json?asset=BTC"
curl "http://127.0.0.1:8765/v1/options-market-read"
curl "http://127.0.0.1:8765/v1/options-market-read?asset=BTC&target_date=2026-12-25"
```

Tests may set `PPE_OPTIONS_MARKET_READ_SNAPSHOT_PATH` to a fixture. Production Caddy exposes the exact path `GET /v1/options-market-read` (query preserved, no `/v1/*` wildcard).
