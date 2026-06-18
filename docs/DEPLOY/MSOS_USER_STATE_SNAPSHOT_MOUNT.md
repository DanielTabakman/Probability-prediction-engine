# MSOS user state v1 — read-only PPE snapshot mount

**Slice:** `MSOS-UserStateV1-Platform-Slice003`  
**Service:** `msos_web` in [`docker-compose.yml`](../../docker-compose.yml)

## Intent

Command Center reads frozen evaluations from the same SQLite file `app_full` writes when `PPE_ENABLE_SNAPSHOTS=1`. The Next.js API route uses `PPE_SNAPSHOT_DB_PATH` (see [`commandCenterSummary.ts`](../../apps/msos-web/src/lib/commandCenterSummary.ts)).

## Compose wiring

| Mount | Mode | Path in container |
|-------|------|-------------------|
| `ppe_snapshots` volume | read-only | `/ppe-snapshots` |

Environment on `msos_web`:

```text
PPE_SNAPSHOT_DB_PATH=/ppe-snapshots/ppe_frozen_evaluations.sqlite3
```

This shares the named volume `ppe_snapshots` with `app_full` (`PPE_SNAPSHOT_DB_PATH=/data/ppe_frozen_evaluations.sqlite3` on the Streamlit service). `msos_web` never writes to the snapshot DB.

## VPS verify

After `docker compose up -d --build msos_web app_full`:

1. Freeze at least one evaluation in Strategy Lab (`app_full`).
2. Open `https://marketstructureos.com/command-center` — KPI row shows live snapshot counts (not degraded).
3. Panel subhead reads **From PPE snapshots**.

Record deploy witness in [`docs/SOP/VALIDATION_DEPLOY_WITNESS.md`](../SOP/VALIDATION_DEPLOY_WITNESS.md) when steward confirms.
