# Surface archive contract v1

**Product:** Options Horizon  
**As-of:** 2026-06-26  
**Implement:** `horizon_surface_archive_v1`

---

## Purpose

Time-indexed **options surface snapshots** for BTC (Deribit) enabling:

1. Future replay scrubber in Options Horizon
2. Chart payload `as_of` queries
3. PPE research / cross-venue backtest consumers

**Strategy:** archive-first from deploy date; no third-party historical backfill in v1.

---

## Storage layout

```
artifacts/horizon_surface_archive/
  YYYY-MM-DD/
    horizon_surface_{HHMMSS}Z.json
```

Default root overridable via `--snapshot-root`.

---

## Snapshot JSON (top level)

```json
{
  "schema_version": 1,
  "as_of_utc": "2026-06-26T14:30:00Z",
  "asset_id": "BTC",
  "venue": "deribit",
  "spot_usd": 105000.0,
  "expiries": [ ... ]
}
```

---

## Per-expiry row

```json
{
  "expiry_ts": 1752537600000,
  "expiry_date": "2026-07-15",
  "forward_usd": 105200.0,
  "atm_iv_annual": 0.52,
  "T_years": 0.16,
  "call_ladder": [
    { "strike": 100000, "mark_usd": 6200.0, "mark_iv": 0.51 }
  ],
  "reference_lognormal": {
    "pdf_checksum_sha256": "…",
    "grid_points": 80
  }
}
```

| Field | Notes |
|-------|-------|
| `call_ladder` | Up to 24 strikes nearest ATM with mark prices |
| `reference_lognormal` | Checksum of normalized PDF for drift detection |
| `mark_usd` | `mark_btc * spot` at collection time |

---

## Query API

`GET /ppe-display-api/horizon/surface.json`

| Param | Required | Notes |
|-------|----------|-------|
| `asset` | no | Default `BTC` |
| `as_of` | no | ISO date or datetime; nearest snapshot ≤ as_of |
| `latest` | no | `1` for most recent |

Response wraps snapshot + `archive_meta`:

```json
{
  "snapshot": { ... },
  "archive_meta": {
    "available_days": 5,
    "earliest_utc": "2026-06-22T00:00:00Z",
    "latest_utc": "2026-06-26T14:30:00Z",
    "replay_ready": false,
    "replay_threshold_days": 30
  }
}
```

---

## Collector

```bash
python scripts/collect_horizon_surface_snapshot.py
python scripts/collect_horizon_surface_snapshot.py --snapshot-root /path/to/archive
```

Cron-friendly; idempotent (multiple runs per day append timestamped files).

---

## Replay gate

`replay_ready: true` when `available_days >= 30` (calendar days with ≥1 snapshot).
