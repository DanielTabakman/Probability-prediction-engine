# Region intent schema v1

**Product:** Options Horizon  
**As-of:** 2026-06-26  
**Status:** Contract — implement in `horizon_region_draw_v1`

---

## Purpose

A **region** is a user-drawn rectangle on the price × time chart expressing a **thesis region**: "I care if spot is in this price band by this date window."

This is **not** a limit order. It is structured intent for implied-mass comparison and expression simulation.

---

## JSON shape

```json
{
  "schema_version": 1,
  "id": "uuid",
  "asset_id": "BTC",
  "venue": "deribit",
  "created_at_utc": "2026-06-26T12:00:00Z",
  "region": {
    "time_start_utc": "2026-07-01T00:00:00Z",
    "time_end_utc": "2026-07-15T23:59:59Z",
    "price_min_usd": 95000,
    "price_max_usd": 110000
  },
  "bias": "bullish_in_region",
  "user_note": "optional free text",
  "linked_expiry_ts": 1752537600000,
  "computed": {
    "implied_mass_pct": 12.4,
    "method": "lognormal_reference",
    "as_of_utc": "2026-06-26T12:00:00Z"
  }
}
```

---

## Field rules

| Field | Required | Notes |
|-------|----------|-------|
| `schema_version` | yes | `1` for v1 |
| `asset_id` | yes | Registry id (v1: `BTC`) |
| `region.time_*` | yes | ISO-8601 UTC; `time_end` > `time_start` |
| `region.price_*` | yes | USD; `price_max` > `price_min` |
| `bias` | yes | `bullish_in_region` \| `bearish_in_region` \| `neutral` |
| `linked_expiry_ts` | no | Nearest options expiry ms for implied mass |
| `computed` | server | Filled by PPE on save/preview |

---

## MSOS persistence

- Save via MSOS theses / workflow API as `kind: "horizon_region"`.
- Deep-link to Strategy Lab: `?asset=BTC&expiry_ts=...&region_id=...`

---

## Copy constraints

- UI: "Thesis region," "implied mass in region," "suggested expression (simulation)."
- Never: "order," "buy," "sell," "execute."
