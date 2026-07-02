# Factory throughput v1

**Plane:** CONTROL-PLANE · **Audience:** founder, operator agents  
**Purpose:** Answer **“Is the factory moving?”** — not just “Is the loop running?”

**Related:** [`PIPELINE_HEALTH_V1.md`](PIPELINE_HEALTH_V1.md) · [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`PPE_TRACKING_HUB_V1.md`](PPE_TRACKING_HUB_V1.md)

---

## Verdicts

| Verdict | Meaning |
|---------|---------|
| `moving` | Slices or closeouts completed in last 24h |
| `idle_ok` | `SUPPLY_LOW` or `HEALTHY_IDLE` — intentional idle |
| `stuck` | Stack up but no throughput; phase stuck; or zero output 12–24h |
| `stack_down` | Loop or watch not running on VM |

---

## Command

```bat
ppe_factory_throughput.cmd
type artifacts\control_plane\FACTORY_THROUGHPUT.json
```

Unified with pipeline (recommended):

```bat
ppe_pipeline_health.cmd
```

---

## Metrics

| Field | Source |
|-------|--------|
| `throughput_24h` / `throughput_7d` | `workflow_metrics` slices + context closeouts |
| `last_slice` | Last row in `slices.jsonl` |
| `phase` / `phase_minutes` | Autobuilder + VM phase mirror + `VM_IN_FLIGHT_SINCE.json` |
| `supply` | Operator status backlog + `PHASE_QUEUE` READY count |

---

## Phase stuck thresholds

| Phase | Alert after |
|-------|-------------|
| `BUILD_IN_FLIGHT` | 2 hours |
| `FINISH_IN_FLIGHT` | 1 hour |
| `RUN_LOCAL_PENDING` | 4 hours |
| `CLOSEOUT_PENDING` | 4 hours |

Loop host also runs `maybe_notify_stuck_in_flight` (45m) via phase mirror sync.

---

## Issue codes

| Code | Meaning |
|------|---------|
| `STACK_DOWN` | Factory off — ensure stack |
| `PHASE_STUCK` | In phase too long |
| `ZERO_THROUGHPUT_12H` | Warning — no completions 24h |
| `ZERO_THROUGHPUT_24H` | Alert — factory silent |
| `SUPPLY_STARVATION_RISK` | Queue drying up |

---

## Alerts (ntfy)

`maybe_notify_throughput_regression` fires on:

- OK → stuck / stack_down
- `ZERO_THROUGHPUT_24H` or `PHASE_STUCK` (12h dedupe)
- Wired via `ppe_pipeline_health.cmd --notify` and operator status refresh

VM watchdog sends **stack restarted** when `ensure_stack` succeeds.

---

## Fix paths

| Verdict | First action |
|---------|--------------|
| `stack_down` | VM: `VM_RESTART.cmd` or `ppe_autobuilder.cmd ensure` |
| `stuck` | `ppe_autobuilder.cmd diagnose` → `advance` |
| `idle_ok` | Charter/promote backlog if unintended |

Pipeline bookkeeping issues: [`PIPELINE_HEALTH_V1.md`](PIPELINE_HEALTH_V1.md).
