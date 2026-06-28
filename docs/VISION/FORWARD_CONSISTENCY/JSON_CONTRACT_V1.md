# Forward consistency JSON contract v1

**Kind:** `forward_consistency_boundary`  
**HTTP:** `GET /ppe-display-api/forward-consistency.json`  
**Query:** `asset` (catalog id), `expiry` (Strategy Lab expiry string or `YYYY-MM-DD` prefix)

---

## Response (success)

```json
{
  "schema_version": 1,
  "kind": "forward_consistency_boundary",
  "asset_id": "BTC",
  "expiry_date": "2026-09-26",
  "as_of_utc": "2026-06-28T12:00:00+00:00",
  "research_only": true,
  "comparable": true,
  "venue": "deribit",
  "spot_usd": 98500.0,
  "forward_usd": 99100.0,
  "status": "NO_ARB",
  "direction": null,
  "best_strike": 99000.0,
  "synthetic_bid": 98950.0,
  "synthetic_ask": 99180.0,
  "synthetic_width_usd": 230.0,
  "future_bid": 99080.0,
  "future_ask": 99150.0,
  "future_instrument": "BTC-26SEP26",
  "gross_edge_usd": -30.0,
  "estimated_cost_usd": 45.0,
  "net_edge_usd": -75.0,
  "legs": [],
  "detail": "",
  "copy_note": "Spot vs future distribution is not arbitrage. ..."
}
```

---

## Status enum

| Value | UI badge |
|-------|----------|
| `NO_ARB` | No arb |
| `WATCH` | Watch |
| `POSSIBLE_ARB` | Possible arb |
| `BAD_DATA` | Bad data |
| `NOT_COMPARABLE` | Not comparable |

`direction` when `POSSIBLE_ARB`: `SELL_FUTURE_BUY_SYNTHETIC` | `BUY_FUTURE_SELL_SYNTHETIC`.

`legs` populated only when `status === POSSIBLE_ARB`.

---

## Error kind

`kind: forward_consistency_error` — missing `expiry` query param or upstream fetch failure.

---

## Layer rule

All parity math in Python (`src/engine/forward_consistency.py`). MSOS displays/proxies only.
