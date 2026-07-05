# Distribution stats collector — ops v1

**Plane:** CONTROL-PLANE · **Program:** [`IMPLIED_DISTRIBUTION_PROGRAM_V1.md`](IMPLIED_DISTRIBUTION_PROGRAM_V1.md)

---

## Agent load bundle

| Role | Path |
|------|------|
| Ops (this file) | this file |
| Program | [`IMPLIED_DISTRIBUTION_PROGRAM_V1.md`](IMPLIED_DISTRIBUTION_PROGRAM_V1.md) |
| Research pipeline | [`RESEARCH_PIPELINE_V1.md`](RESEARCH_PIPELINE_V1.md) |
| Resolve | `python scripts/resolve_sop.py --topic "collector ops" --json` |

---

## Purpose

Run one Deribit BTC implied-distribution stats snapshot per day so future replay
charts have durable CSV evidence.

The collector uses the same export path as the distribution stats download and
writes dated files under `artifacts/distribution_snapshots/`.

---

## Manual run

```bash
collect_distribution_stats_snapshot.cmd
# or
python scripts/collect_distribution_stats_snapshot.py
```

Output:
`artifacts/distribution_snapshots/YYYY-MM-DD/ppe_btc_distribution_stats_HHMMSSZ.csv`

Verify archive metadata:

```bash
python scripts/collect_distribution_stats_snapshot.py --archive-meta
```

`archive_meta.replay_ready` becomes `true` when `available_days >= 30`.

---

## VM daily schedule

On the Hyper-V loop host (`ppeloop`), from repo root after `git pull`:

```bash
install_distribution_stats_collector_task.cmd
```

| Item | Value |
|------|-------|
| Task name | `PPE Distribution Stats Daily` |
| Schedule | Daily `07:45` local |
| Runner | `collect_distribution_stats_snapshot.cmd` |
| Log | `artifacts/orchestrator/distribution_collector.log` |

Remove:

```bash
install_distribution_stats_collector_task.cmd --unregister
```

Remote from desktop:

```bash
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && git pull origin main && install_distribution_stats_collector_task.cmd"
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && collect_distribution_stats_snapshot.cmd"
```

---

## Retention

Retain at least `90` calendar days of CSV snapshots. The repo does not prune
`artifacts/distribution_snapshots/` automatically; only prune manually after a
fresh `--archive-meta` check confirms enough replay evidence remains.
