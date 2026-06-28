# Options Horizon surface collector — ops v1

**Plane:** CONTROL-PLANE · **Contract:** [`SURFACE_ARCHIVE_CONTRACT_V1.md`](../VISION/OPTIONS_HORIZON/SURFACE_ARCHIVE_CONTRACT_V1.md)

---

## Purpose

Run **one Deribit BTC surface snapshot per day** so replay scrubber can ship after **≥30 calendar days** of archive.

**Strategy:** collect yourself — no third-party historical backfill in v1 (cost + schema + license).

---

## Manual run (any machine with Deribit network)

```bash
collect_horizon_surface_snapshot.cmd
# or
python scripts/collect_horizon_surface_snapshot.py
```

Output: `artifacts/horizon_surface_archive/YYYY-MM-DD/horizon_surface_HHMMSSZ.json`

Verify:

```bash
python -c "from src.data.horizon_surface_archive import archive_meta, default_archive_root; print(archive_meta(default_archive_root()))"
```

---

## VM daily schedule (canonical)

On **Hyper-V loop host** (`ppeloop`), from repo root after `git pull`:

```bash
setup_vm_hands_off.cmd
```

Or install collector only:

```bash
install_horizon_surface_collector_task.cmd
```

`setup_vm_hands_off.cmd` is idempotent — registers logon stack, watchdog, daily collector, ensures stack is running, and seeds one archive snapshot.

| Item | Value |
|------|--------|
| Task name | `PPE Horizon Surface Collector` |
| Schedule | Daily **06:30** local |
| Runner | `collect_horizon_surface_snapshot.cmd` |
| Log | `artifacts/orchestrator/horizon_surface_collector.log` |

Remove: `install_horizon_surface_collector_task.cmd --unregister`

**Remote from desktop:**

```bash
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && git pull origin main && install_horizon_surface_collector_task.cmd"
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && collect_horizon_surface_snapshot.cmd"
```

---

## Replay gate

`archive_meta.replay_ready` becomes `true` when `available_days >= 30`. Until then, charter **`horizon_replay_scrubber_v1`** stays deferred.

---

## Third-party historical options (why not v1)

| Factor | Archive-first | Vendor backfill |
|--------|---------------|-----------------|
| Cost | Deribit public marks only | Paid (often **$500–5k+/mo** depending on vendor/resolution) |
| Schema | Own JSON contract | Mapping + license review |
| Charter | Explicit non-goal | Needs new SELECTION |

Revisit vendor backfill only if validation requires **years** of replay on day one.
